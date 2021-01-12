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
        count = User.objects.filter(last_login__gte=now_date).count()

        # 返回响应数据
        response_data = {
            # 年-月-日
            'data': now_date.date(),
            'count': count
        }
        return Response(response_data)


class UserDayOrderView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        conut = User.objects.filter(orders__create_time__gte=now_date).distinct().count()
        # 返回响应数据
        response_data = {
            'data': now_date.date(),
            'count': conut
        }
        return Response(response_data)


class UserMonthCountView(APIView):
    # 指定权限, 只有管理员用户可以访问
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取近30天网站每日新增用户数
        # 查询数据库统计网站近30天每日新增用户数量
        # 结束时间
        now_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # 起始时间: now_date - 29天
        begin_date = now_date - timezone.timedelta(days=29)

        # 当天日期
        current_date = begin_date

        # 每日新增用户数量
        month_list = []
        while current_date <= now_date:
            next_date = current_date + timezone.timedelta(days=1)
            # 统计当天新增用户量
            count = User.objects.filter(date_joined__gte=current_date,
                                        date_joined__lt=next_date).count()

            month_list.append({
                'count': count,
                'date': current_date.date()
            })

            current_date = next_date

        # 返回响应数据
        return Response(month_list)


class TotalCountView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        now_date = timezone.now()
        count = User.objects.filter(date_joined__lt = now_date).count()

        response_data = {
            'date': now_date.date(),
            'count': count
        }

        return Response(response_data)