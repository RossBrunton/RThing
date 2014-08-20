from stats.models import UserOnTask

def attempts(task):
    """Who has attempted this task"""
    return UserOnTask.objects.filter(task=task).count()

def correct(task):
    """How many people have gotten this task correct"""
    return UserOnTask.objects.filter(task=task, correct=True).count()

def completion(task):
    """Of the users who have attempted this task; what fraction got it right"""
    try:
        return float(correct(task)) / attempts(task)
    except ZeroDivisionError:
        return 0.0
