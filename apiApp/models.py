from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(null=True, blank=True)
    
    
    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    category_image = models.ImageField(upload_to="category_image",
            blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Category.objects.filter(slug = unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
                self.slug = unique_slug
            
        super().save(*args, **kwargs)
            
            
    def __str__(self):
        return self.name        

        
class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    product_image = models.ImageField(upload_to="product_image",
                                    blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                blank=True, null=True, related_name="products")
    featured = models.BooleanField(default=False)
    
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Products.objects.filter(slug = unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter += 1
                self.slug = unique_slug
            
        super().save(*args, **kwargs)
            
            
    def __str__(self):
        return self.name 
        
        
class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.cart_code
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_item")   
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="item")
    quantity = models.IntegerField(default=1)
    

    def __str__(self):
        return f"{self.quantity} X {self.product.name} in cart {self.cart.cart_code} "



class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
        
    ]
                        
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="review")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                            on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    reviews  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.user.email}'s reviews on {self.product.name}"
    
    
    class Meta:
        unique_together = ["user", "product"]
        ordering = ["created_at"]
        

class ProductRating(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE, related_name="rating")
    average_rating = models.FloatField(default=0.0)
    total_review = models.PositiveIntegerField(default=0)
    
    
    def __str__(self):
        return f"{self.product.name} - {self.average_rating}, {self.total_review} reviews"
    
    
class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                            on_delete=models.CASCADE, related_name="wishlists")   
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="wishlists")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        unique_together = ["user", "product"]
        ordering = ["created_at"]
        
    def __str__(self):
        return f"{self.user.username} = {self.product.name}"
    
    
    
class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.stripe_checkout_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.product.name} - {self.order.stripe_checkout_id}"    
        
