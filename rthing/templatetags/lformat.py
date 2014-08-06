from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def lformat(value, arg=None, autoescape=None):
    """Formatting lecturers text and such"""
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    value = esc(value)
    
    value = value.replace("\r", "")
    value = value.replace("\n\n", "</div><div>")
    
    return mark_safe("<div>{}</div>".format(value))
