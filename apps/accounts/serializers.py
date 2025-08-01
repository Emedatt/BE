from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from datetime import timedelta
from django.core.exceptions import ValidationError
import uuid

from .models import User, PatientProfile, DoctorProfile, EmailVerificationToken, PasswordResetToken
from .utils.security import log_audit
from .utils.notifications import send_verification_email, send_password_reset_email

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_email_verified']
        read_only_fields = ['id', 'is_email_verified']

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = ['user', 'date_of_birth', 'gender', 'phone_number', 'address', 'medical_history']

    def validate_medical_history(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Medical history must be a valid JSON object")
        return value

class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['user', 'license_number', 'specialty', 'years_experience', 'hospital_affiliation', 'phone_number']

    def validate_license_number(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("License number must be at least 5 characters")
        return value

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'role']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match"})
        if data['role'] == 'admin':
            raise serializers.ValidationError({"role": "Admin role cannot be created via this endpoint"})
        if data['role'] not in ['patient', 'doctor']:
            raise serializers.ValidationError({"role": "Invalid role"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        if user.role == 'patient':
            PatientProfile.objects.create(user=user)
        elif user.role == 'doctor':
            DoctorProfile.objects.create(user=user, license_number=f"TEMP-LIC-{uuid.uuid4().hex[:8]}", specialty='General')
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        send_verification_email(user.email, token.token)
        log_audit(user, "register", {"email": user.email, "role": user.role})
        return user

class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role']

    def validate(self, data):
        if data['role'] != 'admin':
            raise serializers.ValidationError({"role": "This endpoint is for creating admin users only"})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_email_verified = True
        user.save()
        log_audit(self.context['request'].user, "admin_create", {"new_admin_email": user.email})
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user found with this email")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match"})
        try:
            token = PasswordResetToken.objects.get(token=data['token'], expires_at__gt=timezone.now())
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or expired token"})
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Incorrect password"})
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match"})
        return data

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField()

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value
