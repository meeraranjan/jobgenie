from django.urls import path
from . import views
from .views import JobListView, JobDetailView, apply_to_job

urlpatterns = [
    path('', JobListView.as_view(), name='job_list'),
    path('<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path("<int:pk>/apply/", apply_to_job, name="apply_to_job"),
]