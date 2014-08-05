from django.conf.urls import patterns, include, url

import courses.views as views

urlpatterns = patterns('',
    url(r"^$", views.index, {}),
    url(r"^(?P<course>[a-z0-9-]+)/$", views.course, {}),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)$", views.lesson, {}),
)
