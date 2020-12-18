from django.urls import re_path

from verifications import views

urlpatterns = [
    re_path(r'image_codes/(?P<uuid>[\W-]+)/$', views.ImageCodeView.as_view())
]