from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from courses.models import Course

@login_required
def index(request):
    ctx = {}
    ctx["courses"] = Course.get_courses(request.user);
    
    return render(request, "courses/index.html", ctx)

def course(request, course):
    ...

def lesson(request, course, lesson):
    ...
