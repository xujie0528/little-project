from rest_framework import serializers

from goods.models import SKUImage, SKU


class SKUImageSerializer(serializers.ModelSerializer):
    """SKU图片序列化器类"""
    # 关联对象嵌套序列化
    sku = serializers.StringRelatedField(label='SKU商品名称')
    # SKUImage 模型中没有 sku_id 字段，需要自己进行添加
    sku_id = serializers.IntegerField(label='SKU商品ID')

    class Meta:
        model = SKUImage
        exclude = ('create_time', 'update_time')

    def validate_sku_id(self, value):
        """针对 sku_id 进行补充验证"""
        # SKU商品是否存在
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('SKU商品不存在')

        return value

    def create(self, validated_data):
        """上传 SKU 商品图片保存"""
        # 调用 ModelSerializer 中的 create 方法，进行上传文件保存和表记录添加
        sku_image = SKUImage.objects.create(**validated_data)

        # 判断是否需要设置 SKU 商品的默认图片
        sku = sku_image.sku

        if not sku.default_image:
            sku.default_image = sku_image.image.name
            sku.save()

        return sku_image


class SKUSimpleSerializer(serializers.ModelSerializer):
    """SKU商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('id', 'name')