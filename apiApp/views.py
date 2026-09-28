from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe

from .models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    ProductRating,
    Products,
    Review,
    WishList,
)
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategoryDetailedSerializers,
    CategoryListSerializers,
    ProductDetailedSerializer,
    ProductListSerializer,
    ReviewSerializer,
    WishListSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEB_HOOK_SECRET

User = get_user_model()


@api_view(["GET"])
def product_list(request):
    products = Products.objects.filter(featured=True)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def product_details(request, slug):
    product = get_object_or_404(Products, slug=slug)
    serializer = ProductDetailedSerializer(product)
    return Response(serializer.data)


@api_view(["GET"])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategoryListSerializers(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def category_detail(request, slug):
    categories = Category.objects.filter(slug=slug)
    serializer = CategoryDetailedSerializers(categories, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def add_to_cart(request):
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")

    if not cart_code or not product_id:
        return Response(
            {"error": "cart_code and product_id are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart, _ = Cart.objects.get_or_create(cart_code=cart_code)
    product = get_object_or_404(Products, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        product=product, cart=cart, defaults={"quantity": 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_cartitem(request, pk):
    cartitem = get_object_or_404(CartItem, id=pk)
    cartitem.delete()
    return Response(
        "Cart Item Successfully Deleted", status=status.HTTP_204_NO_CONTENT
    )


@api_view(["PUT"])
def update_cartitem_quantity(request):
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    if cartitem_id is None or quantity is None:
        return Response(
            {"error": "item_id and quantity are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cartitem = get_object_or_404(CartItem, id=cartitem_id)
    cartitem.quantity = int(quantity)
    cartitem.save()

    serializer = CartItemSerializer(cartitem)
    return Response(
        {"data": serializer.data, "message": "CartItem updated successfully"}
    )


@api_view(["POST"])
def add_review(request):
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating = request.data.get("rating")
    review_text = request.data.get("reviews")

    try:
        product = Products.objects.get(id=product_id)
        user = User.objects.get(email__iexact=email)
    except Products.DoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User with this email not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if Review.objects.filter(product=product, user=user).exists():
        return Response(
            "You already dropped a review on this product",
            status=status.HTTP_400_BAD_REQUEST,
        )

    review = Review.objects.create(
        rating=rating,
        reviews=review_text,
        product=product,
        user=user,
    )

    serializer = ReviewSerializer(review)
    return Response(
        {
            "data": serializer.data,
            "message": "Your Reviews have been created Successfully",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
def update_review(request, pk):
    rating = request.data.get("rating")
    review_text = request.data.get("reviews")

    review_obj = get_object_or_404(Review, id=pk)
    review_obj.rating = rating
    review_obj.reviews = review_text
    review_obj.save()

    serializer = ReviewSerializer(review_obj)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_review(request, pk):
    reviews = get_object_or_404(Review, id=pk)
    reviews.delete()
    return Response(
        "Review Successfully Deleted", status=status.HTTP_204_NO_CONTENT
    )


@api_view(["POST"])
def add_to_wishlist(request):
    product_id = request.data.get("item_id")
    email_text = request.data.get("email")

    user = get_object_or_404(User, email__iexact=email_text)
    product = get_object_or_404(Products, id=product_id)

    wishlist_item = WishList.objects.filter(user=user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        return Response(
            {"message": "Item removed from wishlist successfully."},
            status=status.HTTP_200_OK,
        )

    new_wishlist = WishList.objects.create(product=product, user=user)
    serializer = WishListSerializer(new_wishlist)

    return Response(
        {
            "data": serializer.data,
            "message": "You have successfully added to wishlist",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def product_search(request):
    query = request.query_params.get("query")

    if not query:
        return Response(
            "No query Provided", status=status.HTTP_400_BAD_REQUEST
        )

    products = Products.objects.filter(
        Q(name__icontains=query)
        | Q(description__icontains=query)
        | Q(category__name__icontains=query)
    )

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code") or request.query_params.get(
        "cart_code"
    )
    email = request.data.get("email") or request.query_params.get("email")

    if not cart_code:
        return Response(
            {"error": "cart_code is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        return Response(
            {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
        )

    cart_items = cart.cart_item.all()
    if not cart_items.exists():
        return Response(
            {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item.product.name},
                        "unit_amount": int(item.product.price * 100),
                    },
                    "quantity": item.quantity,
                }
                for item in cart_items
            ]
            + [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "VAT Fee"},
                        "unit_amount": 500,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://next-shop-self.vercel.app/success",
            cancel_url="https://next-shop-self.vercel.app/failed",
            metadata={"cart_code": str(cart_code)},
        )
        return Response(
            {"id": checkout_session.id, "url": checkout_session.url}
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not sig_header:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] in [
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    ]:
        session = event["data"]["object"]
        session_dict = session.to_dict()
        cart_code = session_dict.get("metadata", {}).get("cart_code")
        fulfill_checkout(session=session_dict, cart_code=cart_code)

    return HttpResponse(status=200)



def fulfill_checkout(session, cart_code):
    if not cart_code:
        return
    

    # Check if order already created (idempotency)
    if Order.objects.filter(stripe_checkout_id=session.get("id")).exists():
        return

    try:
        cart = Cart.objects.get(cart_code=cart_code)
    except Cart.DoesNotExist:
        return

    # Fallback for email in case customer_email is None
    customer_email = session.get("customer_email") or session.get(
        "customer_details", {}
    ).get("email")

    order = Order.objects.create(
        stripe_checkout_id=session.get("id"),
        amount=session.get("amount_total", 0) / 100,
        customer_email=customer_email,
        currency=session.get("currency", "usd"),
        status="Paid",
    )

    for item in cart.cart_item.all():
        OrderItem.objects.create(
            order=order, product=item.product, quantity=item.quantity
        )

    cart.delete()