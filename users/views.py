"""View functions for users app"""
from django.contrib.auth import logout as alogout, login as alogin, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.db.transaction import atomic

from django.conf import settings

def login(request):
    """Handles a log in request
    
    This will accept either "GET" (in which case it displays a form) or "POST" (in which case it tries to log in the
    user). If the user is logged in succesfully, they are redirected to the value of the get var "next" or to "/".
    
    The template used to display the login prompt is users/login.html, the template used when rendering a failed
    REMOTE_USER login is users/denied.html.
    """
    if request.user.is_authenticated():
        # User is already logged in; redirect them somewhere else
        return redirect(request.GET.get("next", "/"))
    
    if request.method == "POST":
        # User has submitted credentials
        form = AuthenticationForm(request, data=request.POST)
        
        user = None
        if form.is_valid():
            # Validate form and if it is valid set the user and log them in
            alogin(request, form.get_user())
            user = form.get_user()
        
        if user is None:
            # But it is invalid
            return render(request, "users/login.html", {"form":form})
        
        # Logged the user in, now go where they wanted to go
        return redirect(request.GET.get("next", "/"))
    else:
        # User did not submit credentials, use a template based on whether we are using remote user auth
        if settings.USE_REMOTE_USER:
            return render(request, "users/denied.html", {"message":settings.REMOTE_DENIED_MESSAGE})
        else:
            return render(request, "users/login.html", {"form":AuthenticationForm(request)})
    

@require_POST
@login_required
def logout(request):
    """Logs out the user and displays a goodbye message
    
    It uses the template users/goodbye.html.
    """
    alogout(request)
    return render(request, "users/goodbye.html", {})


@login_required
def password_changed(request):
    """The user is redirected here when their password is changed, which displays a simple message with a link.
    
    Uses the template users/password_changed.html
    """
    return render(request, "users/password_changed.html", {})


@login_required
def edit(request):
    """Edits the user's password
    
    Accepts GET or POST which will make a form or try to change the password, respectively. If the change was sucessfull
    they are redirected to users:password_changed.
    
    The template used is users/edit.html.
    """
    if request.method == "GET":
        return render(request, "users/edit.html",
            {"form":PasswordChangeForm(request.user), "area":"users", "forced":request.GET.get("forced", False)}
        )
    
    elif request.method == "POST":
        with atomic():
            f = PasswordChangeForm(request.user, request.POST)
            
            if not f.is_valid():
                return render(request, "users/edit.html", {"form":f})
        
            f.save()
            
            request.user.extra.password_forced = False
            request.user.extra.save()
    
    return redirect("users:password_changed")
