# documents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    
    # Gestion des catégories (admin only)
    path('admin/categories/', views.admin_categories_list, name='admin_categories_list'),
    path('admin/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/categories/update/<uuid:category_id>/', views.admin_category_update, name='admin_category_update'),
    path('admin/categories/delete/<uuid:category_id>/', views.admin_category_delete, name='admin_category_delete'),
    
]