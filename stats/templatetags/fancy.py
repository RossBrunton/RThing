""" Fancy formatting for numbers

All functions format a number given a value and a maximum. The class of the generated span element is given by:
if value < (maximum * 0.33) then the class is "bad"
if value > (maximum * 0.67) then the value is "good"
else it is "okay"

There are also _low versions of the functions, which swap "good" and "bad" such that a lower value has the class "good".
"""

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from decimal import Decimal

import re

register = template.Library()

def _get_class(value, max):
    if value < (max * 0.33): return "bad"
    if value > (max * 0.67): return "good"
    return "okay"

def _get_class_low(value, max):
    if value < (max * 0.33): return "bad"
    if value > (max * 0.67): return "good"
    return "okay"

@register.filter(needs_autoescape=True)
def fancy(value, arg=None, autoescape=None):
    """Takes an integer value and a maximum and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{}</span>".format(_get_class(value, arg), value))


@register.filter(needs_autoescape=True)
def fancy_float(value, arg=None, autoescape=None):
    """Takes a float value and a maximum and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{:.2f}</span>".format(_get_class(value, arg), value))


@register.filter(needs_autoescape=True)
def fancy_percent(value, arg=None, autoescape=None):
    """Takes a float value from 0.0 to 1.0 and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{:.2%}</span>".format(_get_class(value, 1), value))


@register.filter(needs_autoescape=True)
def fancy_low(value, arg=None, autoescape=None):
    """Takes an integer value and a maximum and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{}</span>".format(_get_class_low(value, arg), value))


@register.filter(needs_autoescape=True)
def fancy_float_low(value, arg=None, autoescape=None):
    """Takes a float value and a maximum and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{:.2f}</span>".format(_get_class_low(value, arg), value))


@register.filter(needs_autoescape=True)
def fancy_percent_low(value, arg=None, autoescape=None):
    """Takes a float value from 0.0 to 1.0 and wraps it in a span with the appropriate class"""
    return mark_safe("<span class='fancy {}'>{:.2%}</span>".format(_get_class_low(value, 1), value))
