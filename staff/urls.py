from django.conf.urls import patterns, include, url

import staff.views as views

urlpatterns = patterns('',
    url(r"^/?$", views.index, name="index"),
    url(r"^(?P<course>[a-z0-9-]+)/add_users$", views.add_users, name="add_users"),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)/files$", views.files, name="files"),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)/delete-file$", views.delete, name="delete"),
    url(r"~strain/(?P<task>[0-9]+)$", views.strain, name="strain"),
)
