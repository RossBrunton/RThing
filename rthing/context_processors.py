"""Context processors, these get called and add things to template contexts"""
from django.conf import settings

def footer_putter(request):
    """Adds the "footer" property to the context, this is equal to settings.FOOTER"""
    return {"footer":settings.FOOTER}
