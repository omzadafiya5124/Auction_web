from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, "index.html" , {"home" : "Home page"})

def about(request):
    return render(request, "about.html" , {"about" : "About us"})

def auction(request):
    return render(request, "auction.html" , {"auction" : "Auction"})

def auc_details(request):
    return render(request, "auction-details.html" , {"auc_details" : "Auction Details"})

def blog(request):
    return render(request, "blog.html" , {"blog" : "Blog Details"})

def category(request):
    return render(request, "category.html" , {"category" : "Category"})

def contact(request):
    return render(request, "contact.html" , {"contact" : "Contact Details"})

def seller_list(request):
    return render(request, "seller_list.html" , {"seller" : "Seller list"})

def seller_details(request):
    return render(request, "seller_details.html" , {"seller_details" : "Seller Details"})

def how_to_sell(request):
    return render(request, "how-to-sell.html" , {"how_to_sell" : "How to sell"})

def how_to_bid(request):
    return render(request, "how-to-buy.html" , {"how_to_bid" : "How to bid"})

def faqs(request):
    return render(request, "faq.html" , {"faq" : "FAQ"})

def error(request):
    return render(request, "error.html" , {"error" : "Error"})
