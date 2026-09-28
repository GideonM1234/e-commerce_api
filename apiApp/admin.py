from django.contrib import admin
from .models import( Category, ProductRating, Products, CustomUser,
                    Cart, CartItem, Review, WishList, Order, OrderItem
    
                    )
from django.contrib.auth.admin import UserAdmin



class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "featured")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug") 
   

admin.site.register(Category, CategoryAdmin)
admin.site.register(Products, ProductAdmin )
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register([Review, ProductRating, WishList, Order, OrderItem])

# Register your models here.
