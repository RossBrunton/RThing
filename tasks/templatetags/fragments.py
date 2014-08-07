from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag("tasks/task.html")
def task(task, **kwargs):
    kwargs["task"] = task
    return kwargs

@register.inclusion_tag("tasks/lesson_start.html")
def lesson_start(lesson, **kwargs):
    kwargs["lesson"] = lesson
    return kwargs

@register.inclusion_tag("tasks/lesson_end.html")
def lesson_end(lesson, **kwargs):
    kwargs["lesson"] = lesson
    return kwargs

@register.inclusion_tag("tasks/section_start.html")
def section_start(section, **kwargs):
    kwargs["section"] = section
    return kwargs

@register.inclusion_tag("tasks/section_end.html")
def section_end(section, **kwargs):
    kwargs["section"] = section
    return kwargs
