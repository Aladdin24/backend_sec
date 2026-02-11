# documents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('upload/', views.upload_document, name='upload_document'),
    path('list/', views.list_documents, name='list_documents'),
    path('share/<uuid:document_id>/', views.share_document, name='share_document'),
    path('categories/', views.list_categories, name='list-categories'),
    path('users/', views.list_users, name='list-users'),
    path('download/<uuid:document_id>/', views.download_document, name='download_document'),
    path('delete/<uuid:document_id>/', views.delete_document, name='delete_document'),


    # Upload endpoints (MinIO)
    path('upload/prepare/', views.prepare_upload, name='prepare_upload'),
    path('upload/confirm/', views.confirm_upload, name='confirm_upload'),

    path('categories_nw/create/', views.create_category, name='create_category'),
    
]