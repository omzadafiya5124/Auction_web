# In accounts/forms.py
# FINAL AND CORRECTED

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'gender', 'date_of_birth', 'account_type']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Your Email Address")

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password