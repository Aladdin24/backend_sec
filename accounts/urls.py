# accounts/urls.py
from django.urls import path
from accounts import views
from django.views.generic import TemplateView
urlpatterns = [

    # Pages HTML (publiques)
    path('activate/', views.activate_account_page, name='activate_page'),
    path('activation/success/', TemplateView.as_view(template_name='activation/activation_success.html'), name='activation_success'),


    # Login admin
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),


    # Dashboard Admin (HTML)
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/invite/', views.admin_create_user, name='admin_create_user'),
    path('admin/users/toggle/<user_id>/', views.admin_toggle_user_active, name='admin_toggle_user'),
]