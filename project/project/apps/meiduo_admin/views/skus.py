from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.skus import SKUImageSerializer, SKUSimpleSerializer


class SKUImageViewSet(ModelViewSet):
    # 指定权限, 只有管理员用户才可以访问
    permission_classes = [IsAdminUser]
    # 指定router动态生成路由时, 提取参数的正则表达式
    lookup_value_regex = '\d+'
    # 指定视图所使用的查询集
    queryset = SKUImage.objects.all()

    # 指定视图所使用的序列化器类
    serializer_class = SKUImageSerializer


class SKUSimpleView(ListAPIView):
    # 指定权限：只有管理员用户才能进行访问
    permission_classes = [IsAdminUser]

    # 指定视图所使用的查询集
    queryset = SKU.objects.all()

    # 指定视图所使用的序列化器类
    serializer_class = SKUSimpleSerializer

    # 注：关闭分页
    pagination_class = None

