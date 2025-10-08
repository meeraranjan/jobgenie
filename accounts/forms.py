from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from profiles.models import UserProfile
from django.contrib.auth.models import User

class CustomErrorList(ErrorList):
 def __str__(self):
    if not self:
        return ''
    return mark_safe(''.join([ f'<div class="alert alert-danger" role="alert"> {e}</div>' for e in self]))

class BootstrapRadioSelect(forms.RadioSelect):
    template_name = 'django/forms/widgets/radio.html'
    option_template_name = 'django/forms/widgets/radio_option.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        for option in context['widget']['optgroups'][0][1]:
            option['attrs']['class'] = 'form-check-input'
        return context


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
    ('JOB_SEEKER', 'Job Seeker'),
    ('RECRUITER', 'Recruiter'),
    )

    role = forms.ChoiceField(
    choices=ROLE_CHOICES,
    widget=forms.RadioSelect,
    required=True
    )
    


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)

    # Get the selected role from the form
        role = self.cleaned_data.get('role')

    # Create or update the UserProfile
        from profiles.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()

    # If recruiter, create recruiter profile
        if role == 'RECRUITER':
            from recruiters.models import Recruiter
            Recruiter.objects.get_or_create(user=user)
        return user