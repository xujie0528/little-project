from django.urls import re_path
from payment import views


urlpatterns = [
    re_path(r'^payment/(?P<order_id>\d+)/$', views.PaymentURLView.as_view()),
    re_path(r'^payment/status/$', views.PaymentStatusView.as_view()),
]