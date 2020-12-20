from django.db import models
# Create your models here.
from project.utils.base_model import BaseModel
from users.models import User


class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name='地区名称')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL,
                               related_name='subs', null=True,
                               blank=True, verbose_name='父级地区')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '地区'

    def __str__(self):
        return self.name

class Address(BaseModel):
    default_address = models.OneToOneField('Address',
                                           related_name='owner',
                                           null=True,
                                           blank=True,
                                           on_delete=models.SET_NULL,
                                           verbose_name='默认地址')

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')

    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                                 related_name='province_addresses',
                                 verbose_name='省')

    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                             related_name='city_addresses',
                             verbose_name='市')

    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT,
                                 related_name='district_addresses',
                                 verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    phone = models.CharField(max_length=20,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='固定电话')

    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')

    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_addresses'
        verbose_name = '用户地址'
        ordering = ['-update_time']