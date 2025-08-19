from django.urls import path
from django.contrib.auth import views as auth_views # <-- Import Django's auth views
from . import views

urlpatterns = [
    # Your existing URLs
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # Other Page URLs
    path('about/', views.about, name="about"),
    path('auction/', views.auction, name="auction"),
    path('auction-details/', views.auc_details, name="auction-details"),
    path('blog/',views.blog, name="blog"),
    path('category/',views.category, name="category"),
    path('contact/',views.contact, name="contact"),
    path('sellers/',views.seller_list, name="seller_list"),
    path('sellers/details/',views.seller_details, name="seller_details"),
    path('how-to-sell/',views.how_to_sell, name="how-to-sell"),
    path('how-to-bid/',views.how_to_bid, name="how-to-bid"),
    path('faqs/',views.faqs, name="faqs"),
    path('error/',views.error, name="error"),
    path('privacy-policy/',views.privacy_policy, name="privacy_policy"), 
    path('support-center/',views.support_center, name="support_center"), 
    path('terms-condition/',views.terms_condition, name="terms_condition"),
]