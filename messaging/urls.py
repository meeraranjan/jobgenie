from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.messaging_home, name='messaging_home'),
    path('select/', views.select_user_to_message, name='select_user_to_message'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
]