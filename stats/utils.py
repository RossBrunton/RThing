from __future__ import division
from stats.models import UserOnTask

def attempts(task):
    """Who has attempted this task"""
    return UserOnTask.objects.filter(task=task, user__is_staff=False).count()

def correct(task):
    """How many people have gotten this task correct"""
    return UserOnTask.objects.filter(task=task, state=UserOnTask.STATE_CORRECT, user__is_staff=False).count()

def revealed(task):
    """How many people have revealed the answer to this question"""
    return UserOnTask.objects.filter(task=task, state=UserOnTask.STATE_REVEALED, user__is_staff=False).count()

def average_tries_correct(task):
    """For the people that got it correct, what is the average number of tries"""
    q = UserOnTask.objects.filter(task=task, state=UserOnTask.STATE_CORRECT, user__is_staff=False)
    try:
        return reduce(lambda a, v: a + v.tries, q, 0) / q.count()
    except ZeroDivisionError:
        return 0.0

def average_tries_reveal(task):
    """For the people that revealed the answer, what is the average number of tries"""
    q = UserOnTask.objects.filter(task=task, state=UserOnTask.STATE_REVEALED, user__is_staff=False)
    try:
        return reduce(lambda a, v: a + v.tries, q, 0) / q.count()
    except ZeroDivisionError:
        return 0.0

def completion(task):
    """Of the users who have attempted this task; what fraction got it right"""
    try:
        return correct(task) / attempts(task)
    except ZeroDivisionError:
        return 0.0
