# accounts/api/urls.py
from django.urls import path
from .views import  RegisterPublicKeyView, get_user_by_email, profile_view, update_must_change_password_flag, update_profile_view, change_password_view


urlpatterns = [
   

    # API Endpoints (JSON)
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('password/change/', change_password_view, name='change_password'),
    path('users/public-key/', RegisterPublicKeyView.as_view()),
    path('users/must-change-password/', update_must_change_password_flag, name='update_must_change_password_flag'),
    path('users/by-email/<str:email>/', get_user_by_email, name='get_user_by_email'),
    
]