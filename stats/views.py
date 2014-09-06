from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from six.moves import cStringIO as StringIO
import csv

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
                    "users_on_course":ctx["course"].users.all().count(),
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
def csv_lesson(request, course, lesson):
    course = get_object_or_404(Course, slug=course)
    lesson = get_object_or_404(Lesson, slug=lesson, course=course)
    
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Headers
    writer.writerow(
        ["Section", "Task", "Attempts", "Correct", "Revealed"]
    )
    
    section_number = 0
    for s in lesson.sections.all():
        section_number += 1
        task_number = 0
        for t in s.tasks.all():
            task_number += 1
            writer.writerow(
                [section_number, task_number, utils.attempts(task=t), utils.correct(task=t), utils.revealed(task=t)]
            )
    
    return HttpResponse(buffer.getvalue(), "text/csv")


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
def user(request, name, course, lesson):
    ctx = {}
    ctx["target_user"] = get_object_or_404(User, username=name)
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson, course=ctx["course"])
    
    ctx["all_users"] = ctx["course"].users.all()
    ctx["all_lessons"] = ctx["course"].lessons.all()
    
    ctx["overall"] = {
        "attempts":utils.attempts(user=ctx["target_user"], task__section__lesson=ctx["lesson"]),
        "correct":utils.correct(user=ctx["target_user"], task__section__lesson=ctx["lesson"]),
        "revealed":utils.revealed(user=ctx["target_user"], task__section__lesson=ctx["lesson"]),
        "average_tries_correct":
            utils.average_tries_correct(user=ctx["target_user"], task__section__lesson=ctx["lesson"]),
        "average_tries_reveal":utils.average_tries_reveal(user=ctx["target_user"], task__section__lesson=ctx["lesson"]),
        "completion":utils.completion(user=ctx["target_user"], task__section__lesson=ctx["lesson"])
    }
    
    ctx["responses"] = [
        {
            "section":s,
            "tasks":[
                {
                    "task":t,
                    "uot":t.get_uot(ctx["target_user"])
                }
                for t in s.tasks.all()
            ]
        }
        for s in ctx["lesson"].sections.all()
    ]
    
    ctx["task_count"] = 0
    for s in ctx["lesson"].sections.all():
        ctx["task_count"] += s.tasks.all().count()
    
    
    return render(request, "stats/user.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def csv_users(request, course, lesson):
    course = get_object_or_404(Course, slug=course)
    lesson = get_object_or_404(Lesson, slug=lesson, course=course)
    
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Headers
    writer.writerow(
        ["Username", "Attempts", "Correct", "Revealed"]
    )
    
    users = course.users.all()
    
    for u in users:
        writer.writerow([
            u.username,
            utils.attempts(user=u, task__section__lesson=lesson),
            utils.correct(user=u, task__section__lesson=lesson),
            utils.revealed(user=u, task__section__lesson=lesson),
        ])
    
    
    return HttpResponse(buffer.getvalue(), "text/csv")
