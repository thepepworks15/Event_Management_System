from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect("accounts:login")
        if not request.user.is_staff:
            messages.error(request, "You do not have permission to access this page.")
            return redirect("events:home")
        return view_func(request, *args, **kwargs)
    return wrapper
