from django import forms
from django.core.exceptions import ValidationError

from .models import Report
from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User


class customSignUp(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['email'].label = "Email*"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

class customLogin(LoginForm):

    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = "Username"
        self.fields['password'].label = "Password"
        self.fields['remember_me'].label = "Remember Me"


class ReportForm(forms.ModelForm):
    company_name = forms.CharField(required=True)
    reason = forms.CharField(widget=forms.Textarea, required=True)
    class Meta:
        model = Report
        fields = ['company_name', 'reason','category']


class CompleteForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="message")