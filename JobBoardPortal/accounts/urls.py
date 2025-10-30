from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/employer/', views.employer_register, name='employer_register'),
    path('register/jobseeker/', views.jobseeker_register, name='jobseeker_register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
]