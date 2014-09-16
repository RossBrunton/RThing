"""Contains the admin site"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy, ugettext as _

class StaffAdminSite(admin.sites.AdminSite):
    """The admin site used for the system"""
    def __init__(self, *args, **kwargs):
        """Sets site_title and site_header to "Administration", which does nothing in Django 1.6"""
        super(StaffAdminSite, self).__init__(*args, **kwargs)
        
        self.site_title = "Administration"
        self.site_header = "Administration"


class CustomUserAdmin(UserAdmin):
    """Subclass of UserAdmin, which removes some fields I'm not using, like the first name and last name"""
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

"""The instance of the admin site that is to be used"""
admin_site = StaffAdminSite()

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)
