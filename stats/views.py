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
                    "completion":utils.completion(t)
                }
                for t in s.tasks.all()
            ],
            "section":s
        }
        for s in ctx["lesson"].sections.all()
    ]
    
    return render(request, "stats/lesson.html", ctx)
