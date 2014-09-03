"""Views for the root urls

This contains only one view for handling "/".
"""
from django.shortcuts import redirect

from courses.views import index as course_list

def index(request):
    """Redirects to courses:index"""
    return redirect("courses:index", permanent=True)
