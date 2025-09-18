from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.view_profile, name='view_profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
]
