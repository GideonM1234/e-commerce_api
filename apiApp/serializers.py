from rest_framework import serializers
from .models import Cart, Products, Category, CartItem, Review, WishList
from django.contrib.auth import get_user_model


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ["id",  "name","product_image","price", "slug" ]
        
class ProductDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
        

class CategoryListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name", "slug", "category_image"]


class CategoryDetailedSerializers(serializers.ModelSerializer):
    products = ProductListSerializer(many = True, read_only = True)
    class Meta:
        model = Category
        fields = ['id', "name", "category_image", "products"]       
        

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only = True)
    sub_total  = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "sub_total"]
    
    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity
        return total


class CartSerializer(serializers.ModelSerializer):
    cart_item = CartItemSerializer(read_only = True, many = True)
    cart_total  = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart 
        fields = ["id", "cart_code", "cart_item", "cart_total"]       
        
    def  get_cart_total(self, cart):
        items = cart.cart_item.all()
        total = sum([i.quantity * i.product.price for i in items])
        return total

class CartStatSerializer(serializers.ModelSerializer):
    total_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ["id", "cart_code","total_quantity"] 
        
    def count_cart(self, cartcount):
        items = cart.cart_item.all()
        total = sum([i.quantity  for i in items])
        return total


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "profile_picture_url"]


class ReviewSerializer(serializers.ModelSerializer):
    user =  UserSerializer(read_only = True)
    
    class Meta:
        model  = Review
        fields = ["id", "rating", "user", "reviews", "created_at", "update_at"]
    
    
class WishListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    product = ProductListSerializer(read_only = True)
    
    class Meta:
        model = WishList
        fields = ["id", "user", "product" , "created_at"]
    