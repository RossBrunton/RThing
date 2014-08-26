from __future__ import division
from stats.models import UserOnTask
from functools import reduce

def attempts(**kwargs):
    """Who has attempted this task"""
    return UserOnTask.objects.filter(user__is_staff=False, tries__gte=1, **kwargs).count()

def correct(**kwargs):
    """How many people have gotten this task correct"""
    return UserOnTask.objects.filter(state=UserOnTask.STATE_CORRECT, user__is_staff=False, **kwargs).count()

def revealed(**kwargs):
    """How many people have revealed the answer to this question"""
    return UserOnTask.objects.filter(state=UserOnTask.STATE_REVEALED, user__is_staff=False, **kwargs).count()

def average_tries_correct(**kwargs):
    """For the people that got it correct, what is the average number of tries"""
    q = UserOnTask.objects.filter(state=UserOnTask.STATE_CORRECT, user__is_staff=False, **kwargs)
    try:
        return reduce(lambda a, v: a + v.tries, q, 0) / q.count()
    except ZeroDivisionError:
        return 0.0

def average_tries_reveal(**kwargs):
    """For the people that revealed the answer, what is the average number of tries"""
    q = UserOnTask.objects.filter(state=UserOnTask.STATE_REVEALED, user__is_staff=False, **kwargs)
    try:
        return reduce(lambda a, v: a + v.tries, q, 0) / q.count()
    except ZeroDivisionError:
        return 0.0

def completion(**kwargs):
    """Of the users who have attempted this task; what fraction got it right"""
    try:
        return correct(**kwargs) / attempts(**kwargs)
    except ZeroDivisionError:
        return 0.0
