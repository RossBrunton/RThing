from django.template.loader import render_to_string
from django.template import RequestContext

from tasks.templatetags import fragments

# This is used to seperate the user output from the hidden output; it is inserted via a generic_print after code, and
# all output after it will be hidden from the user
# This really isn't the best way of doing this, but I can't think up any other way
SPLIT_TOKEN = "QPZMWOXN_SPLIT_TOKEN_QPZMWOXN"

def perform_execute(code, task, user):
    """Executes code (possibly using a cache) and returns (output, media, isError, isCorrect)"""
    # First, check to see if they are equivalent and the answer exists
    equiv = False
    if task.iface.is_equivalent(task.model_answer, code) and task.answer_exists:
        equiv = True
    
    # Run the user's code, only if the lines of code are not equivalent
    if not equiv:
        userCode = "\n".join([
            task.hidden_pre_code,
            task.visible_pre_code,
            code,
            task.iface.generic_print(SPLIT_TOKEN),
            task.validate_answer,
            task.post_code
        ]).strip()
        
        userInput = {
            "commands":userCode, "namespace":task.pk, "uses_random":task.uses_random, "uses_image":task.uses_image,
            "answer_exists":task.answer_exists
        }
        userOutput = task.iface.exec(userInput)
        
        if userOutput["is_error"]:
            # If the output has an error, assume it's wrong
            return (
                userOutput["err"],
                None,
                True,
                False
            )
    
    
    # Run the model answer, but only if an answer exists
    if task.answer_exists:
        modelCode = "\n".join([
            task.hidden_pre_code,
            task.visible_pre_code,
            task.model_answer,
            task.iface.generic_print(SPLIT_TOKEN),
            task.validate_answer,
            task.post_code
        ]).strip()
        
        modelInput = {
            "commands":modelCode, "namespace":task.pk, "uses_random":task.uses_random, "uses_image":task.uses_image,
            "answer_exists":task.answer_exists
        }
        modelOutput = task.iface.exec(modelInput)
        # If the answers are equivalent, then set the users output to the models output
        if equiv:
            userOutput = modelOutput
    
    # Strip all lines after the split token
    displayedOutput = ""
    lines = userOutput["out"].split("\n")
    for l in range(len(lines)-1, -1, -1):
        # Loop backwards, when we find the token, claim every line before this one as the output
        if SPLIT_TOKEN in lines[l]:
            displayedOutput = "\n".join(lines[:-len(lines)+l])
            break
    
    # And return
    return (
        displayedOutput,
        userOutput.get("media", None),
        False,
        equiv or (task.answer_exists and userOutput["out"] == modelOutput["out"])
    )


def fragmentate(type, obj, request, content_select=None, content_value=None):
    """Generates a fragment for the given type and object as a python dict"""
    frag = {"type":type}
    
    if type == "task":
        frag["id"] = obj.pk
        frag["order"] = "{}-{}".format(obj.section.order, obj.order)
        frag["html"] = render_to_string("tasks/task.html", fragments.task(obj))
    
    if type == "task-content":
        frag["id"] = obj.pk
        frag["select"] = content_select
        frag["html"] = content_value
    
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
