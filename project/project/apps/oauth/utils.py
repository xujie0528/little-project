from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings


def generate_secret_openid(openid):
    """对传入的 openid 进行加密处理，返回加密之后的内容"""
    # settings.SECRET_KEY: 加密使用的秘钥
    # 解密过期时间: 10min = 600s
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                 expires_in=600)

    # 待加密数据
    data = {'openid': openid}

    # 数据加密操作
    secret_openid = serializer.dumps(data).decode()

    # 返回加密之后的 openid
    return secret_openid