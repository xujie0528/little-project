import base64
import json
import pickle

from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU


class CartsView(View):
    def post(self, request):
        # 接收Json参数, 获取数据
        cart = json.loads(request.body)
        sku_id = cart.get('sku_id')
        count = cart.get('count')
        selected = cart.get('selected', True)

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'message': '缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'message': 'sku_id不存在'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'code': 400, 'message': 'count类型错误'})
        if selected:
            if not isinstance(selected, bool):
                return JsonResponse({'code': 400, 'message': '参数selected类型错误'})

        # 验证用户是否登录
        # 已登录
        user = request.user.id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hincrby('carts_{0}'.format(user), sku_id, count)
            if selected:
                redis_conn.sadd('selected_{0}'.format(user), sku_id)

            return JsonResponse({'code': 0, 'message': '购物车记录添加成功', 'count': count})

        # 未登录
        else:
            carts_cookies = request.COOKIES.get('carts')
            # 获取的是一串乱码
            if carts_cookies:
                carts_bytes = base64.b64decode(carts_cookies)
                # 先转byte类型的字典
                cart_dict = pickle.loads(carts_bytes)
                # 再转字典
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                # count累加
                origin_cart = cart_dict[sku_id]['count']
                count = count + origin_cart
            # 存入字典
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_dict = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = JsonResponse({'code': 0,
                                     'message': 'ok'})
            # 设置cookies
            response.set_cookie('carts', cart_dict)
            return response

    def get(self, request):
        # 判断用户是否登录
        users = request.user.id
        # 已经登录
        if request.user.is_authenticated:
            # 与redis数据库建立连接
            redis_conn = get_redis_connection('carts')
            # 查询hash数据
            carts_get = redis_conn.hgetall('carts_{0}'.format(users))
            print(carts_get)
            # 查询set数据
            seleted_get = redis_conn.smembers('selected_{0}'.format(users))
            print(seleted_get)

            cart_dict = {}
            # 遍历查找键值对, 将redis_carts和redis_selected进行数据构造, 存放到一张字典里
            for sku_id, count in carts_get.items():
                # sku_id 和 count 为字符串类型, 转换为整形
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    # 如果sku_id在seleted_get中存在, 返回True
                    'selected': sku_id in seleted_get
                }
            # # 查询所有的key(sku_id), 获取SKU
            # sku_ids = cart_dict.keys()
            # list = []
            # nginx_url = 'http://192.168.19.131:8888/'
            # # 一边遍历, 一边查询数据
            # for sku_id in sku_ids:
            #     skus = SKU.objects.filter(id=sku_id)
            #     # 遍历所有数据, 构造响应字典
            #     for sku in skus:
            #         dict = {'id': sku.id,
            #                 'name': sku.name,
            #                 'price': sku.price,
            #                  # 获取完整的图片路径
            #                 'default_image_url':nginx_url + sku.default_image.name,
            #                 # sku中并没有count和selected字段, 所以得从前面字典中读取
            #                 'count': cart_dict[sku.id]['count'],
            #                 'selected': cart_dict[sku.id]['selected'],
            #                 }
            #         list.append(dict)
            # return JsonResponse({'code': 0, 'message': 'OK', 'cart_skus': list})


        # 未登录
        else:
            # 获取cookie中购物车数据
            carts_cookies = request.COOKIES.get('carts')

            if carts_cookies:
                # 先用base64转为byte类型
                carts_bytes = base64.b64decode(carts_cookies)
                # 再用pickle转字典
                cart_dict = pickle.loads(carts_bytes)

            else:
                cart_dict = {}

        sku_ids = cart_dict.keys()
        list = []
        nginx_url = 'http://192.168.19.131:8888/'
        # 一边遍历, 一边查询数据
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            # 遍历所有数据, 构造响应字典
            dict = {'id': sku.id,
                    'name': sku.name,
                    'price': sku.price,
                    # 获取完整的图片路径
                    'default_image_url': nginx_url + sku.default_image.name,
                    # sku中并没有count和selected字段, 所以得从前面字典中读取
                    'count': cart_dict[sku.id]['count'],
                    'selected': cart_dict[sku.id]['selected'],
                    }
            list.append(dict)

        return JsonResponse({'code': 0, 'message': 'OK', 'cart_skus': list})

    def put(self, request):
        cart = json.loads(request.body)
        sku_id = cart.get('sku_id')
        count = cart.get('count')
        selected = cart.get('selected', True)

        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'message': '缺少必传参数'})
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code': 400, 'message': 'sku_id不存在'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'code': 400, 'message': 'count类型错误'})
        if selected:
            if not isinstance(selected, bool):
                return JsonResponse({'code': 400, 'message': '参数selected类型错误'})

        user = request.user.id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hset('carts_{0}'.format(user), sku_id, count)
            if selected:
                redis_conn.sadd('selected_{0}'.format(user), sku_id)
            redis_conn.srem('selected_{0}'.format(user), sku_id)
            return JsonResponse({'code': 0, 'message': '购物车记录添加成功',
                                 'cart_sku': cart})

        else:
            carts_cookies = request.COOKIES.get('carts')
            # 获取的是一串乱码
            if carts_cookies:
                carts_bytes = base64.b64decode(carts_cookies)
                # 先转byte类型的字典
                cart_dict = pickle.loads(carts_bytes)
                print(cart_dict)
                cart_dict[sku_id] = {"count": count,
                                     "selected": selected}
                cart_dict = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response = JsonResponse({'code': 0,
                                         'message': 'ok',
                                         "cart_sku": {
                                             "sku_id": sku_id,
                                             "count": count,
                                             "selected": selected
                                         }})
                # 设置cookies
                response.set_cookie('carts', cart_dict)
                return response

    def delete(self, request):
        cart = json.loads(request.body)
        sku_id = cart.get('sku_id')

        if not sku_id:
            return JsonResponse({'code': 400, 'message': '参数传输错误'})

        user = request.user.id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hdel('carts_{0}'.format(user), sku_id)
            redis_conn.srem('selected_{0}'.format(user), sku_id)
            return JsonResponse({'code': 0, 'message': '购物车记录删除成功'})

        else:
            cart_cookies = request.COOKIES.get('carts')
            if cart_cookies:
                cart_byte = base64.b64decode(cart_cookies)
                cart_dict = pickle.loads(cart_byte)
                cart_dict.pop(sku_id)
                cart_dict = base64.b64encode(pickle.dumps(cart_dict)).decode()
                return JsonResponse({'code': 0, 'message': '购物车记录删除成功'})

class SelectionView(View):
    def put(self, request):
        cart = json.loads(request.body)
        selected = cart.get('selected', True)
        user = request.user.id
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            sku_ids = redis_conn.hkeys('carts_{0}'.format(user))
            if selected:
                redis_conn.sadd('selected_{0}'.format(user), *sku_ids)
            else:
                redis_conn.srem('selected_{0}'.format(user), *sku_ids)
            return JsonResponse({'code': 0,
                                 'message': 'OK'})
        else:
            cookie_cart = request.COOKIES.get('carts')
            if not cookie_cart:
                return JsonResponse({'code': 0,
                                     'message': 'OK'})

