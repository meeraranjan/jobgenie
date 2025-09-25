from django import forms
from .models import Recruiter

class RecruiterForm(forms.ModelForm):
    class Meta:
        model = Recruiter
        fields = ['company_name', 'position']  # adjust fields as needed
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your position'
            }),
        }

