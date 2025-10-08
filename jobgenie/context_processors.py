from recruiters.models import Recruiter

def user_role_context(request):
    if not request.user.is_authenticated:
        return {}
    
    is_recruiter = Recruiter.objects.filter(user=request.user).exists()
    return {'is_recruiter': is_recruiter}
