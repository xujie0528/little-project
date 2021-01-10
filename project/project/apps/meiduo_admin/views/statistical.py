from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User


class UserDayActiveView(APIView):
    # 指定权限, 只有管理员用户才能进行访问
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取网站日活跃用户"""
        # 查询数据库统计网站当日活跃用户
        now_date = timezone.now().replace(hour=0, minute=0, second=0,
                                          microsecond=0)
        count = User.objects.filter(last_login__gte = now_date).count()

        #返回响应数据
        response_data = {
            # 年-月-日
            'data': now_date.date(),
            'count': count
        }
        return Response(response_data)

