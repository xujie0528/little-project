# Create your views here.
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
