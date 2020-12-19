# Create your views here.
import random

from django.http import JsonResponse, HttpResponse
from django.views import View
from django_redis import get_redis_connection

from project.libs.captcha.captcha import captcha
from project.libs.yuntongxun.ccp_sms import CCP


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.set('img_{0}'.format(uuid), text, 300)
        return HttpResponse(image, content_type='image/jpeg')

import logging
logger = logging.getLogger('django')

class SMSCodeView(View):
    def get(self, request, mobile):
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_{0}'.format(mobile))
        if send_flag:
            return JsonResponse({'code': 400, 'message': '验证码发送过于频繁'})
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'message': '缺少必传参数'})

        redis_conn = get_redis_connection('verify_code')
        image_code_redis = redis_conn.get('img_{0}'.format(uuid))
        if image_code_redis is None:
            return JsonResponse({'code': 400, 'message':'图形验证码失效'})
        try:
            redis_conn.delete('img_{0}'.format(uuid))
        except Exception as e:
            logger.error(e)

        if image_code.lower() != image_code_redis.lower():
            return JsonResponse({'code': 400, 'message':'输入的验证码有误'})

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info('短信验证码为{0}'.format(sms_code))
        redis_conn.set('sms_{0}'.format(mobile), sms_code, 300)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)
        return JsonResponse({'code': 0, 'message':'短信发送成功'})
