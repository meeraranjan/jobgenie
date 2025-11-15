from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Write a message...'}),
        label=''
    )

    class Meta:
        model = Message
        fields = ['body']
