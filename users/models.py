"""Database models for users"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Task
from rthing.utils import py2_str

@py2_str
class UserExtraData(models.Model):
    """Extra data associated with users
    
    When a user is created, an instance of this model is created for them.
    
    It contains the task that was last ran, the time it was ran and the code and output that was used. At the moment
    code that uses this is commented out, since it is unstable.
    
    This model has the following fields:
    user - The user the extra data is for.
    last_script_time - The time the last script was ran.
    last_script_output - The last script output.
    last_script_error - The last script error output.
    last_task - The last task that was ran by the user.
    password_forced - If true, then the user has to change their password the next time they log in.
    """ 
    user = models.OneToOneField(User, related_name="extra")
    
    last_script_time = models.DateTimeField(blank=True, auto_now_add=True)
    
    last_script_code = models.TextField(default="", max_length=1000, blank=True)
    last_script_output = models.TextField(default="", max_length=1000, blank=True)
    last_script_error = models.BooleanField(default=False, blank=True)
    last_task = models.ForeignKey(Task, null=True, default=None, on_delete=models.SET_NULL)
    
    password_forced = models.BooleanField(default=True)
    
    def __str__(self):
        return u"Extra data for {}".format(self.user.username)

@receiver(post_save, sender=User)
def _user_created(sender, instance, created, **kwargs):
    """When a user is created, create a UserExtraData object for them"""
    if created:
        UserExtraData.objects.get_or_create(user=instance)

