"""Database models for statistics"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from courses.models import Task
from rthing.utils import py2_str

@py2_str
class UserOnTask(models.Model):
    """Represents a user on a task
    
    This model has the following fields:
    user - The user that is on the task.
    task - The task that the user is on.
    tries - The number of tries that the user has made on this task. Stops counting when they reveal or get it right.
    state - One of STATE_NONE (User has not attempted the question), STATE_CORRECT (user has answered the task
    correctly) or STATE_REVEALED (User has revealed the answer).
    skipped - Whether the user has skipped the task at least once.
    seed - The seed that was generated the last time the user ran this question.
    last - The time when the student last executed this task.
    """
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
        return u"UserOnTask for {} with {}".format(self.user.username, self.task.__str__())
    
    def add_wrong_answer(self, code):
        """Given a string, creates links a WrongAnswer with that code to this"""
        # After 10 tries don't add a wrong answer
        if self.tries > 10:
            return
        
        wa = WrongAnswer(uot=self, code=code)
        wa.save()
        
        self.wrong_answers.add(wa)
    
    @property
    def status(self):
        """One of the following with increasing priority:
        
        "Not attempted yet" if the user hasn't yet tried the question.
        "Attempted" if the user has attempted the question.
        "Skipped" if the user has skipped the question.
        "Skipped with no attempt" if the user has skipped the question with no attempts.
        "Correct" if the user has attempted the question and got it correct.
        "Revealed" if the user has revealed the answer before getting it correct.
        "Revealed with no attempt" if the user has revealed the question without attempting it.
        
        "Revealed", "Correct" and "Skiped" are ignored if the task is not automark.
        """
        if self.tries == 0 and self.state == UserOnTask.STATE_REVEALED: return "Revealed with no attempt"
        if self.state == UserOnTask.STATE_REVEALED and self.task.automark: return "Revealed"
        if self.state == UserOnTask.STATE_CORRECT and self.task.automark: return "Correct"
        if self.skipped and self.tries == 0: return "Skipped with no attempt"
        if self.skipped and self.task.automark: return "Skipped"
        if self.tries > 0: return "Attempted"
        return "Not attempted yet"
    
    @property
    def status_colour(self):
        """A class name for fancy text based on the status as follows:
        
        "Not attempted yet" - "no-attempt"
        "Attempted" - "attempt"
        "Skipped" - "okay"
        "Skipped with no attempt" - "bad"
        "Correct" - "good"
        "Revealed" - "okay"
        "Revealed with no attempt" - "bad"
        """
        if self.status == "Not attempted yet": return "no-attempt"
        if self.status == "Attempted": return "attempt"
        if self.status == "Skipped": return "okay"
        if self.status == "Skipped with no attempt": return "bad"
        if self.status == "Correct": return "good"
        if self.status == "Revealed": return "okay"
        if self.status == "Revealed with no attempt": return "bad"
    
    @property
    def status_span(self):
        """A string containing a HTML span element with the state and its style"""
        return "<span class='fancy {}'>{}</span>".format(self.status_colour, self.status)


@py2_str
class WrongAnswer(models.Model):
    """Represents a single wrong answer to a task
    
    This model has the following fields:
    uot - The UOT that this is associated with.
    code - The code that was ran.
    time - The time that the answer was submitted.
    """
    uot = models.ForeignKey(UserOnTask, related_name="wrong_answers")
    code = models.TextField(default="", max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return u"WrongAnswer for {}".format(self.uot.__str__())
