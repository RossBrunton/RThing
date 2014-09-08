"""Utility functions for the tasks app"""
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.cache import cache

from tasks.templatetags import fragments
from courses.models import get_iface

import random

# This is used to seperate the user output from the hidden output; it is inserted via a generic_print after code, and
# all output after it will be hidden from the user
# This really isn't the best way of doing this, but I can't think up any other way
_SPLIT_TOKEN = "QPZMWOXN_SPLIT_TOKEN_QPZMWOXN"

def perform_execute(code, task, user):
    """Executes provided code (a string) and the model answer and returns (output, media, is_error, is_correct)
    
    It compares it to the model answer, that's what is_correct means.
    
    is_correct will always be false if the task has automark set to false.
    
    This will try to do as little work as possible by storing the model answer in a cache, and by trying is_equivilant
    on the interface.
    """
    # Encode it to ascii to get rid of unicode chars
    code = code.encode("ascii", "ignore").decode("ascii")
    
    # Strip whitespace from both ends
    code = code.strip()
    
    # Ensure the code ends with ";" or whatever
    if not code.endswith(task.iface.LINE_END):
        code += task.iface.LINE_END
    
    # First, check to see if they are equivalent and the answer exists
    # if the task cannot be automarked, equiv is always false
    equiv = task.iface.is_equivalent(task.model_answer, code) and task.automark
    
    # Look up prior
    prior = ""
    if task.takes_prior and task.previous():
        prior = task.previous().as_prior() + task.iface.generic_print(_SPLIT_TOKEN)
    
    # Generate a seed if needed
    seed = 0
    if task.random_poison():
        seed = random.randint(0, 1 << 30)
    
    if task.takes_prior and task.previous():
        seed = task.previous().prior_seed(user)
    
    # Run the user's code, only if the lines of code are not equivalent
    if not equiv:
        user_code = "".join(filter(lambda x: bool(x), [
            prior,
            task.hidden_pre_code,
            task.visible_pre_code,
            code,
            task.iface.generic_print(_SPLIT_TOKEN),
            task.validate_answer,
            task.post_code
        ])).strip()
        
        user_input = {
            "commands":user_code, "namespace":task.lesson.pk, "uses_random":task.random_poison(),
            "uses_image":task.uses_image, "automark":task.automark, "seed":seed, "user":user.pk
        }
        user_output = task.iface.run(user_input)
        
        if user_output["is_error"]:
            # If the output has an error, assume it's wrong
            return (
                user_output["err"],
                None,
                True,
                False
            )
    
    
    # Run the model answer, but only if an answer exists
    if task.automark:
        # Check the cache for a model answer
        cache_value = None
        if not task.random_poison():
            cache_value = cache.get("task_model_{}".format(task.pk))
        
        if not cache_value:
            # Miss
            model_code = "".join(filter(lambda x: bool(x), [
                prior,
                task.hidden_pre_code,
                task.visible_pre_code,
                task.model_answer,
                task.iface.generic_print(_SPLIT_TOKEN),
                task.validate_answer,
                task.post_code
            ])).strip()
            
            model_input = {
                "commands":model_code, "namespace":task.lesson.pk, "uses_random":task.random_poison(),
                "uses_image":task.uses_image, "automark":task.automark, "seed":seed, "user":user.pk, "model":True
            }
            model_output = task.iface.run(model_input)
            
            if not task.random_poison():
                cache.set("task_model_{}".format(task.pk), model_output)
        else:
            # Hit
            model_output = cache_value
        
        # If the answers are equivalent, then set the users output to the models output
        if equiv:
            user_output = model_output
    
    # Strip all lines after the split token
    displayed_output = ""
    range_end = 0
    range_start = 0
    
    lines = user_output["out"].split("\n")
    for l in range(len(lines)-1, -1, -1):
        # Loop backwards until we find the token, to see what range of lines we should output
        
        # This is for takes_prior (takes_prior injects another split token before the command) for the start of range
        if range_end and _SPLIT_TOKEN in lines[l]:
            range_start = -len(lines)+l+1
            break
        
        # And this is for the end of the range, to delete post_code and validate_answer
        if _SPLIT_TOKEN in lines[l]:
            range_end = -len(lines)+l
            if not task.takes_prior:
                break
    
    displayed_output = "\n".join(lines[range_start:range_end])
    
    # Store the seed
    if seed:
        uot = task.get_uot(user)
        uot.seed = seed
        uot.save()
    
    # And return
    return (
        displayed_output,
        user_output.get("media", None),
        False,
        equiv or (
            task.automark
            and user_output["out"] == model_output["out"]
            and user_output.get("media", None) == model_output.get("media", None)
        )
    )


def validate_execute(task, instance):
    """Executes the model answer treating the task as if it were a dict and returns (is_error, error)
    
    This is used when validating the contents of the model when saving it.
    """
    # If prior is true this method doesn't seem to work
    if task["takes_prior"]:
        return (False, "")
    
    # Look up prior
    prior = ""
    if task["takes_prior"] and instance.previous():
        prior = instance.previous().as_prior() + get_iface(task["language"]).generic_print(_SPLIT_TOKEN)
    
    # Generate a seed
    seed = random.randint(0, 1 << 30)
    
    # Run the model answer
    model_code = "".join(filter(lambda x: bool(x), [
        prior,
        task["hidden_pre_code"],
        task["visible_pre_code"],
        task["model_answer"],
        task["validate_answer"],
        task["post_code"]
    ])).strip()
    
    model_input = {
        "commands":model_code, "namespace":task["section"].lesson.pk, "uses_random":True,
        "uses_image":task["uses_image"], "automark":task["automark"], "seed":seed, "user":0
    }
    model_output = get_iface(task["language"]).run(model_input)
    
    if model_output["is_error"]:
        return (True, model_output["err"])
    
    # And return
    return (False, "")


def fragmentate(type, obj, request, content_select=None, content_value=None):
    """Generates a fragment for the given type and returns it as a python dict
    
    See doc/task_submit_interface.md for details.
    """
    frag = {"type":type}
    
    if type == "task":
        frag["id"] = obj.pk
        frag["order"] = "{}-{}".format(obj.section.order, obj.order)
        frag["html"] = render_to_string("tasks/task.html", fragments.task(obj))
        return frag
    
    if type == "task-content":
        frag["id"] = obj.pk
        frag["select"] = content_select
        frag["html"] = content_value
        return frag
    
    if type == "lesson-start":
        frag["html"] = render_to_string("tasks/lesson_start.html", fragments.lesson_start(obj))
        return frag
    
    if type == "lesson-end":
        frag["html"] = render_to_string("tasks/lesson_end.html", fragments.lesson_end(obj))
        return frag
    
    if type == "section-start":
        frag["order"] = obj.order
        frag["html"] = render_to_string("tasks/section_start.html", fragments.section_start(obj, request.user.is_staff))
        return frag
    
    if type == "section-end":
        frag["order"] = obj.order
        frag["html"] = render_to_string("tasks/section_end.html", fragments.section_end(obj))
        return frag
    
    if type == "prompt-entry":
        frag["id"] = obj.pk
        frag["html"] = render_to_string("tasks/prompt_entry.html", fragments.prompt_entry(obj))
        return frag
    
    raise RuntimeError("{} is not a fragment type".format(type))
