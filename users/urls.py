from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from users.views import custom_logout, register

urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    # urls.py
    path('resend-activation/', views.resend_activation, name='resend_activation'),

    path('logout/', custom_logout, name='logout'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
]