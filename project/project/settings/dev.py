"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-g+9^(gq2jgx)h8ew_^h8&-bkdth6a3n@2j&@6&g41osh=388('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'corsheaders',
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
    'contents.apps.ContentsConfig',
    'goods.apps.GoodsConfig',
    'haystack',
    'carts.apps.CartsConfig',
    'orders.apps.OrdersConfig',
    'payment.apps.PaymentConfig',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    # 将异步跨域请求中，Origin请求头携带的源请求地址添加到此处的白名单中
    'http://www.meiduo.site:8080',
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'projectbase',
        'HOST': '192.168.19.131',
        'PORT': 3306,
        'USER': 'xujie',
        'PASSWORD': '123456abc'
    }
}

AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
CACHES = {
    "default": {
        # 默认缓存数据存储信息：存到 0 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.19.131:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        # session数据信息：存到 1 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.19.131:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": {
        # 验证码信息: 存到 2 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.19.131:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 从redis中查询出数据之后，会自动将bytes数据解码为str
            "CONNECTION_POOL_KWARGS": {
                'decode_responses': True
            }
        }
    },
    "carts": {
        # 购物车数据: 存到 4 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.19.131:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 从redis中查询出数据之后，会自动将bytes数据解码为str
            "CONNECTION_POOL_KWARGS": {
                'decode_responses': True
            }
        }
    },
    "history": {
        # 购物车数据: 存到 5 号库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.19.131:6379/5",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # 从redis中查询出数据之后，会自动将bytes数据解码为str
            "CONNECTION_POOL_KWARGS": {
                'decode_responses': True
            }
        }
    },
}

# 设置session数据存储到CACHES缓存中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# 设置session数据存储到CACHES缓存的session配置中
SESSION_CACHE_ALIAS = "session"

# 日志存储配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

QQ_CLIENT_ID = '101474184'
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

# 邮件发送 SMTP 服务配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# 我们使用的 SMTP 服务地址：
EMAIL_HOST = 'smtp.qq.com'
# SMTP 服务的端口号
EMAIL_PORT = 25
# 开启 SMTP 服务的邮箱：此处是你的网易163邮箱
EMAIL_HOST_USER = '2422640226@qq.com'
# 开启 SMTP 服务后显示的授权密码
EMAIL_HOST_PASSWORD = 'ntjdyklapjvlebhj'
EMAIL_USE_TLS = True
# 收件人看到的发件人
EMAIL_FROM = '美多商城<2422640226@qq.com>'
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8080/success_verify_email.html?token='

# 生成的静态 html 文件保存目录
# GENERATED_STATIC_HTML_FILES_DIR：项目目录，即 meiduo 目录的绝对路径
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# django-haystack 配置
HAYSTACK_CONNECTIONS = {
    'default': {
        # 配置使用 ElasticSearch 搜索引擎
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        # 配置 ElasticSearch 服务的地址
        # 注意：如果不是使用提供的虚拟机，需要将 192.168.19.131 替换为自己虚拟机的IP
        'URL': 'http://192.168.19.131:9200/',
        # 存储索引数据的索引库的名称
        'INDEX_NAME': 'meiduo_mall',
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 支付宝开发者应用ID
# 注意：此处替换为你的账号中沙箱应用的APPID，如果使用线上开发者应用，则替换为对应开发者应用的APPID
ALIPAY_APPID = '2021000116684343'
# 是否使用沙箱环境
# 注意：如果使用线上开发者应用，此处设置为：False
ALIPAY_DEBUG = True
# 支付宝网关地址
# 注意：此处为支付宝沙箱环境的网关地址，如果使用线上开发者应用，此处需替换为支付宝线上环境的网关地址
ALIPAY_URL = '	https://openapi.alipaydev.com/gateway.do'
# 用户授权支付后的回调地址
ALIPAY_RETURN_URL = "http://www.meiduo.site:8080/pay_success.html"
