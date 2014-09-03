"""Lecturer formatting tags"""
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from courses.models import Lesson
from django.conf import settings
from six.moves.html_parser import HTMLParser

import re

register = template.Library()

_YOUTUBE_IFRAME = r"""
<iframe width='640' height='385' src='http://www.youtube.com/embed/\1' allowfullscreen
sandbox="allow-scripts allow-same-origin" class='youtube-iframe'
>
</iframe>
"""

def _reverse_escape(match):
    """Undos the escaping"""
    return (HTMLParser()).unescape(match.group(1))


@register.filter(needs_autoescape=True)
def lformat(value, arg=None, autoescape=None, print_=False):
    """Formatting lecturer's text and such
    
    Arg should be the lesson's PK if it exists.
    If the page is on a print view, print_ should be set to true to hide youtube and not make links.
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
    
    value = re.sub(r"\[img\s*(.*?)\](.*?//)?(.*?)\[/img\]", image_repl, value)
    
    # Raw HTML
    value = re.sub(r"\[html\](.*?)\[\/html\]", _reverse_escape, value)
    
    # Youtube
    if print_:
        value = re.sub(r"\[youtube\](.+?)\[\/youtube\]", r"https://www.youtube.com/watch?v=\1", value)
    else:
        value = re.sub(r"\[youtube\](.+?)\[\/youtube\]", _YOUTUBE_IFRAME, value)
    
    # Links
    if print_:
        value = re.sub(r"\[url\](.*?)\[/url\]", r"\1", value)
        value = re.sub(r"\[url\s*(.*?)\](.*?)\[/url\]", r"\2 (\1)", value)
    else:
        value = re.sub(r"\[url\](.*?)\[/url\]", r"<a href='\1'>\1</a>", value)
        value = re.sub(r"\[url\s*(.*?)\](.*?)\[/url\]", r"<a href='\1'>\2</a>", value)
    
    # Boxes
    value = re.sub(r"\<div\>[Ww]arning:(.+?)\<\/div\>", r"<div class='l-warning'>\1</div>", value)
    value = re.sub(r"\<div\>[Nn]ote:(.+?)\<\/div\>", r"<div class='l-note'>\1</div>", value)
    value = re.sub(r"\<div\>[Ii]nfo:(.+?)\<\/div\>", r"<div class='l-info'>\1</div>", value)
    
    # Click transfer thing
    value = re.sub(r"(\s)\#(.+?)\#", r"\1<span class='l-click'>\2</span>", value)
    
    return mark_safe(value)


@register.filter(needs_autoescape=True)
def lformat_print(value, arg=None, autoescape=None):
    """Like lformat, but sets print_ to true"""
    return lformat(value, arg, autoescape, print_=True)
