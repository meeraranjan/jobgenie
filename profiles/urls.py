from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('view_profile/', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path("create/", views.create_profile, name="create_profile"),
    path('jobseekers/', views.jobseeker_list, name='jobseeker_list'),
    path('jobseekers/<int:pk>/', views.jobseeker_detail, name='jobseeker_detail'),

]
