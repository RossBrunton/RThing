"""Context processors, these get called and add things to template contexts"""
from django.conf import settings

def use_remote_checker(request):
    """Adds the "use_remote_user" property to the context, this is equal to settings.USE_REMOTE_USER"""
    return {"use_remote_user":settings.USE_REMOTE_USER}
