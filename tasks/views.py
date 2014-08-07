from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.views.decorators.http import require_POST

@login_required
@require_POST
def submit(request):
    ...
