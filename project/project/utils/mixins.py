from django.http import JsonResponse


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({'code': 400,
                                 'message': '用户未登录'})
    return wrapper


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **init_kwargs):
        view = super().as_view(**init_kwargs)
        return login_required(view)
