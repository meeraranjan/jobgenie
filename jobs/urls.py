from django.urls import path
from .views import JobListView, JobDetailView, apply_to_job, JobCreateView, JobUpdateView
from . import views

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path("<int:pk>/apply/", apply_to_job, name="apply_to_job"),
    path("new/", JobCreateView.as_view(), name="job_create"),
    path("<int:pk>/edit/", JobUpdateView.as_view(), name="job_edit"),
]