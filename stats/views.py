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
                    "attempts":utils.attempts(t),
                    "correct":utils.correct(t),
                    "revealed":utils.revealed(t),
                    "average_tries_correct":utils.average_tries_correct(t),
                    "average_tries_reveal":utils.average_tries_reveal(t),
                    "completion":utils.completion(t)
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
    print(ctx["wrong"])
    
    return render(request, "stats/wrong.html", ctx)
