"""Views for staff functions, most of these are only visible to staff members"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.transaction import atomic

from courses.models import Course, Lesson, Section, Task
from staff.forms import NamespaceUploadForm, DeleteForm

from os import path
from django.conf import settings
import os
import re

@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    """Index page, simply render a template (staff/index.html) with all the courses"""
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user)
    
    return render(request, "staff/index.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
def help_formatting(request):
    """Formatting help renders a template (staff/help_formatting.html)"""
    return render(request, "staff/help_formatting.html", {})

@login_required
@user_passes_test(lambda u: u.is_staff)
def help_general(request):
    """General help, using the template staff/help_general.html"""
    return render(request, "staff/help_general.html", {})


@login_required
@user_passes_test(lambda u: u.is_staff)
def add_users(request, course):
    """Handles adding or removing users
    
    Will display a form if GET or incomplete POST, and will erase and re-add all users on a valid POST.
    
    The form used is staff/add_user.html.
    """
    course = get_object_or_404(Course, slug=course)
    
    if request.method == "POST":
        with atomic():
            if not "users" in request.POST:
                raise SuspiciousOperation
            
            users = request.POST.get("users", "").split("\n")
            
            course.users.clear()
            
            for user in users:
                u = user.strip().split(" ")[0]
                
                if u and re.match("^[a-zA-Z0-9@.+_-]+$", u) is not None:
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
    """Renders a template (staff/strain.html) which will make requests every 10 seconds or so"""
    ctx = {}
    ctx["task"] = get_object_or_404(Task, pk=task);
    
    return render(request, "staff/strain.html", ctx)


def _get_path(location, basename, lesson):
    """Takes a location (from NamespaceUploadForm) and a basename and returns the file path that it points to
    
    Also replaces any whitespace in the name with underscores.
    """
    basename = re.sub("\s", "_", basename)
    
    if location == NamespaceUploadForm.LOC_SANDBOX:
        return path.join(settings.NAMESPACE_DIR, str(lesson.pk), basename)
    
    if location == NamespaceUploadForm.LOC_TASK:
        return path.join(settings.MEDIA_ROOT, str(lesson.pk), basename)
    
    raise RuntimeError(u"Location {} isn't valid".format(location))


@login_required
@user_passes_test(lambda u: u.is_staff)
def files(request, course, lesson):
    """File manager view, handles uploading of files
    
    Will display a form (staff/files.html) on GET or invalid POST, or add an uploaded file on valid POST.
    """
    course = get_object_or_404(Course, slug=course)
    lesson = get_object_or_404(Lesson, slug=lesson, course=course)
    
    # If it doesn't exist, create a directory in media root for the files
    if not path.isdir(path.join(settings.MEDIA_ROOT, str(lesson.pk))):
        os.mkdir(path.join(settings.MEDIA_ROOT, str(lesson.pk)), 0o750)
    
    # Create context for template
    ctx = {}
    ctx["course"] = course
    ctx["lesson"] = lesson
    ctx["task_files"] = os.listdir(path.join(settings.MEDIA_ROOT, str(lesson.pk)))
    ctx["sandbox_files"] = os.listdir(path.join(settings.NAMESPACE_DIR, str(lesson.pk)))
    ctx["delete_form"] = DeleteForm(auto_id=False)
    
    if request.method == "POST":
        ctx["form"] = NamespaceUploadForm(request.POST, request.FILES)
        
        if not ctx["form"].is_valid():
            # Form invalid
            return render(request, "staff/files.html", ctx)
        
        basename = path.basename(request.FILES["file"].name)
        filename = _get_path(ctx["form"].cleaned_data["location"], basename, lesson)
        
        # Copy the file
        with open(filename, "wb+") as dest:
            for chunk in request.FILES["file"].chunks():
                dest.write(chunk)
        os.chmod(filename, 0o640)
        
        # Now change to a get request and start over
        request.method = "GET"
        return files(request, course.slug, lesson.slug)
    else:
        ctx["form"] = NamespaceUploadForm()
        
        return render(request, "staff/files.html", ctx)


@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def delete(request, course, lesson):
    """Deletes an uploaded file using DeleteForm"""
    course = get_object_or_404(Course, slug=course)
    lesson = get_object_or_404(Lesson, slug=lesson, course=course)
    
    form = DeleteForm(request.POST)
    if not form.is_valid():
        raise SuspiciousOperation
    
    basename = form.cleaned_data["basename"]
    filepath = _get_path(form.cleaned_data["location"], basename, lesson)
    
    if not path.isfile(filepath):
        raise SuspicousOperation
    
    os.remove(filepath)
    
    return redirect("staff:files", lesson=lesson.slug, course=course.slug)
