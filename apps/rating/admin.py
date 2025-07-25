from django.contrib import admin
from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('patient__username', 'doctor__username', 'comment')

