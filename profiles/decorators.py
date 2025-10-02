from functools import wraps
from django.core.exceptions import PermissionDenied

def recruiter_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not hasattr(request.user, "recruiter_profile"):
            raise PermissionDenied 
        return view_func(request, *args, **kwargs)
    return _wrapped_view
