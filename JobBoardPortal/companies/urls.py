from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('profile/', views.CompanyProfileView.as_view(), name='profile'),
    path('<int:company_id>/', views.company_detail, name='detail'),
]