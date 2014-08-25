from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from courses.models import Course, Lesson, Section, Task
from staff.forms import NamespaceUploadForm

from os import path
import settings
import os

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user)
    
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


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_users(request, course):
    course = get_object_or_404(Course, slug=course)
    
    if request.method == "POST":
        if not "users" in request.POST:
            raise SuspiciousOperation
        
        users = request.POST.get("users", "").split("\n")
        
        course.users.clear()
        
        for user in users:
            u = user.strip().split(" ")[0]
            
            if u:
                user_obj = None
                try:
                    user_obj = User.objects.get(username=u)
                except User.DoesNotExist:
                    user_obj = User.objects.create_user(u, u"{}@{}".format(u, settings.EMAIL_DOMAIN), u)
                
                course.users.add(user_obj)
            
        return redirect("courses:course", course=course.slug)
                
    else:
        ctx = {}
        ctx["course"] = course
        ctx["users"] = u"\n".join([u.username for u in course.users.all()])
        return render(request, "staff/add_user.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def strain(request, task):
    ctx = {}
    ctx["task"] = get_object_or_404(Task, pk=task);
    
    return render(request, "staff/strain.html", ctx)
