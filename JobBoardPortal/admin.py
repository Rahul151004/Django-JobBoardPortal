"""
Custom admin configuration for Job Board Portal
Handles role-based access control and permissions
"""

from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class JobBoardAdminSite(AdminSite):
    """Custom admin site with role-based access control"""
    
    site_header = "Job Board Portal Administration"
    site_title = "Job Board Admin"
    index_title = "Welcome to Job Board Portal Administration"
    
    def has_permission(self, request):
        """
        Check if user has permission to access admin site
        Allow superusers, staff, and employers with specific permissions
        """
        if not request.user.is_active:
            return False
        
        # Superusers always have access
        if request.user.is_superuser:
            return True
        
        # Staff users have access
        if request.user.is_staff:
            return True
        
        # Employers with admin permissions have limited access
        if hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer':
                # Check if employer has been granted admin permissions
                return request.user.has_perm('companies.view_company') or \
                       request.user.has_perm('jobs.view_job') or \
                       request.user.has_perm('jobs.view_application')
        
        return False
    
    def index(self, request, extra_context=None):
        """
        Customize admin index page based on user role
        """
        extra_context = extra_context or {}
        
        if hasattr(request.user, 'userprofile'):
            user_type = request.user.userprofile.user_type
            extra_context['user_type'] = user_type
            
            if user_type == 'employer':
                # Add employer-specific context
                from JobBoardPortal.companies.models import Company
                from JobBoardPortal.jobs.models import Job, Application
                
                try:
                    company = Company.objects.get(user=request.user)
                    jobs = Job.objects.filter(company=company)
                    applications = Application.objects.filter(job__company=company)
                    
                    extra_context.update({
                        'company': company,
                        'total_jobs': jobs.count(),
                        'active_jobs': jobs.filter(deadline__gt=timezone.now().date()).count(),
                        'total_applications': applications.count(),
                        'pending_applications': applications.filter(status='applied').count(),
                    })
                except Company.DoesNotExist:
                    extra_context['no_company'] = True
        
        return super().index(request, extra_context)


# Create custom admin site instance
job_board_admin = JobBoardAdminSite(name='job_board_admin')


def setup_employer_permissions():
    """
    Set up permissions for employer users to access admin
    This should be called during deployment or via management command
    """
    # Get or create employer group
    employer_group, created = Group.objects.get_or_create(name='Employers')
    
    if created:
        # Define permissions for employers
        permissions_to_add = [
            # Company permissions
            ('companies', 'company', 'view_company'),
            ('companies', 'company', 'add_company'),
            ('companies', 'company', 'change_company'),
            ('companies', 'company', 'delete_company'),
            
            # Job permissions
            ('jobs', 'job', 'view_job'),
            ('jobs', 'job', 'add_job'),
            ('jobs', 'job', 'change_job'),
            ('jobs', 'job', 'delete_job'),
            
            # Application permissions (view and change only)
            ('jobs', 'application', 'view_application'),
            ('jobs', 'application', 'change_application'),
        ]
        
        for app_label, model, codename in permissions_to_add:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                permission = Permission.objects.get(content_type=content_type, codename=codename)
                employer_group.permissions.add(permission)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                pass  # Permission doesn't exist yet, will be created during migration


def grant_employer_admin_access(user):
    """
    Grant admin access to an employer user
    """
    if hasattr(user, 'userprofile') and user.userprofile.user_type == 'employer':
        # Make user staff so they can access admin
        user.is_staff = True
        user.save()
        
        # Add to employer group
        employer_group, created = Group.objects.get_or_create(name='Employers')
        user.groups.add(employer_group)
        
        return True
    return False


def revoke_employer_admin_access(user):
    """
    Revoke admin access from an employer user
    """
    if hasattr(user, 'userprofile') and user.userprofile.user_type == 'employer':
        # Remove staff status
        user.is_staff = False
        user.save()
        
        # Remove from employer group
        try:
            employer_group = Group.objects.get(name='Employers')
            user.groups.remove(employer_group)
        except Group.DoesNotExist:
            pass
        
        return True
    return False