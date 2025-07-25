from django.db import models
from accounts.models import User

class Rating(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings', limit_choices_to={'role': 'doctor'})
    score = models.IntegerField() 
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → {self.doctor.username} [{self.score}]"

