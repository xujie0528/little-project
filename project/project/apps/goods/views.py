# Create your views here.
import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection
from haystack.views import SearchView
from goods.models import GoodsCategory, SKU
from goods.utils import get_breadcrumb
from haystack.query import SearchQuerySet

from project.utils.mixins import LoginRequiredMixin


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
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': nginx_url + sku.default_image.name
            }
            hot_skus.append(sku_dict)
        return JsonResponse({'code': 0, 'message': 'OK', 'count': paginator.num_pages, 'hot_skus': hot_skus})


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

    # GET /search/?q=<关键字>&page=<页码>&page_size=<页容量>


class SKUSearchView(View):
    def get(self, request):
        """SKU商品数据搜索"""
        # ① 获取参数并进行校验
        keyword = request.GET.get('q')
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 6)

        if not keyword:
            return JsonResponse({'code': 400,
                                 'message': '缺少搜索关键字!'})

        # ② 使用 haystack 检索数据
        query = SearchQuerySet()
        search_res = query.auto_query(keyword).load_all()

        # ③ 对结果数据进行分页
        # 对查询数据进行分页
        from django.core.paginator import Paginator
        paginator = Paginator(search_res, page_size)
        results = paginator.get_page(page)

        # ④ 组织响应数据并返回
        sku_li = []
        nginx_url = 'http://192.168.19.131:8888/'

        for res in results:
            sku = res.object
            sku_li.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': nginx_url + sku.default_image.name,
                'comments': sku.comments
            })

        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'count': paginator.count,
                             'page_size': paginator.per_page,
                             'query': keyword,
                             'skus': sku_li})


class BrowseHistoriesView(LoginRequiredMixin, View):
    def post(self, request):
        req_data = json.loads(request.body.decode())
        sku_id = req_data.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'message': '商品id参数错误'})

        user = request.user
        redis_conn = get_redis_connection('history')
        i = redis_conn.lrem('history_{0}'.format(user.id), 0, sku_id)
        j = redis_conn.lpush('history_{0}'.format(user.id), sku_id)
        k = redis_conn.ltrim('history_{0}'.format(user.id), 0, 4)
        return JsonResponse({'code': 0, 'message': 'OK'})

    def get(self, request):
        user = request.user
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_{0}'.format(user.id), 0, 4)
        skus = []
        nginx_url = 'http://192.168.19.131:8888/'
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_dict = {'id': sku.id,
                        'name': sku.name,
                        'price': sku.price,
                        'comments': sku.comments,
                        'default_image_url': nginx_url + sku.default_image.name}
            skus.append(sku_dict)
            print(skus)

        return JsonResponse({'code': 0, 'message': 'OK', 'skus': skus})
