from django import forms
from .models import JobSeekerProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['first_name', 'last_name','headline', 'skills', 'education', 'work_experience', 'links', 'is_public']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'links': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_public': 'Make my profile visible to others', 
        }
