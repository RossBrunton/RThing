from django.conf.urls import patterns, include, url

import tasks.views as views

urlpatterns = patterns('',
    url(r"^(?P<task>[0-9]+)/submit$", views.lesson, name="submit"),
)
