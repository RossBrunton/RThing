from django.conf.urls import patterns, include, url

import stats.views as views

urlpatterns = patterns('',
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)$", views.lesson, name="lesson"),
)
