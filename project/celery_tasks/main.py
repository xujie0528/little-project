import os

# 设置django运行所依赖的环境变量
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.dev')

from celery import Celery

# ① 创建Celery对象
celery_app = Celery('demo')

# ② 加载config.py的配置
celery_app.config_from_object('celery_tasks.config')

# ③ celery worker启动时自动加载任务
celery_app.autodiscover_tasks(['celery_tasks.sms',
                               'celery_tasks.email'])
