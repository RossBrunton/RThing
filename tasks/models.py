from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import defaultfilters

from courses.models import Task

class UserTaskStatusModel(models.Model):
    user = models.ForeignKey(User, related_name="uts")
    task = models.ForeignKey(Task, related_name="uts")
