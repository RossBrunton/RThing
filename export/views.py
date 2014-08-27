from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core import serializers

from courses.models import Course, Lesson, Section, Task
from export.parse import encode, decode

from os import path
import settings
import os
#import yaml
#from dicttoxml import dicttoxml
#from xml.dom.minidom import parseString
import json

@login_required
@user_passes_test(lambda u: u.is_staff)
def export(request, course):
    data = get_object_or_404(Course, slug=course).to_dict()
    
    print(decode(encode(data)) == data)
    return HttpResponse(encode(data), "text/plain")

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def import_(request, course):
    pass
