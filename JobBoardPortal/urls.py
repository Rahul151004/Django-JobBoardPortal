"""
URL configuration for JobBoardPortal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import ValidationErrorReportView, csrf_failure_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # Redirect home page to job listings
    path('', RedirectView.as_view(url='/jobs/', permanent=False), name='home'),
    # URL patterns for apps
    path('accounts/', include('JobBoardPortal.accounts.urls')),
    path('jobs/', include('JobBoardPortal.jobs.urls')),
    path('companies/', include('JobBoardPortal.companies.urls')),
    # Validation and error handling endpoints
    path('api/validation-error/', ValidationErrorReportView.as_view(), name='validation_error_report'),
    path('csrf-failure/', csrf_failure_view, name='csrf_failure'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
