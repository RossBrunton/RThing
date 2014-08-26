from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.core import serializers

from courses.models import Course, Lesson, Section, Task
from export.parse import from_dict

from os import path
import settings
import os
import yaml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import json

@login_required
@user_passes_test(lambda u: u.is_staff)
def export(request, course):
    data = get_object_or_404(Course, slug=course).to_dict()
    
    #return HttpResponse(json.dumps(data, indent=4), "application/json")
    #return HttpResponse(parseString(dicttoxml(data)).toprettyxml(), "text/xml")
    #return HttpResponse(yaml.dump(data), "text/x-yaml")
    return HttpResponse(from_dict(data), "text/plain")
