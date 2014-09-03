from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static

from courses.urls import urlpatterns as courses
from users.urls import urlpatterns as users
from tasks.urls import urlpatterns as tasks
from staff.urls import urlpatterns as staff
from stats.urls import urlpatterns as stats
from export.urls import urlpatterns as export
import rthing.views as views

from staff.admin import admin_site

from django.conf import settings

admin.autodiscover()

urlpatterns = patterns("",
    url(r"^/?$", views.index, name="index"),
    
    url(r"^admin/", include(admin_site.urls)),
    url(r"^courses/", include(courses, namespace="courses")),
    url(r"^tasks/", include(tasks, namespace="tasks")),
    url(r"^users/", include(users, namespace="users")),
    url(r"^staff/", include(staff, namespace="staff")),
    url(r"^stats/", include(stats, namespace="stats")),
    url(r"^io/", include(export, namespace="export"))
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
