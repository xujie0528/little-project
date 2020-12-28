import json
from decimal import Decimal

from django.http import JsonResponse
from django.views import View
from project.utils.mixins import LoginRequiredMixin

from carts.utils import CartHelper
from goods.models import SKU
from users.models import Address
from django.utils import timezone
from django.db import transaction
from orders.models import OrderInfo
from orders.models import OrderGoods
# Create your views here.



# GET /orders/settlement/
class OrderSettlementView(LoginRequiredMixin, View):
    def get(self, request):
        """订单结算页面"""
        # ① 获取当前用户的收货地址信息
        addresses = Address.objects.filter(user=request.user, is_delete=False)

        # ② 从redis中获取用户所要结算的商品信息
        try:
            cart_helper = CartHelper(request)
            cart_dict = cart_helper.get_redis_selected_cart()
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '获取购物车数据失败'})

        # ③ 查询数据库获取对应的商品数据
        # 商品数据
        sku_li = []
        try:
            skus = SKU.objects.filter(id__in=cart_dict.keys())

            nginx_url = 'http://192.168.19.131:8888/'

            for sku in skus:
                sku_li.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': nginx_url + sku.default_image.url,
                    'price': sku.price,
                    'count': cart_dict[sku.id]
                })
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '获取商品数据失败'})

        # 订单运费
        freight = Decimal(10.00)

        # 地址信息
        address_li = []

        try:
            for address in addresses:
                address_li.append({
                    'id': address.id,
                    'province': address.province.name,
                    'city': address.city.name,
                    'district': address.district.name,
                    'place': address.place,
                    'receiver': address.receiver,
                    'mobile': address.mobile
                })
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '地址信息获取有误'})

        # ④ 组织并返回响应数据
        context = {
            'addresses': address_li,
            'skus': sku_li,
            'freight': freight,
            'nowsite': request.user.default_address_id
        }

        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'context': context})

class OrderCommitView(View):
    def post(self, request):
        """订单创建"""
        # ①获取参数并进行校验
        req_data = json.loads(request.body.decode())
        address_id = req_data.get('address_id')
        pay_method = req_data.get('pay_method')

        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})

        # 地址是否存在
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '地址信息有误'})

        # 1. 货到付款   2. 支付宝
        if pay_method not in [1, 2]:
            return JsonResponse({'code': 400,
                                 'message': '支付方式有误'})

        # ② 组织订单数据
        user = request.user
        # 生成订单id
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        # total_count和total_amount
        total_count = 0
        total_amount = 0

        # 订单状态
        if pay_method == 1:
            # 货到付款, 等待发货
            status = 2
        else:
            # 支付宝, 待支付
            status = 1

        freight = Decimal(10.00)

        with transaction.atomic():
            # 设置数据库保存操作时, 事务中的保存点
            sid = transaction.savepoint()

        # ③向tb_order_info数据表中添加一行记录
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             address=address,
                                             total_count=total_count,
                                             total_amount=total_amount,
                                             freight=freight,
                                             pay_method=pay_method,
                                             status=status)

            # ④遍历用户要购买的商品记录, 循环向tb_order_goods表中添加记录
            # 从redis中获取用户要购买的商品信息
            cart_helper = CartHelper(request)
            cart_dict = cart_helper.get_redis_selected_cart()
            sku_ids = cart_dict.keys()

            for sku_id in sku_ids:
                sku = SKU.objects.get(id=sku_id)
                count = cart_dict[sku_id]

                # 判断库存是否充足
                if count > sku.stock:
                    # 数据库操作时, 撤销事务中指定保存点后的操作
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({'code': 400,
                                         'message': '商品库存不足'})

                # 减少SKU商品库存, 增加销量
                sku.stock -= count
                sku.stock += count
                sku.save()

                # 增加对应的SPU商品销量
                sku.spu.sales += count
                sku.spu.save()

                # 保存订单信息
                OrderGoods.objects.create(order=order,
                                          sku=sku,
                                          count=count,
                                          price=sku.price)

                # 累计计算订单商品的总数量和总价格
                total_count += count
                total_amount += count*sku.price

            total_amount += freight
            order.total_count = total_count
            order.total_amount = total_amount
            order.save()

        # ⑤ 清除用户购物车中已购买的记录
        cart_helper.clear_redis_selected_cart()

        # ⑥ 返回响应
        return JsonResponse({'code': 0,
                             'message': '下单成功',
                             'order_id': order_id})