from django.template.loader import render_to_string
from django.template import RequestContext

from tasks.templatetags import fragments

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
