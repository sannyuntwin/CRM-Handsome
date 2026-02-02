from django import forms
from django.contrib.auth.models import User
from .models import Lead, UserProfile

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone', 'description', 'status', 'assigned_to']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                user_profile = user.userprofile
                if user_profile.role == 'sales_rep':
                    self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)
                    self.fields['assigned_to'].initial = user
                    self.fields['assigned_to'].widget = forms.HiddenInput()
                elif user_profile.role in ['admin', 'manager']:
                    self.fields['assigned_to'].queryset = User.objects.filter(userprofile__role='sales_rep')
            except UserProfile.DoesNotExist:
                self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)
                self.fields['assigned_to'].initial = user
                self.fields['assigned_to'].widget = forms.HiddenInput()
        else:
            self.fields['assigned_to'].queryset = User.objects.none()
