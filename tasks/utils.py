from django.template.loader import render_to_string
from django.template import RequestContext

from tasks.templatetags import fragments

# This is used to seperate the user output from the hidden output; it is inserted via a generic_print after code, and
# all output after it will be hidden from the user
# This really isn't the best way of doing this, but I can't think up any other way
SPLIT_TOKEN = "QPZMWOXN_SPLIT_TOKEN_QPZMWOXN"

def perform_execute(code, task, user):
    """Executes code (possibly using a cache) and returns (output, media, isError, isCorrect)"""
    
    code = "\n".join([
        task.hidden_pre_code,
        task.visible_pre_code,
        code,
        task.iface.generic_print(SPLIT_TOKEN),
        task.validate_answer,
        task.post_code
    ]).strip()
    
    
    input = {
        "commands":code, "namespace":task.pk, "uses_random":task.uses_random, "uses_image":task.uses_image,
        "answer_exists":task.answer_exists
    }
    
    output = task.iface.exec(input)
    
    return (
        output["out"] if not output["is_error"] else output["err"],
        output.get("media", None),
        output["is_error"],
        True
    )

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
