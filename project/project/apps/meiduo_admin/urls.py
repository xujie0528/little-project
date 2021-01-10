from django.urls import re_path
from meiduo_admin.views import users

urlpatterns = [
    re_path(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
]