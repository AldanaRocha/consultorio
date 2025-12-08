# accounts/decorators.py
from django.shortcuts import redirect
from functools import wraps

def role_required(group_name, redirect_url='home'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            return redirect(redirect_url)
        return _wrapped
    return decorator
