from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy, ugettext as _

class StaffAdminSite(admin.sites.AdminSite):
    def __init__(self, *args, **kwargs):
        super(StaffAdminSite, self).__init__(*args, **kwargs)
        
        site_title = ugettext_lazy("Rthing Administration")
        site_header = ugettext_lazy("Rthing Administration")


admin_site = StaffAdminSite()

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
