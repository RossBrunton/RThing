from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404

from courses.models import Course, Lesson

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
    
    if not ctx["course"].can_see(request.user):
        raise Http404
    
    return render(request, "courses/course.html", ctx)


@login_required
def lesson(request, course, lesson):
    ctx = {}
    ctx["course"] = get_object_or_404(Course, slug=course);
    ctx["lesson"] = get_object_or_404(Lesson, slug=lesson);
    ctx["all_lessons"] = filter(lambda l : l.can_see(request.user), ctx["course"].lessons.all())
    
    if not ctx["lesson"].can_see(request.user):
        raise Http404
    
    return render(request, "courses/lesson.html", ctx)
