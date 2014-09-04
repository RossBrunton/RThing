"""Tags for fragments

See doc/task_submit_interface.md for details
"""
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag("tasks/task.html")
def task(task, **kwargs):
    """Handles the "task" fragment
    
    Creates the keyword arg "multiline" as a boolean for whether the model answer has multiple lines and "pre_lines" as
    a list of lines for the visible_pre_code.
    """
    kwargs["task"] = task
    kwargs["multiline"] = "\n" in task.model_answer
    kwargs["pre_lines"] = task.visible_pre_code.split("\n")
    
    return kwargs

@register.inclusion_tag("tasks/prompt_entry.html")
def prompt_entry(task, **kwargs):
    """Handles the "prompt-entry" fragment"""
    kwargs["task"] = task
    
    return kwargs

@register.inclusion_tag("tasks/lesson_start.html")
def lesson_start(lesson, **kwargs):
    """Handles the "lesson-start" fragment"""
    kwargs["lesson"] = lesson
    return kwargs

@register.inclusion_tag("tasks/lesson_end.html")
def lesson_end(lesson, **kwargs):
    """Handles the "lesson-end" fragment"""
    kwargs["lesson"] = lesson
    return kwargs

@register.inclusion_tag("tasks/section_start.html")
def section_start(section, staff, **kwargs):
    """Handles the "section-start" fragment"""
    kwargs["section"] = section
    kwargs["staff"] = staff
    return kwargs

@register.inclusion_tag("tasks/section_end.html")
def section_end(section, **kwargs):
    """Handles the "section-end" fragment"""
    kwargs["section"] = section
    return kwargs
