from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from courses.models import Lesson
import settings

import re

register = template.Library()

@register.filter(needs_autoescape=True)
def lformat(value, arg=None, autoescape=None):
    """Formatting lecturer's text and such
    
    Arg should be the lesson's PK if it exists.
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    value = esc(value)
    
    # New lines
    value = value.replace("\r", u"")
    value = value.replace("\n\n", u"</div><div>")
    
    value = u"<div>{}</div>".format(value)
    
    # Images
    def image_repl(match):
        if match.group(2) is not None:
            # Has a protocol
            return mark_safe(
                "<img src='{}{}' alt='{}'>".format(esc(match.group(2)), esc(match.group(3)), esc(match.group(1)))
            )
        
        if arg is None:
            return "(Image cannot be used in a non-lesson context unless it has a protocol (http://))"
        
        return mark_safe(
            "<img src='{}{}/{}' alt='{}'>".format(settings.MEDIA_URL, arg, esc(match.group(3)), esc(match.group(1)))
        )
    
    value = re.sub("\[img\s*(.*?)\](.*?//)?(.*)\[/img\]", image_repl, value)
    
    # Boxes
    value = re.sub(r"\<div\>[Ww]arning:(.+?)\<\/div\>", r"<div class='l-warning'>\1</div>", value)
    value = re.sub(r"\<div\>[Nn]ote:(.+?)\<\/div\>", r"<div class='l-note'>\1</div>", value)
    value = re.sub(r"\<div\>[Ii]nfo:(.+?)\<\/div\>", r"<div class='l-info'>\1</div>", value)
    
    # Click transfer thing
    value = re.sub(r"(\s)\#(.+?)\#", r"\1<span class='l-click'>\2</span>", value)
    
    return mark_safe(value)
