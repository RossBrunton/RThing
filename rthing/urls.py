from django.conf.urls import patterns, include, url
from django.contrib import admin

from courses.urls import urlpatterns as courses
from users.urls import urlpatterns as users
import rthing.views as views

admin.autodiscover()

urlpatterns = patterns("",
    url(r"^/?$", views.index, {}),
     
    url(r"^admin/", include(admin.site.urls)),
    url(r"^courses/", include(courses)),
    url(r"^users/", include(users)),
)
