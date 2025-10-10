from django.urls import path
from .views import RecruiterSignupView, RecruiterDashboardView, BecomeRecruiterView, update_status, RecruiterApplicationDetailView

app_name = "recruiters"

urlpatterns = [
    path("signup/", RecruiterSignupView.as_view(), name="signup"),
    path("dashboard/", RecruiterDashboardView.as_view(), name="dashboard"),
    path("become/", BecomeRecruiterView.as_view(), name="become_recruiter"),
    path("update_status/<int:app_id>/<str:new_status>/", update_status, name="update_status"),
    path("application/<int:pk>/", RecruiterApplicationDetailView.as_view(), name="application_detail"),
]

