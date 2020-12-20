from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import BadData, TimedJSONWebSignatureSerializer


# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'

    @staticmethod
    def check_verify_email_token(token):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except BadData as e:
            return None
        else:
            user_id = data.get('user_id')
            email = data.get('email')

        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user

    def generate_verify_email_url(self):
        """生成当前用户的邮件验证链接"""
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 7200)

        # 用户信息加密，生成token
        data = {'user_id': self.id,
                'email': self.email}
        token = serializer.dumps(data).decode()

        # 生成邮箱验证链接地址
        verify_url = settings.EMAIL_VERIFY_URL + token
        return verify_url
