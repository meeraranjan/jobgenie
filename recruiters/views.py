from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import Recruiter
from .forms import RecruiterForm
from jobs.models import Job
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class RecruiterSignupView(LoginRequiredMixin, CreateView):
    model = Recruiter
    form_class = RecruiterForm
    template_name = "recruiters/recruiter_signup.html" 

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "recruiter_profile"):
            return redirect("recruiters:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        recruiter = form.save(commit=False)
        recruiter.user = self.request.user
        recruiter.save()
        return redirect("recruiters:dashboard")


class RecruiterDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "recruiters/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recruiter = self.request.user.recruiter_profile
        context["recruiter"] = recruiter
        context["jobs"] = Job.objects.filter(recruiter=recruiter).order_by("-created_at")
        return context
    
class BecomeRecruiterView(View):
    @method_decorator(login_required)
    def get(self, request):
        if hasattr(request.user, "recruiter_profile"):
            return redirect("recruiters:dashboard")
        return redirect("recruiters:signup")

# Create your views here.
