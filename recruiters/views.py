from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from functools import reduce
import operator
import re
from math import radians, sin, cos, asin, sqrt
from .models import Recruiter
from .forms import RecruiterForm, CandidateSearchForm
from jobs.models import Job, Application
from profiles.models import JobSeekerProfile
try:
    from profiles.models import Project
except Exception:
    Project = None

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

        # No recommendations on dashboard per request

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
    
def _tokens(s: str):
    if not s:
        return []
    return [t.strip() for t in re.split(r"[,\s]+", s) if t.strip()]

def haversine_km(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        return None
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c
class CandidateSearchView(ListView):
    template_name = "recruiters/candidate_search.html"
    context_object_name = "candidates"
    paginate_by = 20

    def get_queryset(self):
        g = self.request.GET
        qs = (
            JobSeekerProfile.objects
            .filter(is_public=True)
            .order_by("last_name", "first_name")
        )
        skill_tokens = _tokens(g.get("skills"))
        if skill_tokens:
            and_clauses = []
            for t in skill_tokens:
                and_clauses.append(
                    Q(skills__icontains=t) |
                    Q(headline__icontains=t) |
                    Q(work_experience__icontains=t)
                )
            qs = qs.filter(reduce(operator.and_, and_clauses))

        loc = g.get("city")
        if loc:
            qs = qs.filter(
                Q(city__icontains=loc) |
                Q(state__icontains=loc) |
                Q(country__icontains=loc)
            )

        proj = g.get("project")
        if proj:
            qs = qs.filter(
                Q(work_experience__icontains=proj) |
                Q(headline__icontains=proj) |
                Q(education__icontains=proj)
            )
        
        # Get radius and user location from GET params
        radius = g.get("radius_km", "").strip()
        user_lat = g.get("user_lat")
        user_lng = g.get("user_lng")

        if radius and user_lat and user_lng:
            try:
                radius_km = float(radius)
                user_lat = float(user_lat)
                user_lng = float(user_lng)

                # First, coarse filter using bounding box
                delta_lat = radius_km / 111.0  # ~111 km per degree latitude
                cos_lat = max(0.1, cos(radians(user_lat)))
                delta_lng = radius_km / (111.0 * cos_lat)

                qs = qs.exclude(lat__isnull=True).exclude(lng__isnull=True)
                qs = qs.filter(
                    lat__gte=user_lat - delta_lat,
                    lat__lte=user_lat + delta_lat,
                    lng__gte=user_lng - delta_lng,
                    lng__lte=user_lng + delta_lng
                )

                # Then precise haversine filter
                keep_ids = []
                for c in qs.only("id", "lat", "lng"):
                    d = haversine_km(user_lat, user_lng, c.lat, c.lng)
                    if d is not None and d <= radius_km:
                        keep_ids.append(c.id)
                qs = qs.filter(id__in=keep_ids)

            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = CandidateSearchForm(self.request.GET or None)
        return ctx
    