from django.conf.urls import patterns, include, url
from django.contrib.auth.views import\
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete

import users.views as views

urlpatterns = patterns('',
    url(r"^login$", views.login, name="login"),
    url(r"^logout$", views.logout, name="logout"),
    url(r"^edit$", views.edit, name="edit"),
    url(r"^success$", views.password_changed, name="password_changed"),
    
    url(r"^reset$", password_reset,\
        {'template_name': "users/reset.html", "post_reset_redirect":"/users/resetDone",\
        "email_template_name":"users/reset_email.txt"},
    name="reset"),
    url(r"^resetDone$", password_reset_done, {'template_name': "users/reset_done.html"}, name="resetDone"),
    url(r"^resetConfirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)$", password_reset_confirm,\
        {'template_name': "users/reset_confirm.html", "post_reset_redirect":"/users/resetComplete"},name="resetConfirm"\
    ),
    url(r"^resetComplete$", password_reset_complete, {'template_name': "users/reset_complete.html"},
        name="resetComplete",
    )
)
