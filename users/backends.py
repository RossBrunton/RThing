"""Backends for the Django auth plugin thing"""
from django.contrib.auth.backends import RemoteUserBackend

from django.conf import settings

class CustomRemoteUserBackend(RemoteUserBackend):
    """RemoteUserBackend with some changes
    
    create_unknown_user is set to false, and clean_username is set to settings.CLEAN_REMOTE
    """
    create_unknown_user = False
    
    clean_username = settings.CLEAN_REMOTE

class RemoteUserAddMiddleware:
    """For testing, this is middleware that sets the remote user to "test" """
    def process_request(self, request):
        request.META["REMOTE_USER"] = "test"
