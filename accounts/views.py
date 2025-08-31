import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
import random, sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import base64

from .forms import RegistrationForm, EmailAuthenticationForm, PasswordResetRequestForm, SetNewPasswordForm

User = get_user_model()

# This view now ONLY handles the initial page load.
def register_view(request):
    form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def validate_step1(request):
    if request.method == 'POST':
        # Check for existing inactive user with this email and clean it up first
        email = request.POST.get('email')
        User.objects.filter(email__iexact=email, is_active=False).delete()

        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            # Store image in session if it exists, converting it to base64
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                request.session['registration_image'] = {
                    'name': image_file.name,
                    'content': encoded_image,
                    'content_type': image_file.content_type,
                }
                # Remove from cleaned_data as it's handled separately
                cleaned_data.pop('image')
            
            # Convert date objects to string for session serialization
            if isinstance(cleaned_data.get('date_of_birth'), date):
                cleaned_data['date_of_birth'] = cleaned_data['date_of_birth'].isoformat()

            # Passwords are handled in step 3, so remove them from step 1 data
            cleaned_data.pop('password', None)
            cleaned_data.pop('confirm_password', None)

            request.session['registration_data'] = cleaned_data
            request.session.set_expiry(600)  # Session expires in 10 minutes

            otp = random.randint(100000, 999999)
            request.session['registration_otp'] = otp

            send_mail(
                'Verify your Account',
                f'Your OTP for registration is: {otp}',
                settings.DEFAULT_FROM_EMAIL, [cleaned_data['email']], fail_silently=False,
            )
            return JsonResponse({'success': True})
        else:
            serializable_errors = {}
            for field, error_list in form.errors.items():
                serializable_errors[field] = [str(error) for error in error_list]

            return JsonResponse({'success': False, 'errors': serializable_errors})

    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        entered_otp = data.get('otp')
        stored_otp = request.session.get('registration_otp')

        if entered_otp and stored_otp and int(entered_otp) == stored_otp:
            request.session['otp_verified'] = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': {'otp': 'Invalid OTP. Please try again.'}})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

def resend_otp(request):
    if request.method == 'POST':
        # Retrieve email from existing session data, not a pre_registered_user_id
        registration_data = request.session.get('registration_data')
        if not registration_data or not registration_data.get('email'):
            return JsonResponse({'success': False, 'message': 'Registration session data not found.'})

        user_email = registration_data['email']
        try:
            otp = random.randint(100000, 999999)
            request.session['registration_otp'] = otp
            send_mail(
                'Your New Verification Code',
                f'Your new OTP is: {otp}',
                settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': 'A new OTP has been sent.'})
        except Exception as e:
            print(f"Error resending OTP: {e}", file=sys.stderr)
            return JsonResponse({'success': False, 'message': 'Could not resend OTP due to an internal error.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def set_password(request):
    if request.method == 'POST' and request.session.get('otp_verified'):
        registration_data = request.session.get('registration_data')
        if not registration_data:
            return JsonResponse({'success': False, 'errors': {'non_field_errors': 'Session expired. Please start over.'}})

        data = json.loads(request.body)
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Basic password validation (already handled by form.is_valid() if using form)
        if not (password and confirm_password and password == confirm_password and len(password) >= 8):
            return JsonResponse({'success': False, 'errors': {'confirm_password': 'Passwords do not match or are too short (min 8 characters).'}})

        try:
            # Create user object without saving yet
            # We use **registration_data to unpack the dictionary into keyword arguments
            # Ensure date_of_birth is converted back to date object if stored as string
            if 'date_of_birth' in registration_data:
                registration_data['date_of_birth'] = date.fromisoformat(registration_data['date_of_birth'])

            user = User(**registration_data)
            user.set_password(password)
            user.is_active = True # User is active after successful registration
            user.save()

            # Handle profile image if it was uploaded
            registration_image = request.session.get('registration_image')
            if registration_image:
                image_content = base64.b64decode(registration_image['content'])
                user.image.save(
                    registration_image['name'],
                    ContentFile(image_content, name=registration_image['name'])
                )

            # Clean up all session data related to registration
            for key in list(request.session.keys()):
                if key.startswith('registration_') or key in ['registration_data', 'otp_verified', 'registration_image']:
                    del request.session[key]

            messages.success(request, 'Account created successfully! You can now log in.')
            return JsonResponse({'success': True}) # Send redirect URL
        except Exception as e:
            print(f"Error creating user: {e}", file=sys.stderr)
            return JsonResponse({'success': False, 'errors': {'non_field_errors': f'An error occurred during account creation: {e}'}})
    return JsonResponse({'success': False, 'errors': 'Invalid request or OTP not verified.'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

def password_reset_request_view(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid(): 
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                otp = random.randint(100000, 999999)
                request.session['reset_otp'] = otp
                request.session['reset_email'] = user.email
                send_mail('Password Reset Request', f'Your OTP to reset your password is: {otp}',
                         settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                messages.info(request, 'An OTP has been sent to your email.')
                return redirect('password_reset_confirm')
            except User.DoesNotExist:
                messages.error(request, 'No user is registered with this email address.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {'form': form})

def password_reset_confirm_view(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        messages.error(request, 'Session expired. Please request a new password reset.')
        return redirect('password_reset_request')
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        if entered_otp and stored_otp and int(entered_otp) == stored_otp:
            if form.is_valid():
                user = User.objects.get(email=reset_email)
                user.set_password(form.cleaned_data['password'])
                user.save()
                del request.session['reset_otp']
                del request.session['reset_email']
                messages.success(request, 'Password has been reset successfully. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'The OTP you entered is incorrect.')
    else:
        form = SetNewPasswordForm()
    return render(request, 'password_reset_confirm.html', {'form': form})



# --- OTHER PAGE VIEWS (Placeholders) ---

def home(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
def auction(request): return render(request, "auction.html")
def auc_details(request): return render(request, "auction-details.html")
def blog(request): return render(request, "blog.html")
def category(request): return render(request, "category.html")
def contact(request): return render(request, "contact.html")
def seller_list(request): return render(request, "seller_list.html")
def seller_details(request): return render(request, "seller_details.html")
def how_to_sell(request): return render(request, "how-to-sell.html")
def how_to_bid(request): return render(request, "how-to-buy.html")
def faqs(request): return render(request, "faq.html")
def error(request): return render(request, "error.html")
def privacy_policy(request): return render(request, "privacy-policy.html")
def support_center(request): return render(request, "support-center.html")
def terms_condition(request): return render(request, "terms-condition.html")
def dash_board(request): return render(request,"dashboard.html")