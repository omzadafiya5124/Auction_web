    # In accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


#For Edit profile
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'))
    ACCOUNT_TYPE_CHOICES = (('Bidder', 'Bidder'), ('Seller', 'Seller'))
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    mobile_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','date_of_birth']

    def __str__(self):
        return self.email
    
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    sub_description = models.TextField(default='')
    product_description = models.TextField()
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    auction_start_date_time = models.DateTimeField(default=timezone.now)
    auction_end_date_time = models.DateTimeField()

    main_image = models.ImageField(upload_to="products/")
    # This field will store a list of paths to the gallery images
    gallery_images = models.JSONField(default=list, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.product_name

    # Set current_bid to start_price when a new product is created
    def save(self, *args, **kwargs):
        if not self.id and self.current_bid is None:
            self.current_bid = self.start_price
        super().save(*args, **kwargs)

    # **CRITICAL**: Custom delete method to remove associated files from storage
    def delete(self, *args, **kwargs):
        # First, delete the main image file
        self.main_image.delete(save=False)
        
        # Loop through the JSON list and delete each gallery image file
        for image_path in self.gallery_images:
            if default_storage.exists(image_path):
                default_storage.delete(image_path)

        # Call the original delete method
        super().delete(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    email = models.EmailField()
    message = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.product.name} by {self.name}'

#Contect Form
class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True) # blank=True makes it optional
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"  