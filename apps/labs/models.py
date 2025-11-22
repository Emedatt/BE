from django.db import models
from django.conf import settings
from appointments.models import Appointment


class LabTestBooking(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "patient"},
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True
    )
    lab_name = models.CharField(max_length=100)
    test_type = models.CharField(max_length=100)
    result_url = models.URLField(blank=True, null=True)
    date_booked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.test_type} at {self.lab_name}"
