"""Urls for the export system, this should be the namespace "export" """
from django.conf.urls import patterns, include, url

import export.views as views

urlpatterns = patterns('',
    url(r"^(?P<course>[a-z0-9-]+)/export$", views.export, name="export"),
    url(r"^import$", views.import_, name="import"),
)
