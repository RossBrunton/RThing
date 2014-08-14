from django.template.loader import render_to_string
from django.template import RequestContext

from tasks.templatetags import fragments

# This is used to seperate the user output from the hidden output; it is inserted via a generic_print after code, and
# all output after it will be hidden from the user
# This really isn't the best way of doing this, but I can't think up any other way
_SPLIT_TOKEN = "QPZMWOXN_SPLIT_TOKEN_QPZMWOXN"

def perform_execute(code, task, user):
    """Executes code (or reads it from a cache) and returns (output, media, is_error, is_correct)
    
    is_correct will always be false if the task has automark set to false.
    """
    # First, check to see if they are equivalent and the answer exists
    equiv = False
    if task.iface.is_equivalent(task.model_answer, code) and task.automark:
        equiv = True
    
    # Run the user's code, only if the lines of code are not equivalent
    if not equiv:
        userCode = "\n".join([
            task.hidden_pre_code,
            task.visible_pre_code,
            code,
            task.iface.generic_print(_SPLIT_TOKEN),
            task.validate_answer,
            task.post_code
        ]).strip()
        
        userInput = {
            "commands":userCode, "namespace":task.section.lesson.pk, "uses_random":task.uses_random,
            "uses_image":task.uses_image, "automark":task.automark
        }
        userOutput = task.iface.run(userInput)
        
        if userOutput["is_error"]:
            # If the output has an error, assume it's wrong
            return (
                userOutput["err"],
                None,
                True,
                False
            )
    
    
    # Run the model answer, but only if an answer exists
    if task.automark:
        modelCode = "\n".join([
            task.hidden_pre_code,
            task.visible_pre_code,
            task.model_answer,
            task.iface.generic_print(_SPLIT_TOKEN),
            task.validate_answer,
            task.post_code
        ]).strip()
        
        modelInput = {
            "commands":modelCode, "namespace":task.section.lesson.pk, "uses_random":task.uses_random,
            "uses_image":task.uses_image, "automark":task.automark
        }
        modelOutput = task.iface.run(modelInput)
        # If the answers are equivalent, then set the users output to the models output
        if equiv:
            userOutput = modelOutput
    
    # Strip all lines after the split token
    displayedOutput = ""
    lines = userOutput["out"].split("\n")
    for l in range(len(lines)-1, -1, -1):
        # Loop backwards, when we find the token, claim every line before this one as the output
        if _SPLIT_TOKEN in lines[l]:
            displayedOutput = "\n".join(lines[:-len(lines)+l])
            break
    
    # And return
    return (
        displayedOutput,
        userOutput.get("media", None),
        False,
        equiv or (task.automark and userOutput["out"] == modelOutput["out"])
    )


def fragmentate(type, obj, request, content_select=None, content_value=None):
    """Generates a fragment for the given type and returns it as a python dict"""
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
