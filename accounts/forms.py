# In accounts/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .models import Product,Review,ContactSubmission

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'phone', 'email', 'message']


#edit pro
class UserProfileEditForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    image = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = User
        # --- KEY CHANGE: Remove 'account_type' from this list ---
        fields = [
            'username', 'email', 'mobile_number',
            'date_of_birth', 'gender', 'image'  # 'account_type' has been removed
        ]

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    # Your clean_username and clean_email methods remain unchanged
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

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
    
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    
class ProductForm(forms.ModelForm):
    # This field is for the upload widget. It is NOT saved to the database.
    # We will process the files from this field manually in the view.
    gallery_images_upload = forms.FileField(
        widget=MultipleFileInput(),  # <-- Use the custom widget here
        required=False,
        label="Gallery Images (Optional, up to 5)"
    )

    class Meta:
        model = Product
        # Note: The 'gallery_images' JSONField is NOT included here.
        # We only include the fields that Django can handle automatically.
        fields = [
            'product_name', 'product_description', 'start_price',
            'auction_start_date_time', 'auction_end_date_time',
            'category', 'main_image',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'product_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'start_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'auction_start_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'auction_end_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'message', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message...'}),
            'rating': forms.HiddenInput(),  # The rating will be set via JavaScript
        }