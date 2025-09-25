from django.urls import path
from .views import RecruiterSignupView, RecruiterDashboardView

app_name = "recruiters"

urlpatterns = [
    path("signup/", RecruiterSignupView.as_view(), name="signup"),
    path("dashboard/", RecruiterDashboardView.as_view(), name="dashboard"),
]

