from django.contrib import admin
from .models import LabTestBooking

@admin.register(LabTestBooking)
class LabTestBookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'lab_name', 'test_type', 'date_booked')
    search_fields = ('patient__username', 'lab_name', 'test_type')

