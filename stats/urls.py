from django.conf.urls import patterns, include, url

import stats.views as views

urlpatterns = patterns('',
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)$", views.lesson, name="lesson"),
    url(r"^~wrong/(?P<task>[0-9]+)$", views.wrong, name="wrong"),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)/user/(?P<name>[0-9a-zA-Z_@.+-]+)$", views.user, name="user"),
)
