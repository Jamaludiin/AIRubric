from . import views
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register/', views.register, name='users-register'),  # Register route
    #path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='users-login'),  # 
    path('login/', views.user_login, name='users-login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='users-logout'),  # 
    path('logout/', views.user_logout, name='users-logout'),

]

