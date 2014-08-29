from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy, ugettext as _

class StaffAdminSite(admin.sites.AdminSite):
    def __init__(self, *args, **kwargs):
        super(StaffAdminSite, self).__init__(*args, **kwargs)
        
        self.site_title = "Rthing Administration"
        self.site_header = "Rthing Administration"


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin_site = StaffAdminSite()

admin_site.register(User, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)
