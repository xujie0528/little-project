from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User

from meiduo_admin.serializers.permissions import ContentTypeSerializer, GroupSerializer, PermissionSimpleSerializer, \
    AdminSerializer, GroupSimpleSerializer

from meiduo_admin.serializers.permissions import PermissionSerializer


class PermissionViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


    def content_types(self, request):
        """获取权限类型数据"""
        # ① 获取权限类型数据
        content_types = ContentType.objects.all()

        serializer = ContentTypeSerializer(content_types, many=True)
        return Response(serializer.data)


class GroupViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def simple(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSimpleSerializer(permissions, many=True)
        return Response(serializer.data)


class AdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]

    queryset = User.objects.all()
    serializer_class = AdminSerializer

    def simple(self, request):
        groups = Group.objects.all()
        serializer = GroupSimpleSerializer(groups, many=True)
        return Response(serializer.data)

