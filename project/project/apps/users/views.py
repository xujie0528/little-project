# Create your views here.
import json
import re

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection

from project.utils.mixins import LoginRequiredMixin
from users.models import User


class UsernameCountView(View):
    def get(self, request, username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            return JsonResponse({'code': 400, 'message': '操作数据库失败'})
        return JsonResponse({'code': 0, 'message': 'OK', 'count': count})


class MobileCountView(View):
    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            return JsonResponse({'code': 400, 'message': '读取数据库错误'})
        return JsonResponse({'code': 0, 'message': 'OK', 'count': count})


class RegisterView(View):
    def post(self, request):
        req_data = json.loads(request.body.decode())
        username = req_data.get('username')
        password = req_data.get('password')
        password2 = req_data.get('password2')
        mobile = req_data.get('mobile')
        allow = req_data.get('allow')
        sms_code = req_data.get('sms_code')
        if not all([username, password, password2, mobile, allow, sms_code]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400,
                                 'message': 'username格式错误'})

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': 400,
                                 'message': 'password格式错误'})

        if password != password2:
            return JsonResponse({'code': 400,
                                 'message': '两次密码不一致'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'message': '手机号格式错误'})

        if not allow:
            return JsonResponse({'code': 400,
                                 'message': '请同意协议!'})

        redis_conn = get_redis_connection('verify_code')
        sms_code_redis = redis_conn.get('sms_{0}'.format(mobile))

        if not sms_code_redis:
            return JsonResponse({'code': 400,
                                 'message': '短信验证码过期'})

        if sms_code != sms_code_redis:
            return JsonResponse({'code': 400,
                                 'message': '短信验证码错误'})

            # ② 保存新增用户数据到数据库
        try:
            user = User.objects.create_user(username=username,
                                            password=password,
                                            mobile=mobile)
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '数据库保存错误'})

        from django.contrib.auth import login
        login(request, user)
        # ③ 返回响应
        response = JsonResponse({'code': 0,
                                 'message': 'OK'})
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        return response


class CSRFTokenView(View):
    def get(self, request):
        """获取csrf_token的值"""
        # ① 生成csrf_token的值
        csrf_token = get_token(request)

        # ② 将csrf_token的值返回
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'csrf_token': csrf_token})


class LoginView(View):
    def post(self, request):
        req_data = json.loads(request.body.decode())
        username = req_data.get('username')
        password = req_data.get('password')
        remember = req_data.get('remember')

        import re
        if re.match(r'^1[3-9]\d{9}$', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        if not all([username, password]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400,
                                 'message': '用户名或密码错误'})

        # ② 保存登录用户的状态信息

        login(request, user)

        if not remember:
            # 如果未选择记住登录，浏览器关闭即失效
            request.session.set_expiry(0)

        # ③ 返回响应，登录成功
        response = JsonResponse({'code': 0,
                                 'message': 'OK'})

        # 设置 cookie 保存 username 用户名
        response.set_cookie('username',
                            user.username,
                            max_age=3600 * 24 * 14)

        return response


class LogoutView(View):
    def delete(self, request):
        """退出登录"""
        # ① 请求登录用户的session信息
        logout(request)

        # ② 删除cookie中的username
        response = JsonResponse({'code': 0,
                                 'message': 'ok'})

        response.delete_cookie('username')

        # ③ 返回响应
        return response


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        info = {
            'username': user.username,
            'mobile': user.mobile,
            'email': user.email,
            'email_active': user.email_active
        }
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'user': info})


class UserEmailView(LoginRequiredMixin, View):
    def put(self, request):
        req_data = json.loads(request.body.decode())
        email = req_data.get('email')

        if not email:
            return JsonResponse({'code': 400,
                                 'message': '缺少email参数'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400,
                                 'message': '参数email有误'})

        user = request.user
        try:
            user.email = email
            user.save()
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '邮箱设置失败'})

        from celery_tasks.email.tasks import send_verify_email
        verify_url = user.generate_verify_email_url()
        # 发出邮件发送的任务消息
        send_verify_email.delay(email, verify_url)

        return JsonResponse({'code': 0,
                             'message': 'OK'})


class EmailVerifyView(View):
    def put(self, request):
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'code': 400,
                                 'message': '缺少token参数'})

            # 对用户的信息进行解密
        user = User.check_verify_email_token(token)

        if user is None:
            return JsonResponse({'code': 400,
                                 'message': 'token信息有误'})

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            return JsonResponse({'code': 400,
                                 'message': '验证邮箱失败'})
            # ③ 返回响应
        return JsonResponse({'code': 0,
                             'message': 'OK'})

