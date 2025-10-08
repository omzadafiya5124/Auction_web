from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    
    path('validate-step1/', views.validate_step1, name='validate_step1'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('set-password/', views.set_password, name='set_password'), # New URL
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('add_product/', views.add_product, name='add_product'),
    #admin dashbord
    path('dashboard-admin/', views.dashboardAdmin, name='dashboard-admin'),


    # Other Page URLs
    path('about/', views.about, name="about"),
    path('auction/', views.auction, name="auction"),
    path('auction-details/<int:pk>/', views.auc_details, name="auction-details"),
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
    path('dashboard/',views.dash_board, name="dashboard"),
    path('edit-profile/',views.edit_profile_view, name="edit_profile_view"),
    #For Edit profile
    path('edit-profile/edit/', views.edit_profile, name='edit_profile'),
        #For contect Form
    path('submit-contact/', views.contact_view, name='submit_contact_form'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.user_wishlist_products, name='user_wishlist'),
]
