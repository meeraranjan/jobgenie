from django.urls import path
from .views import RecruiterSignupView, RecruiterDashboardView, BecomeRecruiterView

app_name = "recruiters"

urlpatterns = [
    path("signup/", RecruiterSignupView.as_view(), name="signup"),
    path("dashboard/", RecruiterDashboardView.as_view(), name="dashboard"),
    path("become/", BecomeRecruiterView.as_view(), name="become_recruiter"),
]

