from django import forms
from .models import JobSeekerProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['first_name', 'last_name','headline', 'skills', 'education', 'work_experience', 'links', 'is_public',
                   "address", "city", "state", "postal_code", "country",]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'links': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP / Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            
        }
        labels = {
            'is_public': 'Make my profile visible to others', 
        }
