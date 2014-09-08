"""Views for handling requests"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core import serializers
from django.forms import ValidationError

from courses.models import Course, Lesson, Section, Task
from export.parse import encode, decode
from export.forms import ImportForm

from os import path
from django.conf import settings
import os
import json

@login_required
@user_passes_test(lambda u: u.is_staff)
def export(request, course):
    """With the given course (as a slug) returns a response containing it's encoded data"""
    data = get_object_or_404(Course, slug=course).to_dict()
    
    return HttpResponse(encode(data), "text/plain")

@login_required
@user_passes_test(lambda u: u.is_staff)
def import_(request):
    """Generates and accepts GET and POST requests for importing courses
    
    If the request is get or an invalid POST, uses the template export/import.html, if valid then redirect to the newly
    uploaded course.
    """
    ctx = {}
    if request.method == "GET":
        # Return an empty form
        ctx["form"] = ImportForm()
        return render(request, "export/import.html", ctx)
    else:
        # Try to import the course
        ctx["form"] = ImportForm(request.POST)
        
        if not ctx["form"].is_valid():
            # Form invalid? Send it right back to the user
            return render(request, "export/import.html", ctx)
        
        try:
            # Attempt decode
            data = decode(ctx["form"].cleaned_data["text"].replace("\r\n", "\n"))
            
            if data is None:
                raise RuntimeError("No data could be extracted from the import")
            
            new = Course.from_dict(data, ctx["form"].cleaned_data["mode"], ctx["form"].cleaned_data["user_mode"])
            return redirect(new.get_absolute_url())
        except RuntimeError as e:
            # Any error? Add it as an error and then show the form again
            ctx["import_error"] = "Sorry, that failed to import, the error was: {}".format(e)
            return render(request, "export/import.html", ctx)
