# 导入Celery对象
from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.ccp_sms import CCP


# @celery_app.task(name="任务名称")
@celery_app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code):
    """封装任务函数代码"""
    print("发送短信任务函数执行...")
    print("[mobile: %s] [sms_code: %s]" % (mobile, sms_code))
    # 调用云通讯SDK接口进行短信的发送
    CCP().send_template_sms(mobile, [sms_code, 5], 1)