from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'consultation', 'issued_at')
    search_fields = ('medicine_name', 'consultation__appointment__patient__username')

