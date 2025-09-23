from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Job
from django.db.models import Q

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10  # optional

class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html' 
    context_object_name = 'job'

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
        return qs