from django.urls import re_path
from meiduo_admin.views import users
from  meiduo_admin.views import statistical

urlpatterns = [
    re_path(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
    re_path(r'statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    re_path(r'statistical/day_orders/$', statistical.UserDayOrderView.as_view()),
    re_path(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    re_path(r'^users/$', users.UserInfoView.as_view()),
]