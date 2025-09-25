from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from functools import reduce
import operator

from .models import Job, Application
from .forms import JobFilterForm


class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        qs = Job.objects.all().order_by('-created_at')
        g = self.request.GET

        if g.get('title'):
            qs = qs.filter(title__icontains=g['title'])

        if g.get('location'):
            qs = qs.filter(location__icontains=g['location'])

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
    if not created and note:
        app.note = note
        app.save(update_fields=["note"])
    return redirect('job_detail', pk=job.pk) 