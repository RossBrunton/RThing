from django.shortcuts import redirect

from courses.views import index as course_list

def index(request):
    """Homepage redirects to /courses/"""
    redirect(course_list)
