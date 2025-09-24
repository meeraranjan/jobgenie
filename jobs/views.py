from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Job, Application

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10  # optional

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html' 
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            application = self.object.applications.filter(candidate=user).first()
            context['application'] = application
        
        return context

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        q = self.request.GET.get('search')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(skills__icontains=q) |
                Q(location__icontains=q)
            )
        
        if self.request.user.is_authenticated:
            from .models import Application
            applied = Application.objects.filter(candidate=self.request.user)
            applied_dict = {app.job_id: app for app in applied}
            for job in qs:
                job.my_application = applied_dict.get(job.id)
        return qs

@login_required
@require_POST
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    note = request.POST.get("note", "")
    
    existing = Application.objects.filter(job=job, candidate=request.user).first()
    if existing:
        messages.warning(request, "You already applied to this job.")
    else:
        Application.objects.create(
            job=job,
            candidate=request.user,
            note=note
        )
        messages.success(request, "Your application has been submitted!")

    return redirect("job_detail", pk=job.pk)