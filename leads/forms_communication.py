from django import forms
from .models import Communication, Lead

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['type', 'subject', 'content', 'date_time']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Communication details', 'rows': 4}),
            'date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        lead = kwargs.pop('lead', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if lead:
            self.instance.lead = lead
        
        if user:
            self.instance.created_by = user
        
        # Set default date_time to current datetime if not provided
        if not self.instance.date_time:
            from django.utils import timezone
            self.instance.date_time = timezone.now()
