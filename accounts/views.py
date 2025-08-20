from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
import random
from datetime import date

from .forms import (
    RegistrationForm, EmailAuthenticationForm, PasswordResetRequestForm, SetNewPasswordForm
)

User = get_user_model()

# --- AUTHENTICATION VIEWS ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if 'date_of_birth' in cleaned_data and cleaned_data['date_of_birth']:
                cleaned_data['date_of_birth'] = cleaned_data['date_of_birth'].isoformat()
            
            request.session['registration_data'] = cleaned_data
            otp = random.randint(100000, 999999)
            request.session['registration_otp'] = otp
            email = form.cleaned_data['email']
            send_mail(
                'Verify your ProBid Account',
                f'Your OTP for registration is: {otp}',
                settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False,
            )
            messages.info(request, f'An OTP has been sent to {email}.')
            return redirect('verify_otp')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('registration_otp')
        if entered_otp and stored_otp and int(entered_otp) == stored_otp:
            reg_data = request.session.get('registration_data')
            if 'date_of_birth' in reg_data and isinstance(reg_data['date_of_birth'], str):
                reg_data['date_of_birth'] = date.fromisoformat(reg_data['date_of_birth'])
            
            form = RegistrationForm(reg_data)
            if form.is_valid():
                user = form.save()
                user.is_active = True
                user.save()
                del request.session['registration_data']
                del request.session['registration_otp']
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'verify_otp.html')

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