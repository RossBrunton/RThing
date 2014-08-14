from django.conf.urls import patterns, include, url

import staff.views as views

urlpatterns = patterns('',
    url(r"^/?$", views.index, name="index"),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)/upload$", views.upload, name="upload"),
)
