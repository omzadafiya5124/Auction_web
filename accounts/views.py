import json
import random, sys
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import base64
from django.core.paginator import Paginator

#For Admin
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from .forms import ProductForm,ReviewForm
from .models import Product


#For edit profile
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash

from .forms import RegistrationForm, EmailAuthenticationForm, PasswordResetRequestForm, SetNewPasswordForm, UserProfileEditForm, CustomPasswordChangeForm,ContactForm

User = get_user_model()

# --- OTHER PAGE VIEWS (Placeholders) ---

def home(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
def auction(request):
    products = Product.objects.all()  
    return render(request, "auction.html", {'products': products})

@login_required
def auc_details(request,pk): 
    product = get_object_or_404(Product, pk=pk)
     # Get all reviews for this product, ordered by the newest first
    reviews = product.reviews.all().order_by('-created_at')
    review_count = reviews.count()
    if request.user.is_authenticated:
        initial_data = {
            'name': request.user.username,
            'email': request.user.email,
        }
        review_form = ReviewForm(initial=initial_data)


    if request.method == 'POST':
        # If the form is submitted, process the data
        form_data = ReviewForm(request.POST)
        if form_data.is_valid():
            # Create a new review object but don't save it to the database yet
            new_review = form_data.save(commit=False)
            # Associate the review with the current product
            new_review.product = product
            # Save the new review to the database
            new_review.save()
            # Redirect to the same page to show the new review and clear the form
            return redirect('auction-details', pk=pk)
        else:
            # If the form is invalid, re-render the page with the submitted data and errors
            review_form = form_data

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'review_count': review_count,
    }
    return render(request, 'auction-details.html', context)

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
#For Edit profile
def edit_profile_view(request):
    form = UserProfileEditForm() 
    return render(request,"dashboard-edit-profile.html",{'form':form})


#For contect Form
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Thank you! Your message has been submitted successfully.')
            return redirect('contact') 
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

#For Edit profile
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('edit_profile_view')
    else:
        form = UserProfileEditForm(instance=request.user)

    return render(request, 'dashboard-edit-profile.html', {'form': form})
    
@login_required
def dashboardAdmin(request):

    current_user = request.user

    attended_auctions_count = 290 

    won_auctions_count = 50 

    canceled_auctions_count = 25 

    from collections import namedtuple
    Auction = namedtuple('Auction', ['id', 'product_name'])
    Bid = namedtuple('Bid', ['auction', 'amount', 'status', 'created_at'])
    import datetime
    all_bids = [
        Bid(Auction(12584885455, 'Porcelain'), 1800, 'Winning', datetime.date(2024, 6, 25)),
        Bid(Auction(12584885482, 'Old Clocks'), 1900, 'Winning', datetime.date(2024, 6, 13)),
        Bid(Auction(12584885536, 'Manuscripts'), 2000, 'Cancel', datetime.date(2024, 6, 2)),
        Bid(Auction(12584885548, 'Renaissance Art'), 2100, 'Winning', datetime.date(2024, 6, 8)),
        Bid(Auction(12584885563, 'Impressionism Art'), 2200, 'Winning', datetime.date(2024, 6, 21)),
        Bid(Auction(12584885589, 'Romanticism Art'), 2300, 'Cancel', datetime.date(2024, 6, 9)),
    ]

    paginator = Paginator(all_bids, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'attended_auctions_count': attended_auctions_count,
        'won_auctions_count': won_auctions_count,
        'canceled_auctions_count': canceled_auctions_count,
        'page_obj': page_obj, # Pass the paginated object
    }
    
    return render(request, 'Admin/dashbord_admin.html', context)

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
            if user.email.lower() == 'sujalzadafiya330@gmail.com':
                login(request, user)
                return redirect('dashboard-admin')  
            else:
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


def add_product(request):
    if request.method == 'POST':
        
        form = ProductForm(request.POST, request.FILES)
        gallery_files = request.FILES.getlist('gallery_images_upload')

        if form.is_valid():
            product_instance = form.save(commit=False)

            
            product_instance.save()

            gallery_paths = []
            for file in gallery_files[:5]:  # limit to 5
                saved_path = default_storage.save(f"products/gallery/{file.name}", file)
                gallery_paths.append(saved_path)

           
            product_instance.gallery_images = gallery_paths
            product_instance.save(update_fields=['gallery_images'])

            return redirect('auction')
        else:
            print("Form Errors:", form.errors)
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})
