from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserExtraData(models.Model):
    user = models.OneToOneField(User, related_name="extra")

@receiver(post_save, sender=User)
def _user_created(sender, instance, created, **kwargs):
    if created:
        UserExtraData.objects.get_or_create(user=instance)
