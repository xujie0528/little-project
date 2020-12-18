# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.views import View
from django_redis import get_redis_connection

from project.libs.captcha.captcha import captcha


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.set('img_{0}'.format(uuid), text, 300)
        return HttpResponse(image, content_type='image/jpeg')