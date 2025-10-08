from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from functools import reduce
import operator
from django.contrib import messages

from .models import Job, Application
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import JobForm
from django.core.exceptions import PermissionDenied
from .forms import JobFilterForm
from math import radians, sin, cos, asin, sqrt

def haversine_km(lat1, lng1, lat2, lng2):
    """Return distance (km) between two lat/long points"""
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

    def get_queryset(self):
        qs = Job.objects.all().order_by('-created_at')
        g = self.request.GET

        title = g.get('title')
        if title:
            qs = qs.filter(title__icontains=title)

        loc = g.get('location')
        if loc:
            qs = qs.filter(location__icontains=loc)

        skills = g.get('skills')
        if skills:
            raw = skills.replace(',', ' ')
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

        lat = g.get('user_lat')
        lng = g.get('user_lng')
        radius = g.get('radius_km')
        if lat and lng and radius:
            try:
                user_lat = float(lat)
                user_lng = float(lng)
                radius_km = float(radius)
                with_coords = qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
                keep_ids = []
                for j in with_coords.only('id', 'latitude', 'longitude'):
                    d = haversine_km(user_lat, user_lng, j.latitude, j.longitude)
                    if d is not None and d <= radius_km:
                        keep_ids.append(j.id)
                qs = qs.filter(id__in=keep_ids)
            except ValueError:
                pass

        if self.request.user.is_authenticated:
            applied = Application.objects.filter(candidate=self.request.user)
            by_job_id = {app.job_id: app for app in applied}
            for job in qs:
                job.my_application = by_job_id.get(job.id)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        g = self.request.GET
        ctx['filter_form'] = JobFilterForm(g or None)
        ctx['selected_remote_types'] = g.getlist('remote_type')
        ctx['selected_visa'] = g.get('visa', '')
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
        return ctx


@login_required
@require_POST
def apply_to_job(request, pk):
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
