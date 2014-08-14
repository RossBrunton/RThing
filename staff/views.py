from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.views.decorators.http import require_POST

from courses.models import Course, Lesson, Section, Task
from staff.forms import NamespaceUploadForm

from os import path
import settings
import os

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user);
    
    return render(request, "staff/index.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def upload(request, course, lesson):
    course = get_object_or_404(Course, slug=course)
    lesson = get_object_or_404(Lesson, slug=lesson)
    
    form = NamespaceUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        raise SuspiciousOperation
    
    name = path.basename(request.FILES["file"].name)
    
    with open(path.join(settings.NAMESPACE_DIR, str(lesson.pk), name), "wb+") as dest:
        for chunk in request.FILES["file"].chunks():
            dest.write(chunk)
    
    # Set permissions
    os.chmod(path.join(settings.NAMESPACE_DIR, str(lesson.pk), name), 0o640)
    
    return redirect("courses:lesson", course=course.slug, lesson=lesson.slug)
