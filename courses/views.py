from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "courses/index.html", {})

def course(request, course):
    ...

def lesson(request, course, lesson):
    ...
