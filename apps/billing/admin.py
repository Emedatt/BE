from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'amount', 'status', 'transaction_reference', 'paid_at')
    list_filter = ('status', 'paid_at')
    search_fields = ('transaction_reference', 'appointment__patient__username')

