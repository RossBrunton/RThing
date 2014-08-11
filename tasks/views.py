from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST

from courses.models import Task

from tasks import utils

import json
import time

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
    output, media, isError, isCorrect = utils.perform_execute(request.POST["code"], task, request.user)
    
    # Set output
    data["output"] = output
    data["isError"] = isError
    data["isCorrect"] = isCorrect
    data["frags"] = [utils.fragmentate("prompt-entry", task, request)]
    
    # Custom fragments
    if task.answer_exists:
        if isCorrect:
            data["frags"].append(utils.fragmentate("task-content", task, request, ".after-text", task.after_text))
        else:
            data["frags"].append(utils.fragmentate("task-content", task, request, ".wrong-text", task.wrong_text))
    
    
    # If they were correct load the next task or section
    if isCorrect:
        n = task.next()
        if n:
            data["frags"].append(utils.fragmentate("task", n, request))
        else:
            data["frags"].append(utils.fragmentate("section-end", task.section, request))
            new_sect = task.section.next()
            if new_sect:
                data["frags"].append(utils.fragmentate("section-start", new_sect, request))
                data["frags"].append(utils.fragmentate("task", new_sect.tasks.all()[0], request))
            else:
                data["frags"].append(utils.fragmentate("lesson-end", task.section.lesson, request))
    
    return HttpResponse(json.dumps(data), content_type="application/json")
