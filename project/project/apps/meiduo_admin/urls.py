from django.urls import re_path

from meiduo_admin.views import users, skus, statistical, permissions
urlpatterns = [
    re_path(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
    re_path(r'statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    re_path(r'statistical/day_orders/$', statistical.UserDayOrderView.as_view()),
    re_path(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    re_path(r'^users/$', users.UserInfoView.as_view()),
    re_path(r'^skus/simple/$', skus.SKUSimpleView.as_view()),
    re_path(r'^permission/content_types/$', permissions.PermissionViewSet.as_view({
        'get': 'content_types'
    })),
]

# 图片管理
from rest_framework.routers import SimpleRouter
router = SimpleRouter()
router.register('skus/images', skus.SKUImageViewSet, basename='images')
urlpatterns += router.urls

router = SimpleRouter()
router.register('permission/perms', permissions.PermissionViewSet, basename='perms')
urlpatterns += router.urls
