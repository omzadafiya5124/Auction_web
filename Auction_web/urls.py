"""
URL configuration for Auction_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home),
    path('about/', views.about),
    path('auction/', views.auction),
    path('auction-details/', views.auc_details),
    path('blog/',views.blog),
    path('category/',views.category),
    path('contact/',views.contact),
    path('seller_list/',views.seller_list),
    path('seller_details/',views.seller_details),
    path('how-to-sell/',views.how_to_sell),
    path('how-to-bid/',views.how_to_bid),
    path('faqs/',views.faqs),
    path('error/',views.error)
]
