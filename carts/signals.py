from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import Basket

@receiver(post_save, sender=User)
def create_user_basket(sender, instance, created, **kwargs):
    if created:
        Basket.objects.create(user=instance)
