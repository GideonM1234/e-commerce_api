from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import ProductRating, Review


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    product = instance.product  # singular
    reviews = product.review.all()
    total_reviews = reviews.count()
    reviews_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0

    product_rating, created = ProductRating.objects.get_or_create(
        product=product,
    )
    product_rating.average_rating = reviews_average
    product_rating.total_review = total_reviews
    product_rating.save()


@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    product = instance.product  # singular
    reviews = product.review.all()
    total_reviews = reviews.count()
    reviews_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0

    product_rating, created = ProductRating.objects.get_or_create(
        product=product,
    )
    product_rating.average_rating = reviews_average
    product_rating.total_review = total_reviews
    product_rating.save()