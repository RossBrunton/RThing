from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from courses.models import Course, Lesson, Section, Task

from stats import utils

@login_required
@user_passes_test(lambda u: u.is_staff)
def lesson(request, course, lesson):
    ctx = {}
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson, course=ctx["course"])
    ctx["all_lessons"] = ctx["course"].lessons.all()
    
    # List comprehension, because Python
    ctx["sectiondata"] = [
        {
            "taskdata":[
                {
                    "task":t,
                    "attempts":utils.attempts(task=t),
                    "correct":utils.correct(task=t),
                    "revealed":utils.revealed(task=t),
                    "average_tries_correct":utils.average_tries_correct(task=t),
                    "average_tries_reveal":utils.average_tries_reveal(task=t),
                    "completion":utils.completion(task=t)
                }
                for t in s.tasks.all()
            ],
            "section":s
        }
        for s in ctx["lesson"].sections.all()
    ]
    
    return render(request, "stats/lesson.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def wrong(request, task):
    ctx = {}
    ctx["task"] = get_object_or_404(Task, pk=task)
    ctx["lesson"] = ctx["task"].section.lesson
    ctx["wrong"] = [uot.wrong_answers.all() for uot in ctx["task"].uots.all()]
    
    return render(request, "stats/wrong.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def user(request, name, course):
    ctx = {}
    ctx["user"] = get_object_or_404(User, username=name)
    
    return render(request, "stats/wrong.html", ctx)
