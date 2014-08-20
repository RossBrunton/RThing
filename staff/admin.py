from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission

class StaffAdminSite(admin.sites.AdminSite):
    site_title = "Rthing Administration"
    site_header = "Rthing Administration"


admin_site = StaffAdminSite()

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
