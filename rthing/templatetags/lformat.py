from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

import re

register = template.Library()

@register.filter(needs_autoescape=True)
def lformat(value, arg=None, autoescape=None):
    """Formatting lecturers text and such"""
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    value = esc(value)
    
    # New lines
    value = value.replace("\r", "")
    value = value.replace("\n\n", "</div><div>")
    
    # Boxes
    value = re.sub(r"\<div\>[Ww]arning:(.+?)\<\/div\>", r"<div class='l-warning'>\1</div>", value)
    value = re.sub(r"\<div\>[Nn]ote:(.+?)\<\/div\>", r"<div class='l-note'>\1</div>", value)
    value = re.sub(r"\<div\>[Ii]nfo:(.+?)\<\/div\>", r"<div class='l-info'>\1</div>", value)
    
    # Click transfer thing
    value = re.sub(r"(\s)\#(.+?)\#", r"\1<span class='l-click'>\2</span>", value)
    
    return mark_safe("<div>{}</div>".format(value))
