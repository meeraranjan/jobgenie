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

class CandidateSearchForm(forms.Form):
    skills = forms.CharField(
        required=False,
        label="Skills / keywords",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Python, SQL, Java"})
    )
    city = forms.CharField(
        required=False,
        label="City",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "City"})
    )
    project = forms.CharField(
        required=False,
        label="Project keyword",
        help_text="Title/description keyword",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ex: chatbot"})
    )