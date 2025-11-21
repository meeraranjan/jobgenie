from django.urls import path
from . import views
from .views import (
    RecruiterSignupView, RecruiterDashboardView, BecomeRecruiterView,
    update_status, RecruiterApplicationDetailView, CandidateSearchView,
    RecruiterProfileView, RecruiterEditView,
    SavedSearchListView, SavedSearchDetailView,
    save_candidate_search, email_saved_search_matches,
)

app_name = "recruiters"

urlpatterns = [
    path("signup/", RecruiterSignupView.as_view(), name="signup"),
    path("dashboard/", RecruiterDashboardView.as_view(), name="dashboard"),
    path("candidates/", CandidateSearchView.as_view(), name="candidate_search"),
    path("become/", BecomeRecruiterView.as_view(), name="become_recruiter"),
    path("update_status/<int:app_id>/<str:new_status>/", update_status, name="update_status"),
    path('email/<int:application_id>/', views.send_candidate_email, name='send_candidate_email'),
    path("application/<int:pk>/", RecruiterApplicationDetailView.as_view(), name="application_detail"),
    path("profile/edit/", RecruiterEditView.as_view(), name="edit_profile"),
    path("profile/<str:username>/", RecruiterProfileView.as_view(), name="profile"),
        path(
        "saved-searches/",
        SavedSearchListView.as_view(),
        name="saved_search_list",
    ),
    path(
        "saved-searches/<int:pk>/",
        SavedSearchDetailView.as_view(),
        name="saved_search_detail",
    ),
    path("saved-searches/<int:pk>/delete/", views.delete_saved_search, name="saved_search_delete"),
    path(
        "candidates/save-search/",
        save_candidate_search,
        name="save_candidate_search",
    ),
    path(
        "saved-searches/<int:pk>/email/",
        email_saved_search_matches,
        name="saved_search_email",
    ),
]

