from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import F

from courses.models import Task
from tasks import utils
from stats.models import UserOnTask
from django.conf import settings
from rthing.templatetags.lformat import lformat

import json
import time
import datetime

@login_required
@require_POST
def submit(request, task):
    """Takes a task and executes it
    
    See doc/task_submit_interface.md for details on the interface.
    """
    def create_error(reason):
        """Creates a simple return value representing an error"""
        return HttpResponse(json.dumps(
            {"output":reason, "isError":True, "isCorrect":False, "revealed":False,
            "frags":[utils.fragmentate("prompt-entry", task, request)]}
        ), content_type="application/json")
    
    data = {}
    
    task = get_object_or_404(Task, pk=task)
    if not task.can_see(request.user):
        raise Http404
    
    if "code" not in request.POST:
        raise SuspiciousOperation
    
    mode = request.POST.get("mode", "answered")
    if mode not in ["skipped", "revealed", "answered"]:
        mode = "answered"
    
    # Users cannot submit the scripts faster than one a second if they are not staff
    if request.user.extra.last_script_time + datetime.timedelta(milliseconds=1000) > datetime.datetime.now():
        if not request.user.is_staff:
            return create_error("You are running scripts too fast!")
    
    # Users also can't submit an empty string
    if not len(request.POST["code"]) and mode == "answered":
        return create_error("You didn't submit anything.")
    
    # Or a string that is too long
    if len(request.POST["code"]) > 1000:
        return create_error("That script is too long.")
    
    # Or the same script twice if the task has no random elements
    #if task.iface.is_equivalent(request.user.extra.last_script_code, request.POST["code"])\
    #and mode == "answered" and not task.uses_random and request.user.extra.last_task == task:
    #    return HttpResponse(json.dumps(
    #        {
    #            "output":request.user.extra.last_script_output,
    #            "isError":request.user.extra.last_script_error,
    #            "isCorrect":False,
    #            "revealed":False,
    #            "frags":[utils.fragmentate("prompt-entry", task, request)],
    #            "media":request.user.extra.last_script_media
    #        }
    #    ), content_type="application/json")
    
    # Run the code
    if mode == "answered":
        output, media, isError, isCorrect = utils.perform_execute(request.POST["code"], task, request.user)
        
        data["output"] = output
        data["media"] = media
        data["isError"] = isError
        data["isCorrect"] = isCorrect
        data["revealed"] = False
    elif mode == "skipped":
        if task.automark:
            data["output"] = "[skipped]"
        else:
            data["output"] = "[continued]"
        data["isError"] = False
        data["isCorrect"] = False
        data["revealed"] = False
    elif mode == "revealed":
        if task.lesson.answers_published:
            data["output"] = task.model_answer
        else:
            data["output"] = "Stop that"
        data["isError"] = False
        data["isCorrect"] = False
        data["revealed"] = True
    
    # Set the last script values
    request.user.extra.last_script_code = request.POST["code"]
    request.user.extra.last_script_output = data["output"]
    request.user.extra.last_script_error = data["isError"]
    request.user.extra.last_script_time = datetime.datetime.now()
    request.user.extra.last_task = task
    request.user.extra.save()
    
    # Give the client another entry if enabled
    if (not data["isCorrect"] and mode == "answered") or not settings.ANSWER_LOCK:
        data["frags"] = [utils.fragmentate("prompt-entry", task, request)]
    else:
        data["frags"] = []
    
    # Custom fragments
    if task.automark and mode != "revealed":
        if mode == "skipped":
            if task.skip_text:
                data["frags"].append(
                    utils.fragmentate("task-content", task, request, ".skip-text", lformat(task.skip_text, task.lesson))
                )
        elif not isCorrect:
            if task.wrong_text:
                data["frags"].append(
                    utils.fragmentate(
                        "task-content", task, request, ".wrong-text", lformat(task.wrong_text, task.lesson)
                    )
                )
            else:
                data["frags"].append(
                    utils.fragmentate("task-content", task, request, ".wrong-text",
                        "Sorry, that is incorrect. Please try again"
                    )
                )
    
    
    # If they were correct (or skipped) then load the next task or section
    if mode == "skipped" or mode == "revealed" or isCorrect:
        data["frags"].append(
            utils.fragmentate("task-content", task, request, ".after-text", lformat(task.after_text, task.lesson))
        )
        
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
                data["frags"].append(utils.fragmentate("lesson-end", task.lesson, request))
    
    
    # Store statistics on the user
    uot = UserOnTask.objects.get_or_create(user=request.user, task=task)[0]
    if mode in ["answered", "revealed"] and not request.user.is_staff:
        
        if uot.state == UserOnTask.STATE_NONE:
            # Only set state if the user has no state
            if mode == "answered" and isCorrect:
                uot.tries += 1
                uot.state = UserOnTask.STATE_CORRECT
            elif mode == "answered":
                uot.tries += 1
                uot.add_wrong_answer(request.POST["code"])
            elif mode == "revealed":
                uot.state = UserOnTask.STATE_REVEALED
    
    if mode == "skipped":
        uot.skipped = True
    
    uot.save()
    
    return HttpResponse(json.dumps(data), content_type="application/json")
