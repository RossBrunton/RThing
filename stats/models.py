from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Task

class UserOnTask(models.Model):
    user = models.ForeignKey(User, related_name="uots")
    task = models.ForeignKey(Task, related_name="uots")
    
    tries = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)
    
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
    
    def __str__(self):
        return "WrongAnswer for {}".format(self.uot.__str__())
