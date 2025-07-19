from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
import uuid

class BaseModel(models.Model):
    """Abstract base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save()

class User(AbstractUser, BaseModel):
    """Custom user model that extends the default Django user model."""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='admin')
    address = models.TextField(blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(null=True, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        permissions = [
            ("can_view_analytics", "Can view analytics"),
            ("can_manage_users", "Can manage users"),
            ("can_approve_content", "Can approve content"),
        ]

    def __str__(self):
        full_name = super().get_full_name()
        return full_name if full_name else self.email

    def get_primary_phone(self):
        return self.phone_numbers.filter(is_primary=True).first()

    def send_verification_email(self):
        self.email_verification_token = uuid.uuid4()
        self.email_verification_sent_at = timezone.now()
        self.save()
        # Add email sending logic here

class PhoneNumber(BaseModel):
    """Model for storing multiple phone numbers per user."""
    PHONE_TYPES = (
        ('mobile', 'Mobile'),
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_numbers', db_index=True)
    number = PhoneNumberField()
    type = models.CharField(max_length=10, choices=PHONE_TYPES, default='mobile')
    is_primary = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_primary:
            PhoneNumber.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-is_primary', 'type']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_primary=True),
                name='unique_primary_phone'
            )
        ]

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

    def update_user(self):
        # This method can be extended to update user fields from profile if needed
        # For example, if you add first_name, last_name to Profile model
        # self.user.first_name = self.first_name
        # self.user.last_name = self.last_name
        # self.user.save()
        pass


class Staff(BaseModel):
    """Model representing a staff member."""
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('support', 'Support'),
        ('analyst', 'Analyst'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    # business = models.ForeignKey('business.Business', on_delete=models.CASCADE, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='support')

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Unknown User"
        return f"{user_name} - {self.role}"
    
    def save(self, *args, **kwargs):
        if self.user:
            if not self.user.is_staff:
                self.user.is_staff = True
            current_role = getattr(self.user, 'role', None)
            if current_role != 'staff':
                setattr(self.user, 'role', 'staff')
            
            # Assign role-based permissions
            if self.role == 'manager':
                self.user.user_permissions.add(
                    Permission.objects.get(codename='can_manage_users'),
                    Permission.objects.get(codename='can_approve_content')
                )
            elif self.role == 'analyst':
                self.user.user_permissions.add(
                    Permission.objects.get(codename='can_view_analytics')
                )
            
            self.user.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user:
            self.user.is_staff = False
            self.user.save()
        super().delete(*args, **kwargs)

