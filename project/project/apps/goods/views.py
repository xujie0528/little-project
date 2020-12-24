# Create your views here.
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from goods.models import GoodsCategory, SKU
from goods.utils import get_breadcrumb


class HotGoodsView(View):
    def get(self, request, category_id):
        # page = request.GET.get('page', 1)
        # page_size = request.GET.get('page_size', 2)
        ordering = request.GET.get('ordering', '-sales')
        try:
            skus = SKU.objects.filter(category_id=category_id,
                                      is_launched=True).order_by(ordering)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '分类SKU商品数据获取错误'})
        paginator = Paginator(skus, 2)
        skus1 = paginator.get_page(1)

        hot_skus = []
        nginx_url = 'http://192.168.19.131:8888/'
        for sku in skus1:
            sku_dict = {
                'id':sku.id,
                'name':sku.name,
                'price':sku.price,
                'default_image_url': nginx_url + sku.default_image.name
            }
            hot_skus.append(sku_dict)
        return JsonResponse({'code':0, 'message':'OK', 'count': paginator.num_pages, 'hot_skus':hot_skus})



class SKUListView(View):
    def get(self, request, category_id):
        """分类商品数据获取"""
        # ① 获取参数并进行校验
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)
        ordering = request.GET.get('ordering', '-create_time')

        try:
            cat3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return JsonResponse({'code': 400,
                                 'message': '分类数据不存在'})

        # ② 查询获取商品列表页相关数据
        # 面包屑导航数据
        try:
            breadcrumb = get_breadcrumb(cat3)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '面包屑导航数据获取错误'})

        # 分类SKU商品数据
        try:
            skus = SKU.objects.filter(category_id=category_id,
                                      is_launched=True).order_by(ordering)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '分类SKU商品数据获取错误'})

        # ③ 对SKU商品数据进行分页
        paginator = Paginator(skus, page_size)
        results = paginator.get_page(page)

        sku_li = []
        # FastDFS 中 nginx 服务器的地址
        nginx_url = 'http://192.168.19.131:8888/'

        for sku in results:
            sku_li.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'comments': sku.comments,
                'default_image_url': nginx_url + sku.default_image.name
            })

        # ④ 返回响应数据
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'breadcrumb': breadcrumb,
                             'count': paginator.num_pages,
                             'list': sku_li})
