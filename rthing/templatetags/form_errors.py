"""Displays form errors in a nice way"""
from django import template

register = template.Library()

@register.inclusion_tag('form_errors.html')
def form_errors(form):
    """Use the form_errors.html template to render errors in the given form"""
    return {"form":form}

