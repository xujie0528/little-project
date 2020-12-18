from django.urls import re_path
from users import views

urlpatterns = [
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9]_-{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view())
]