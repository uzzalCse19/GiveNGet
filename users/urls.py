from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import register, custom_logout

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
   # urls.py
    path('logout/', custom_logout, name='logout'),

    # Add registration view as needed
    path('register/', register, name='register'),
]