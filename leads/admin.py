from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'date_created')
    list_filter = ('date_created',)
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_created',)
    readonly_fields = ('date_created',)
