from rest_framework import serializers

from goods.models import SKUImage
class SKUImageSerializer(serializers.ModelSerializer):
    """sku图片序列化器类"""
    # 关联对象嵌套序列化
    sku = serializers.StringRelatedField(label='SKU商品名称')
    # SKUImage模型中没有sku_id字段, 需要自己进行添加
    sku_id = serializers.IntegerField(label='SKU商品ID')

    class Meta:
        model=SKUImage
        exclude = ('create_time', 'update_time')