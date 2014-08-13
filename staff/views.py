from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404

from courses.models import Course, Lesson, Section, Task

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user);
    
    return render(request, "staff/index.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def course(request, course):
    ctx = {}
    ctx["all_courses"] = Course.get_courses(request.user);
    ctx["course"] = get_object_or_404(Course, slug=course);
    ctx["lessons"] = filter(lambda l : l.can_see(request.user), ctx["course"].lessons.all())
    
    if not ctx["course"].can_see(request.user):
        raise Http404
    
    return render(request, "staff/course.html", ctx)
