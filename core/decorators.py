# decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def role_required(role_name):
    """
    Декоратор для проверки наличия роли у пользователя
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_role(role_name):
                return HttpResponseForbidden("У вас нет доступа к этой странице")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator