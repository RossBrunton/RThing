from django.contrib.auth.backends import RemoteUserBackend

from django.conf import settings

class CustomRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False
    
    clean_username = settings.CLEAN_REMOTE

class Test:
    def process_request(self, request):
        request.META["REMOTE_USER"] = "test"
