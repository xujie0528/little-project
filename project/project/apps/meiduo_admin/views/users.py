from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from meiduo_admin.serializers.users import UserSerializer

from meiduo_admin.serializers.users import AdminAuthSerializer


# POST /meiduo_admin/authorizations/
class AdminAuthorizeView(CreateAPIView):
    # 指定当前视图所使用的序列化器类
    serializer_class = AdminAuthSerializer


class UserInfoView(ListAPIView):
    """指定权限, 只有管理员用户可以访问"""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        """普通用户数据查询"""
        # ① 获取keyword关键字
        keyword = self.request.query_params.get('keyword')

        # ② 查询普通用户数据
        if keyword:
            users = User.objects.filter(is_staff=False, username__contains=keyword)
        else:
            users = User.objects.filter(is_staff=False)

        return users