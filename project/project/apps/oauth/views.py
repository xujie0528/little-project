# Create your views here.
import json
import re
from django_redis import get_redis_connection

from users.models import User
from oauth.utils import check_secret_openid


from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login
from oauth.models import OAuthQQUser
from oauth.utils import generate_secret_openid

import logging
logger = logging.getLogger('django')


class QQLoginView(View):
    def get(self, request):
        next = request.GET.get('next', '/')

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        login_url = oauth.get_qq_url()

        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'login_url': login_url})


class QQUserView(View):
    def get(self, request):
        code = request.GET.get('code')
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI
        )
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'message': 'QQ登录失败'})
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            secret_openid = generate_secret_openid(openid)
            return JsonResponse(
                {'code': 300,
                 'message': 'OK',
                 'secret_openid': secret_openid})
        else:
            user = qq_user.user
            login(request, user)
            response = JsonResponse({'code': 0,
                                     'message': 'OK'})
            response.set_cookie('username', user.username,
                                max_age=3600 * 24 * 14)

            return response

    def post(self, request):
        req_data = json.loads(request.body.decode())
        mobile = req_data.get('mobile')
        password = req_data.get('password')
        sms_code = req_data.get('sms_code')
        secret_openid = req_data.get('secret_openid')
        if not all([mobile, password, sms_code, secret_openid]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})

            # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'message': '请输入正确的手机号码'})

            # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'message': '请输入8-20位的密码'})

            # 短信验证码是否正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_redis = redis_conn.get('sms_%s' % mobile)

        if not sms_code_redis:
            return JsonResponse({'code': 400,
                                 'message': '短信验证码已过期'})

        if sms_code != sms_code_redis:
            return JsonResponse({'code': 400,
                                 'message': '短信验证码错误'})

        # 对access_token进行解密
        openid = check_secret_openid(secret_openid)

        if not openid:
            return JsonResponse({'code': 400,
                                 'message': 'secret_openid有误'})

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            import base64
            username = base64.b64encode(mobile.encode()).decode()
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
        else:
            # 校验密码是否正确
            if not user.check_password(password):
                return JsonResponse({'code': 400,
                                     'message': '登录密码错误'})

        try:
            OAuthQQUser.objects.create(openid=openid,
                                       user=user)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400,
                                 'message': '数据库操作失败'})

            # ③ 返回响应，登录成功
        login(request, user)

        response = JsonResponse({'code': 0,
                                 'message': 'OK'})
        # 设置cookie
        response.set_cookie('username', user.username,
                            max_age=3600 * 24 * 14)

        return response



