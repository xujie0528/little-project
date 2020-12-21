from django.db import models
# Create your models here.


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
