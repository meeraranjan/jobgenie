from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from functools import reduce
import operator
from django.contrib import messages

from .models import Job, Application
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import JobForm
from django.core.exceptions import PermissionDenied
from .forms import JobFilterForm
from django.conf import settings
from recruiters.recommendations import recommend_candidates_for_job

from math import radians, sin, cos, asin, sqrt
from .utils import geocode_address


def haversine_km(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        return None
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def _center_from_request(self, g):
        lat = (g.get('user_lat') or '').strip()
        lng = (g.get('user_lng') or '').strip()
        if lat and lng:
            try:
                return float(lat), float(lng)
            except ValueError:
                pass

        city = (g.get('city') or '').strip()
        if city:
            latlng = geocode_address(city)
            if latlng and all(latlng):
                try:
                    return float(latlng[0]), float(latlng[1])
                except ValueError:
                    pass
        return None

    def get_queryset(self):
        qs = Job.objects.all().order_by('-created_at')
        g = self.request.GET

        # Filter jobs based on user role
        user = self.request.user
        if g.get('title'):
            qs = qs.filter(title__icontains=g['title'])

        if g.get('city'):
            qs = qs.filter(city__icontains=g['city'])

        if g.get('skills'):
            raw = g['skills'].replace(',', ' ')
            tokens = [t.strip() for t in raw.split() if t.strip()]
            if tokens:
                qs = qs.filter(reduce(operator.or_, (Q(skills__icontains=t) for t in tokens)))

        job_types = g.getlist('job_type')
        if job_types:
            qs = qs.filter(job_type__in=job_types)

        remote_types = g.getlist('remote_type')
        if remote_types:
            qs = qs.filter(remote_type__in=remote_types)

        visa = g.get('visa')
        if visa in ('YES', 'NO'):
            qs = qs.filter(visa_sponsorship=visa)

        min_salary = g.get('min_salary')
        max_salary = g.get('max_salary')
        if min_salary:
            qs = qs.filter(Q(salary_max__isnull=True) | Q(salary_max__gte=min_salary))
        if max_salary:
            qs = qs.filter(Q(salary_min__isnull=True) | Q(salary_min__lte=max_salary))

        radius = (g.get('radius_km') or '').strip()
        center = None
        if radius:
            center = self._center_from_request(g)

        if center and radius:
            try:
                user_lat, user_lng = center
                radius_km = float(radius)

                delta_lat = radius_km / 111.0
                cos_lat = max(0.1, cos(radians(user_lat)))
                delta_lng = radius_km / (111.0 * cos_lat)

                approx = (qs.exclude(lat__isnull=True)
                            .exclude(lng__isnull=True)
                            .filter(lat__gte=user_lat - delta_lat,
                                    lat__lte=user_lat + delta_lat,
                                    lng__gte=user_lng - delta_lng,
                                    lng__lte=user_lng + delta_lng))

                keep_ids = []
                for j in approx.only('id', 'lat', 'lng'):
                    d = haversine_km(user_lat, user_lng, j.lat, j.lng)
                    if d is not None and d <= radius_km:
                        keep_ids.append(j.id)
                qs = qs.filter(id__in=keep_ids)
            except ValueError:
                pass
        
        if user.is_authenticated:
            userprofile = getattr(user, "userprofile", None)
            if userprofile and getattr(userprofile, "role", None) == "JOB_SEEKER":
                applied = Application.objects.filter(candidate=user)
                applied_dict = {app.job_id: app for app in applied}
                for job in qs:
                    job.my_application = applied_dict.get(job.id)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        g = self.request.GET
        ctx['filter_form'] = JobFilterForm(g or None)
        ctx['selected_remote_types'] = g.getlist('remote_type')
        ctx['selected_visa'] = g.get('visa', '')
        ctx['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return ctx


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['application'] = Application.objects.filter(
                job=self.object, candidate=self.request.user
            ).first()
        # Recommendations are visible to the owning recruiter only
        recruiter = getattr(self.request.user, "recruiter_profile", None)
        if recruiter and self.object.recruiter_id == recruiter.id:
            ctx['job_recommendations'] = recommend_candidates_for_job(self.object, limit=5)
        return ctx

@login_required
@require_POST
def apply_to_job(request, pk):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'JOB_SEEKER':
        messages.error(request, "Only job seekers can apply to jobs.")
        return redirect("job_detail", pk=pk)
    
    job = get_object_or_404(Job, pk=pk)
    note = (request.POST.get("note") or "").strip()
    app, created = Application.objects.get_or_create(
        job=job,
        candidate=request.user,
        defaults={"status": "applied", "note": note},
    )
    if created:
        messages.success(request, "Your application has been submitted!")
    elif note:
        app.note = note
        app.save(update_fields=["note"])
        messages.info(request, "Your note has been updated for this application.")
    else:
        messages.warning(request, "You already applied to this job.")

    return redirect("job_detail", pk=job.pk)

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'

    def form_valid(self, form):
        recruiter = getattr(self.request.user, "recruiter_profile", None)
        if recruiter is None:
            form.add_error(None, "You must have a recruiter profile to post a job.")
            return self.form_invalid(form)
        form.instance.recruiter = recruiter
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        recruiter = getattr(self.request.user, "recruiter_profile", None)
        if obj.recruiter != recruiter:
            raise PermissionDenied("You can only edit your own jobs.")
        return obj


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = '/recruiters/dashboard/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        recruiter = getattr(self.request.user, "recruiter_profile", None)
        if obj.recruiter != recruiter:
            raise PermissionDenied("You can only delete your own jobs.")
        return obj

    def delete(self, request, *args, **kwargs):
        messages.success(request, f"Job '{self.get_object().title}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class MyApplicationsView(ListView):
    model = Application
    template_name = 'jobs/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return Application.objects.filter(candidate=self.request.user).select_related('job').order_by('-applied_at')