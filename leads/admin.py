from django.contrib import admin
from django.contrib.auth.models import User
from .models import Lead, UserProfile, Communication

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'assigned_to', 'date_created')
    list_filter = ('status', 'date_created', 'assigned_to')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-date_created',)
    readonly_fields = ('date_created',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_profile = request.user.userprofile
        if user_profile.role == 'sales_rep':
            return qs.filter(assigned_to=request.user)
        return qs

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('-created_at',)

@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('lead', 'type', 'subject', 'date_time', 'created_by', 'created_at')
    list_filter = ('type', 'date_time', 'created_by')
    search_fields = ('lead__first_name', 'lead__last_name', 'subject', 'content')
    ordering = ('-date_time',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        user_profile = request.user.userprofile
        if user_profile.role == 'sales_rep':
            return qs.filter(lead__assigned_to=request.user)
        return qs
