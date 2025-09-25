from django import forms
from .models import Job

class JobFilterForm(forms.Form):
    title = forms.CharField(required=False)
    skills = forms.CharField(required=False, help_text="Separate skills with comma or space")
    location = forms.CharField(required=False)
    min_salary = forms.DecimalField(required=False, min_value=0)
    max_salary = forms.DecimalField(required=False, min_value=0)
    job_type = forms.MultipleChoiceField(
        required=False, choices=Job.JOB_TYPES, widget=forms.CheckboxSelectMultiple
    )
    remote_type = forms.MultipleChoiceField(
        required=False, choices=Job.REMOTE_TYPES, widget=forms.CheckboxSelectMultiple
    )
    visa = forms.ChoiceField(
        required=False,
        choices=[('', 'Either'), ('YES', 'Sponsorship available'), ('NO', 'No sponsorship')],
    )