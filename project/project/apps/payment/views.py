import os

from alipay import AliPay
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from project.utils.mixins import LoginRequiredMixin

from orders.models import OrderInfo


# /payment/(?P<order_id>\d+)/
class PaymentURLView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        """获取支付宝支付地址"""
        # ① 获取参数并进行校验
        user = request.user

        try:
            order = OrderInfo.objects.get(user=user,
                                          order_id=order_id,
                                          status=1)
        except Exception as e:
            return JsonResponse({'code': 0,
                                 'message': '订单信息有误!'})

        # ② 生成支付宝支付地址并返回
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'alipay_url': alipay_url})


from payment.models import Payment


# PUT /payment/status/
class PaymentStatusView(LoginRequiredMixin, View):
    def put(self, request):
        """支付结果信息处理"""
        # ① 获取参数并进行校验
        req_data = request.GET.dict()

        # 签名校验
        signature = req_data.pop('sign')
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        success = alipay.verify(req_data, signature)

        # ② 订单支付结果处理保存
        if success:
            order_id = req_data.get('out_trade_no')
            trade_id = req_data.get('trade_no')

            # 保存支付交易编号
            Payment.objects.create(order_id=order_id,
                                   trade_id=trade_id)

            # 修改对应订单的支付状态：2-待发货
            OrderInfo.objects.filter(order_id=order_id,
                                     status=1).update(status=2)

            # ③ 返回响应
            return JsonResponse({'code': 0,
                                 'message': 'ok',
                                 'trade_id': trade_id})
        else:
            # 订单支付失败，返回相应提示
            return JsonResponse({'code': 400,
                                 'message': '支付出错!非法请求!'})
