from django.urls import re_path
from meiduo_admin.views import users, skus, statistical

urlpatterns = [
    re_path(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
    re_path(r'statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    re_path(r'statistical/day_orders/$', statistical.UserDayOrderView.as_view()),
    re_path(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    re_path(r'^users/$', users.UserInfoView.as_view()),
]

# 图片管理
from rest_framework.routers import SimpleRouter
router = SimpleRouter()
router.register('skus/images', skus.SKUImageViewSet, basename='images')
urlpatterns += router.urls
