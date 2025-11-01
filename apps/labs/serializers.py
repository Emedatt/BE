from rest_framework import serializers
from .models import LabTestBooking

class LabTestBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestBooking
        fields = '__all__'
