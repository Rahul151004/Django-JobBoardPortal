from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and details
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    
    # Job management (employers only)
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/edit/', views.JobUpdateView.as_view(), name='job_edit'),
    path('<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    
    # Job applications (job seekers only)
    path('<int:pk>/apply/', views.apply_for_job, name='apply_job'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    
    # Job alerts (job seekers only)
    path('alerts/', views.JobAlertListView.as_view(), name='job_alerts'),
    path('alerts/create/', views.create_job_alert, name='create_job_alert'),
    path('alerts/<int:pk>/delete/', views.delete_job_alert, name='delete_job_alert'),
    
    # Notifications (job seekers only)
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Employer application management
    path('employer/applications/', views.EmployerApplicationListView.as_view(), name='employer_applications'),
    path('applications/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:pk>/detail/', views.ApplicationDetailView.as_view(), name='application_detail'),
]