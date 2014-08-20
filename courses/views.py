from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404

from courses.models import Course, Lesson, Section, Task

from ifaces.r import r

@login_required
def index(request):
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user);
    
    return render(request, "courses/index.html", ctx)


@login_required
def course(request, course):
    ctx = {}
    ctx["all_courses"] = Course.get_courses(request.user);
    ctx["course"] = get_object_or_404(Course, slug=course);
    ctx["lessons"] = filter(lambda l : l.can_see(request.user), ctx["course"].lessons.all())
    
    for x in xrange(0, 2):
        r.run({
            "commands":"print('hello world');", "namespace":1, "uses_random":True,
            "uses_image":True, "automark":False, "seed":1
        })
    
    if not ctx["course"].can_see(request.user):
        raise Http404
    
    return render(request, "courses/course.html", ctx)


@login_required
def lesson(request, course, lesson):
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
            ctx["task"] = ctx["section"].tasks.get(order=0)
    except Section.DoesNotExist:
        try:
            ctx["section"] = ctx["lesson"].sections.get(order=0)
            ctx["task"] = ctx["section"].tasks.get(order=0)
        except (Section.DoesNotExist, Task.DoesNotExist):
            ctx["section"] = None
            ctx["task"] = None
            
    
    return render(request, "courses/lesson.html", ctx)
