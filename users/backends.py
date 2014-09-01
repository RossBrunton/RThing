from django.contrib.auth.backends import RemoteUserBackend

import settings

class CustomRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False
    
    clean_username = settings.CLEAN_REMOTE
