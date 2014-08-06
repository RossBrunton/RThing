from django.conf.urls import patterns, include, url

import users.views as views

urlpatterns = patterns('',
    url(r"^login$", views.login, name="login"),
    url(r"^logout$", views.logout, name="logout"),
)
