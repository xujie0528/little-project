# Create your views here.
import json
import re

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection

from project.utils.mixins import LoginRequiredMixin
from rest_framework.generics import CreateAPIView

from carts.utils import CartHelper
from users.models import User, Address



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

        cart_helper = CartHelper(request, response)
        cart_helper.merge_cookie_cart_to_redis()

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

        cart_helper = CartHelper(request, response)
        cart_helper.merge_cookie_cart_to_redis()

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

class AddressView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            count = Address.objects.filter(user=request.user, is_delete=False).count()
        except Exception:
            return JsonResponse({'code': 400,
                                 'message': '获取地址数据出错'})

        if count >= 20:
            return JsonResponse({'code': 400,
                                 'message': '收货地址超过上限'})

        req_data = json.loads(request.body.decode())
        title = req_data.get('title')
        receiver = req_data.get('receiver')
        province_id = req_data.get('province_id')
        city_id = req_data.get('city_id')
        district_id = req_data.get('district_id')
        place = req_data.get('place')
        mobile = req_data.get('mobile')
        phone = req_data.get('phone')
        email = req_data.get('email')

        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'message': '参数mobile有误'})

        if phone:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', phone):
                return JsonResponse({'code': 400,
                                     'message': '参数phone有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'message': '参数email有误'})
        user = request.user
        try:
            address = Address.objects.create(user_id=user.id, **req_data)
            if not request.user.default_address:
                user.default_address = address
                user.save()
        except Exception:
            return JsonResponse({'code': 400,
                                 'message': '新增地址保存失败'})
        address_data = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'phone': address.phone,
            'email': address.email
        }
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'address': address_data})

    @staticmethod
    def get(request):
        user=request.user
        address_list = []
        try:
            address_user = Address.objects.filter(user_id=user.id)
        except Exception:
            return JsonResponse({'code':400, 'message':'数据获取失败'})
        for address in address_user:
            if address.is_delete == False:
                info = {
                    'id': address.id,
                    'title': address.title,
                    'receiver': address.receiver,
                    'province': str(address.province),
                    'city': str(address.city),
                    'district': str(address.district),
                    'province_id': address.province_id,
                    'city_id': address.city_id,
                    'district_id': address.district_id,
                    'place': address.place,
                    'mobile': address.mobile,
                    'phone': address.phone,
                    'email': address.email
                }
                address_list.append(info)
        return JsonResponse({'code': 0, 'message': 'OK',
                             "default_address_id": user.default_address_id,
                             'addresses': address_list})


class UserUpdateView(View):
    def put(self, request, address_id):

        req_data = json.loads(request.body)

        title = req_data.get('title')
        receiver = req_data.get('receiver')
        province_id = req_data.get('province_id')
        city_id = req_data.get('city_id')
        district_id = req_data.get('district_id')
        place = req_data.get('place')
        mobile = req_data.get('mobile')
        phone = req_data.get('phone')
        email = req_data.get('email')

        address = Address.objects.get(id=address_id)

        address.title = title
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.phone = phone
        address.email = email
        address.save()

        # info = {
        #     'title': title,
        #     'receiver': receiver,
        #     'province_id': province_id,
        #     'city_id': city_id,
        #     'district_id': district_id,
        #     'place': place,
        #     'mobile': mobile,
        #     'phone': phone,
        #     'email': email
        # }

        return JsonResponse({'code': 0, 'message':'OK', 'address': req_data})

    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            address.is_delete = True
            address.save()
        except Exception:
            return JsonResponse({'code':400, 'message':'数据获取失败'})
        return JsonResponse({'code': 0, 'message':'OK'})

# API: PUT /addresses/(?P<address_id>\d+)/default/
class AddressesDefaultView(View):
    def put(self, request, address_id):
        user = request.user
        user.default_address_id = address_id
        user.save()
        return JsonResponse({'code': 0, 'message':'OK'})

# API: PUT /addresses/(?P<address_id>\d+)/title/
class AddressTitleView(View):
    def put(self, request, address_id):
        address = Address.objects.get(id=address_id)
        title_get = json.loads(request.body)
        title = title_get.get('title')
        address.title = title
        address.save()
        return JsonResponse({'code': 0, 'message':'OK'})


# API: PUT /password/
class PasswordUpdateView(LoginRequiredMixin, View):
    def put(self, request):
        password_set = json.loads(request.body)
        old_password = password_set.get('old_password')
        new_password = password_set.get('new_password')
        new_password2 = password_set.get('new_password2')
        users = request.user
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400,
                                 'message': '缺少必传参数'})

        if not re.match(r'^[a-zA-Z0-9]{8,20}$', new_password):
            return JsonResponse({'code': 400,
                                 'message': 'password格式错误'})

        if new_password != new_password2:
            return JsonResponse({'code': 400,
                                 'message': '两次密码不一致'})

        if users.check_password(old_password) == False:
            return JsonResponse({'code':400, 'message': '两次密码cuowu'})

        users.set_password(new_password)
        users.save()
        return JsonResponse({'code': 0, 'message': 'OK'})
