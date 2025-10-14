from django import forms
from .models import Job

class JobFilterForm(forms.Form):
    title = forms.CharField(required=False)
    skills = forms.CharField(required=False, help_text="Separate skills with comma or space")
    city = forms.CharField(required=False, label="City")
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
    
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "skills",
            'street', 'apartment', 'city', 'state', 'postal_code', 'country',
            "salary_min",
            "salary_max",
            "job_type",
            "visa_sponsorship",
            "company_name",
        ]
