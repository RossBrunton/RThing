from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Task

class UserOnTask(models.Model):
    STATE_NONE = "n"
    STATE_CORRECT = "c"
    STATE_REVEALED = "r"
    STATE_CHOICES = ((STATE_NONE, "None"), (STATE_CORRECT, "Correct"), (STATE_REVEALED, "Revealed"))
    
    user = models.ForeignKey(User, related_name="uots")
    task = models.ForeignKey(Task, related_name="uots")
    
    tries = models.IntegerField(default=0)
    state = models.CharField(default="n", max_length=1, choices=STATE_CHOICES)
    skipped = models.BooleanField(default=False)
    seed = models.IntegerField(default=0)
    last = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "UserOnTask for {} with {}".format(self.user.username, self.task.__str__())
    
    def add_wrong_answer(self, code):
        # After 10 tries don't add a wrong answer
        if self.tries > 10:
            return
        
        wa = WrongAnswer(uot=self, code=code)
        wa.save()
        
        self.wrong_answers.add(wa)


class WrongAnswer(models.Model):
    uot = models.ForeignKey(UserOnTask, related_name="wrong_answers")
    code = models.TextField(default="", max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "WrongAnswer for {}".format(self.uot.__str__())
