from django.conf.urls import patterns, include, url
from django.contrib import admin
from courses.urls import urlpatterns as courses
from users.urls import urlpatterns as users
from tasks.urls import urlpatterns as tasks
from staff.urls import urlpatterns as staff
import rthing.views as views

from staff.admin import admin_site

admin.autodiscover()

urlpatterns = patterns("",
    url(r"^/?$", views.index, name="index"),
    
    url(r"^admin/", include(admin_site.urls)),
    url(r"^courses/", include(courses, namespace="courses")),
    url(r"^tasks/", include(tasks, namespace="tasks")),
    url(r"^users/", include(users, namespace="users")),
    url(r"^staff/", include(staff, namespace="staff")),
)
