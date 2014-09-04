"""View functions for courses"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from courses.models import Course, Lesson, Section, Task
from django.conf import settings

@login_required
def index(request):
    """Index page; displays a list of courses available to the user"""
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user);
    
    # Check if the user needs to change their password
    if request.user.extra.password_forced and not settings.USE_REMOTE_USER:
        return HttpResponseRedirect(u"{}?forced=1".format(reverse("users:edit")))
    
    return render(request, "courses/index.html", ctx)


@login_required
def course(request, course):
    """Course page; displays a description and list of lessons that the user can see"""
    ctx = {}
    ctx["all_courses"] = Course.get_courses(request.user)
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lessons"] = [\
        (l, l.complete_states(request.user))\
        for l in filter(lambda l : l.can_see(request.user), ctx["course"].lessons.all())
    ]
    
    if not ctx["course"].can_see(request.user):
        raise Http404
    
    return render(request, "courses/course.html", ctx)


@login_required
def lesson(request, course, lesson):
    """Lesson page; displays a lesson with an introduction and (usually) the first section and task)
    
    If a GET variable t exists like t=1, lesson 1 will be displayed
    If a GET variable t exists like t=1-1, task 1 of lesson 1 will be displayed
    
    Most of this page is manipulated by JavaScript and AJAX in the "tasks" app.
    """
    ctx = {}
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson, course=ctx["course"])
    ctx["all_lessons"] = filter(lambda l : l.can_see(request.user), ctx["course"].lessons.all())
    
    # Check user has permission
    if not ctx["lesson"].can_see(request.user):
        raise Http404
    
    # Load current task from URL
    section = 0
    task = 0
    try:
        section, task = request.GET.get("t", "1-1").split("-")
    except ValueError:
        section = request.GET.get("t", "1")
    
    # Check if it is valid
    try:
        task = int(task)
        section = int(section)
    except ValueError:
        task = 1
        section = 1
    
    # Get the section and task
    try:
        ctx["section"] = ctx["lesson"].sections.get(order=int(section)-1)
        try:
            ctx["task"] = ctx["section"].tasks.get(order=int(task)-1)
        except Task.DoesNotExist:
            try:
                ctx["task"] = ctx["section"].tasks.get(order=0)
            except:
                ctx["task"] = None
    except Section.DoesNotExist:
        try:
            ctx["section"] = ctx["lesson"].sections.get(order=0)
            ctx["task"] = ctx["section"].tasks.get(order=0)
        except (Section.DoesNotExist, Task.DoesNotExist):
            ctx["section"] = None
            ctx["task"] = None
            
    
    return render(request, "courses/lesson.html", ctx)


@login_required
def print_lesson(request, course, lesson):
    """Lesson page for print view, displays all sections and tasks in a print friendly format"""
    ctx = {}
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson, course=ctx["course"])
    
    # Check user has permission
    if not ctx["lesson"].can_see(request.user):
        raise Http404
    
    return render(request, "courses/print_lesson.html", ctx)


@login_required
def print_lesson_answers(request, course, lesson):
    """Lesson answer page for print view, displays everything along with answers in a print friendly format"""
    ctx = {}
    ctx["course"] = get_object_or_404(Course, slug=course)
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson, course=ctx["course"])
    
    # Check user has permission
    if not ctx["lesson"].can_see(request.user) or not (request.user.is_staff or ctx["lesson"].answers_published):
        raise Http404
    
    return render(request, "courses/print_lesson_answers.html", ctx)
