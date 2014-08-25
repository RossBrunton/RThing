from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Task

class UserExtraData(models.Model):
    user = models.OneToOneField(User, related_name="extra")
    
    last_script_time = models.DateTimeField(blank=True, auto_now_add=True)
    
    last_script_code = models.TextField(default="", max_length=1000, blank=True)
    last_script_output = models.TextField(default="", max_length=1000, blank=True)
    last_script_error = models.BooleanField(default=False, blank=True)
    last_task = models.ForeignKey(Task, null=True, default=None)
    
    password_forced = models.BooleanField(default=True)
    
    def __str__(self):
        return u"Extra data for {}".format(self.user.username)

@receiver(post_save, sender=User)
def _user_created(sender, instance, created, **kwargs):
    if created:
        UserExtraData.objects.get_or_create(user=instance)

