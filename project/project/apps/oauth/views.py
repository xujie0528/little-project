# Create your views here.
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.http import  JsonResponse
from django.views import View

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
