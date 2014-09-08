"""Management features for the staff app"""
from django.contrib.auth.models import User, Group, Permission
from django.db.models import signals
from django.dispatch import receiver

from courses.models import Course, Lesson, Section, Task
import courses.models as models

@receiver(signals.post_syncdb)
def _post_syncdb(sender, **kwargs):
    """Creates the "Course Editor" group after syncdb
    
    sender is the model that was created.
    """
    
    if sender != models:
        return
    
    group = Group.objects.get_or_create(name="Course Editor")[0]
    
    permissions = [
        u"{}_{}".format(x, y)
        for x in ["add", "change", "delete"]
        for y in ["course", "lesson", "section", "task"]
    ]
    
    for p in permissions:
        group.permissions.add(Permission.objects.get(codename=p))
