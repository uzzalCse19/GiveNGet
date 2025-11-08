from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/request/', views.request_post, name='request_post'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    
]