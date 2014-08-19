from django.contrib.auth import logout as alogout, login as alogin, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

def login(request):
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
        # User did not submit credentials
        return render(request, "users/login.html", {"form":AuthenticationForm(request)})
    

@require_POST
@login_required
def logout(request):
    alogout(request)
    return render(request, "users/goodbye.html", {})


@login_required
def password_changed(request):
    return render(request, "users/password_changed.html", {})


@login_required
def edit(request):
    if request.method == "GET":
        return render(request, "users/edit.html", {"form":PasswordChangeForm(request.user), "area":"users"});
    
    elif request.method == "POST":
        f = PasswordChangeForm(request.user, request.POST)
        
        if not f.is_valid():
            return render(request, "users/edit.html", {"form":f});
    
        f.save()
    
    return redirect("users:password_changed")
