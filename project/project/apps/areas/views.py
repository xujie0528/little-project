from django.core.cache import cache
from django.http import JsonResponse

# Create your views here.
from django.views import View
from areas.models import Area


class ProvinceAreasView(View):
    def get(self, request):
        cache_provinces = cache.get('provinces')

        if not cache_provinces:
            try:
                provinces = Area.objects.filter(parent=None).values('id', 'name')
                provinces = list(provinces)

                cache.set('provinces', provinces, 3600)
            except Exception as e:
                return JsonResponse({'code': 400,
                                     'message': '省级信息获取错误'})
        else:
            provinces = cache_provinces
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'provinces': provinces})


class SubAreasView(View):
    def get(self, request, pk):
        cache_subs = cache.get('sub_areas_%s' % pk)

        if not cache_subs:
            try:
                subs_li = Area.objects.filter(parent_id=pk).values('id', 'name')
                subs_li = list(subs_li)
                cache.set('sub_areas_%s' % pk, subs_li, 3600)
            except Exception as e:
                return JsonResponse({'code': 400,
                                     'message': '子级地区信息获取错误'})
        else:
            subs_li = cache_subs
        return JsonResponse({'code': 0,
                             'message': 'OK',
                             'subs': subs_li})