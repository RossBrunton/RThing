from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.core.context_processors import csrf
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.template import RequestContext

from courses.models import Task

from tasks.templatetags import fragments

import json
import time

def perform_execute(code, task, user):
    """Executes code (possibly using a cache) and returns (output, media, isError, isCorrect)"""
    return (code, None, False, True)

def fragmentate(type, obj, request):
    """Generates a fragment for the given type and object as a python dict"""
    frag = {"type":type}
    
    if type == "task":
        frag["id"] = obj.pk
        frag["order"] = "{}-{}".format(obj.section.order, obj.order)
        frag["html"] = render_to_string("tasks/task.html", fragments.task(obj))
    
    if type == "lesson-start":
        frag["html"] = render_to_string("tasks/lesson_start.html", fragments.lesson_start(obj))
    
    if type == "lesson-end":
        frag["html"] = render_to_string("tasks/lesson_end.html", fragments.lesson_end(obj))
    
    if type == "section-start":
        frag["order"] = obj.order
        frag["html"] = render_to_string("tasks/section_start.html", fragments.section_start(obj))
    
    if type == "section-end":
        frag["order"] = obj.order
        frag["html"] = render_to_string("tasks/section_end.html", fragments.section_end(obj))
    
    if type == "prompt-entry":
        frag["id"] = obj.pk
        frag["html"] = render_to_string("tasks/prompt_entry.html", fragments.prompt_entry(obj))
    
    return frag


@login_required
@require_POST
def submit(request, task):
    data = {}
    
    task = get_object_or_404(Task, pk=task)
    if not task.can_see(request.user):
        raise Http404
    
    if "code" not in request.POST:
        raise SuspiciousOperation
    
    # Run the code
    output, media, isError, isCorrect = perform_execute(request.POST["code"], task, request.user)
    
    # Set output
    data["output"] = output
    data["isError"] = isError
    data["isCorrect"] = isCorrect
    data["frags"] = [fragmentate("prompt-entry", task, request)]
    
    # If they were correct load the next task or section
    if isCorrect:
        n = task.next()
        if n:
            data["frags"].append(fragmentate("task", n, request))
        else:
            data["frags"].append(fragmentate("section-end", task.section, request))
            new_sect = task.section.next()
            if new_sect:
                data["frags"].append(fragmentate("section-start", new_sect, request))
                data["frags"].append(fragmentate("task", new_sect.tasks.all()[0], request))
            else:
                data["frags"].append(fragmentate("lesson-end", task.section.lesson, request))
    
    return HttpResponse(json.dumps(data), content_type="application/json")
