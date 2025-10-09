from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Recruiter
from .forms import RecruiterForm
from jobs.models import Job, Application
from profiles.models import JobSeekerProfile
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

        jobs = Job.objects.filter(recruiter=recruiter).order_by("-created_at")
        context["jobs"] = jobs

        job_pipelines = {}
        for job in jobs:
            applications = job.applications.select_related("candidate")
            job_pipelines[job.id] = {
                "applied": applications.filter(status="applied"),
                "review": applications.filter(status="review"),
                "interview": applications.filter(status="interview"),
                "offer": applications.filter(status="offer"),
                "closed": applications.filter(status="closed"),
            }
        context["job_pipelines"] = job_pipelines

        return context
    
class BecomeRecruiterView(View):
    @method_decorator(login_required)
    def get(self, request):
        if hasattr(request.user, "recruiter_profile"):
            return redirect("recruiters:dashboard")
        return redirect("recruiters:signup")

# Create your views here.

@csrf_exempt
def update_status(request, app_id, new_status):
    if request.method == "POST":
        app = get_object_or_404(Application, id=app_id)
        app.status = new_status
        app.save()
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def update_status(request, app_id, new_status):
    print("Received status update:", app_id, new_status)  # Debug log
    if request.method == "POST":
        app = get_object_or_404(Application, id=app_id)
        app.status = new_status.lower().strip()  # Normalize
        app.save()
        print("Updated application:", app.id, app.status)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

class RecruiterApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = "recruiters/application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        recruiter = self.request.user.recruiter_profile
        return Application.objects.filter(job__recruiter=recruiter)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        candidate = application.candidate

        profile = JobSeekerProfile.objects.filter(user=candidate).first()

        if profile and profile.is_public:
            context["profile"] = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "headline": profile.headline,
                "skills": profile.skills,
                "education": profile.education,
                "work_experience": profile.work_experience,
                "links": profile.links,
            }
        else:
            context["profile"] = None

        return context