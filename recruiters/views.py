from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
from django.templatetags.static import static
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from functools import reduce
import operator
import os
import base64
import re
from math import radians, sin, cos, asin, sqrt
from .models import Recruiter
from .forms import RecruiterForm, CandidateSearchForm
from jobs.models import Job, Application
from profiles.models import JobSeekerProfile
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
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

        if profile and (profile.first_name or profile.last_name):
            name = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
        elif candidate.get_full_name():
            name = candidate.get_full_name()
        else:
            name = candidate.username

        if name != candidate.username:
            display_name_with_username = f"{name} ({candidate.username})"
        else:
            display_name_with_username = candidate.username

        context["display_name_with_username"] = display_name_with_username

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

def send_candidate_email(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    candidate = application.candidate
    profile = JobSeekerProfile.objects.filter(user=candidate).first()

    # --- Recipient name ---
    if profile and (profile.first_name or profile.last_name):
        recipient_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
    elif candidate.get_full_name():
        recipient_name = candidate.get_full_name()
    else:
        recipient_name = candidate.username

    # --- Recipient email ---
    recipient_email = profile.email if profile and profile.email else candidate.email
    if not recipient_email:
        messages.error(request, f"{recipient_name} has not provided an email address. Try messaging instead.")
        return redirect('recruiters:application_detail', pk=application.id)

    # --- Read and encode logo ---
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    logo_data_uri = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            logo_data_uri = f"data:image/png;base64,{logo_base64}"

    if request.method == 'POST':
        subject_input = request.POST.get('subject')
        message_body = request.POST.get('message')
        
        job = application.job
        company_name = job.company_name or "Unknown Company"

        # 👇 This is the inbox subject (caption)
        email_subject = f"JobGenie - Regarding your application for {job.title} from {company_name}"

        # 👇 These go into the HTML email body
        context = {
            'company_name': company_name,
            'header_title': subject_input or "Application Update",  # subheader inside email
            'message_body': message_body,
        }

        html_message = render_to_string('recruiters/email_template.html', context)

        email = EmailMultiAlternatives(
            subject=email_subject,  # shown in inbox
            body=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

        messages.success(request, f"Email sent to {recipient_name} successfully!")
        return redirect('recruiters:application_detail', pk=application.id)

    # GET: render email form
    return render(request, 'recruiters/send_email.html', {
        'candidate': candidate,
        'application': application,
        'display_name_clean': recipient_name,
    })


class RecruiterProfileView(DetailView):
    model = Recruiter
    template_name = "recruiters/profile.html"
    context_object_name = "recruiter"

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(self.request.user.__class__, username=username)
        recruiter = getattr(user, 'recruiter_profile', None)
        if not recruiter:
            from django.http import Http404
            raise Http404("Recruiter profile not found")
        return recruiter

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        recruiter = ctx.get('recruiter')
        if recruiter is None:
            ctx['public'] = False
            return ctx

        if not recruiter.is_public and self.request.user != recruiter.user:
            ctx['public'] = False
        else:
            ctx['public'] = True
        return ctx


class RecruiterEditView(LoginRequiredMixin, UpdateView):
    model = Recruiter
    form_class = RecruiterForm
    template_name = "recruiters/edit_profile.html"
    success_url = "/recruiters/dashboard/"

    def get_object(self, queryset=None):
        return get_object_or_404(Recruiter, user=self.request.user)
    