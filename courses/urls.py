from django.conf.urls import patterns, include, url

import courses.views as views

urlpatterns = patterns('',
    url(r"^/?$", views.index, name="index"),
    url(r"^(?P<course>[a-z0-9-]+)/$", views.course, name="course"),
    url(r"^(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)$", views.lesson, name="lesson"),
    url(r"^print/(?P<course>[a-z0-9-]+)/(?P<lesson>[a-z0-9-]+)$", views.print_lesson, name="print_lesson"),
)
