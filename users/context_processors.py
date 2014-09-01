import settings

def use_remote_checker(request):
    return {"use_remote_user":settings.USE_REMOTE_USER}
