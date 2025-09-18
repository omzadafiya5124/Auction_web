# In accounts/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

class ProfileUpdateForm(forms.ModelForm):
    """A form for updating a user's profile information."""
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = get_user_model()
        fields = [
            'username', 'email', 'mobile_number', 
            'date_of_birth', 'image', 'gender'
        ]

class CustomPasswordChangeForm(PasswordChangeForm):
    """A styled version of Django's secure password change form."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'placeholder': '********',
                'autocomplete': 'new-password' # Helps prevent browser auto-filling
            })

class RegistrationForm(forms.ModelForm):
    # These fields are defined here to control their order and widgets
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False, min_length=8)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    # --- KEY CHANGE: Added placeholders for better UX ---
    # gender = forms.ChoiceField(choices=[('', 'Select Gender...')] + User.GENDER_CHOICES)
    # account_type = forms.ChoiceField(choices=[('', 'Select Account Type...')] + User.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'date_of_birth', 'gender', 'account_type', 'image']
        
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        # Ensure we don't validate against an existing inactive user during their own registration
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("An active account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # The password is now set in the view, so we just call the parent save method
        user = super().save(commit=commit)
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