from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import Job, Application, JobAlert


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_company_link', 'get_employer', 'location', 'salary', 'get_application_count', 'posted_date', 'deadline', 'is_active']
    list_filter = ['posted_date', 'deadline', 'location', 'company__location', 'company__user__userprofile__user_type']
    search_fields = ['title', 'description', 'requirements', 'company__name', 'location', 'company__user__username']
    readonly_fields = ['posted_date', 'created_at', 'updated_at', 'get_application_count', 'get_days_remaining']
    date_hierarchy = 'posted_date'
    list_per_page = 25
    
    fieldsets = (
        ('Job Information', {
            'fields': ('company', 'title', 'description', 'requirements')
        }),
        ('Job Details', {
            'fields': ('location', 'salary', 'deadline', 'get_days_remaining')
        }),
        ('Statistics', {
            'fields': ('get_application_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('posted_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_company_link(self, obj):
        """Get company name with link to company admin"""
        url = reverse('admin:companies_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    get_company_link.short_description = 'Company'
    get_company_link.admin_order_field = 'company__name'
    
    def get_employer(self, obj):
        """Get employer username"""
        return obj.company.user.username
    get_employer.short_description = 'Employer'
    get_employer.admin_order_field = 'company__user__username'
    
    def get_application_count(self, obj):
        """Get number of applications for this job"""
        return obj.applications.count()
    get_application_count.short_description = 'Applications'
    
    def get_days_remaining(self, obj):
        """Get days remaining until deadline"""
        if obj.deadline:
            days = obj.days_until_deadline
            if days > 0:
                return f"{days} days"
            elif days == 0:
                return "Today"
            else:
                return "Expired"
        return "No deadline"
    get_days_remaining.short_description = 'Days Remaining'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def get_queryset(self, request):
        """Optimize queryset and filter for employers"""
        qs = super().get_queryset(request).select_related('company', 'company__user').prefetch_related('applications')
        
        # If user is an employer, show only their jobs
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'employer':
            if not request.user.is_superuser:
                qs = qs.filter(company__user=request.user)
        
        return qs
    
    def has_view_permission(self, request, obj=None):
        """Allow employers to view their own jobs"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.company.user:
                return True
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Allow employers to edit their own jobs"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.company.user:
                return True
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Allow employers to delete their own jobs"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.company.user:
                return True
        return super().has_delete_permission(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on user permissions"""
        form = super().get_form(request, obj, **kwargs)
        
        # If user is an employer, limit company field to their companies
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'employer':
            if not request.user.is_superuser:
                form.base_fields['company'].queryset = form.base_fields['company'].queryset.filter(user=request.user)
        
        return form


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['get_applicant_link', 'get_applicant_email', 'get_job_link', 'get_company', 'status', 'applied_date', 'get_resume_link']
    list_filter = ['status', 'applied_date', 'job__company', 'job__location', 'applicant__userprofile__user_type']
    search_fields = ['applicant__username', 'applicant__email', 'applicant__first_name', 'applicant__last_name', 'job__title', 'job__company__name']
    readonly_fields = ['applied_date', 'get_resume_link']
    date_hierarchy = 'applied_date'
    list_per_page = 25
    actions = ['mark_under_review', 'mark_shortlisted', 'mark_rejected']
    
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Details', {
            'fields': ('resume', 'get_resume_link', 'cover_letter')
        }),
        ('Timestamps', {
            'fields': ('applied_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_applicant_link(self, obj):
        """Get applicant username with link to user admin"""
        url = reverse('admin:auth_user_change', args=[obj.applicant.pk])
        return format_html('<a href="{}">{}</a>', url, obj.applicant.username)
    get_applicant_link.short_description = 'Applicant'
    get_applicant_link.admin_order_field = 'applicant__username'
    
    def get_applicant_email(self, obj):
        return obj.applicant.email
    get_applicant_email.short_description = 'Email'
    get_applicant_email.admin_order_field = 'applicant__email'
    
    def get_job_link(self, obj):
        """Get job title with link to job admin"""
        url = reverse('admin:jobs_job_change', args=[obj.job.pk])
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    get_job_link.short_description = 'Job'
    get_job_link.admin_order_field = 'job__title'
    
    def get_company(self, obj):
        return obj.job.company.name
    get_company.short_description = 'Company'
    get_company.admin_order_field = 'job__company__name'
    
    def get_resume_link(self, obj):
        """Display resume as downloadable link"""
        if obj.resume:
            return format_html('<a href="{}" target="_blank">Download Resume</a>', obj.resume.url)
        return 'No resume uploaded'
    get_resume_link.short_description = 'Resume'
    
    def get_queryset(self, request):
        """Optimize queryset and filter for employers"""
        qs = super().get_queryset(request).select_related('job', 'job__company', 'applicant', 'applicant__userprofile')
        
        # If user is an employer, show only applications for their jobs
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'employer':
            if not request.user.is_superuser:
                qs = qs.filter(job__company__user=request.user)
        
        return qs
    
    def has_view_permission(self, request, obj=None):
        """Allow employers to view applications for their jobs"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.job.company.user:
                return True
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Allow employers to change application status for their jobs"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.job.company.user:
                return True
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Restrict deletion - only superusers can delete applications"""
        return super().has_delete_permission(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on user permissions"""
        form = super().get_form(request, obj, **kwargs)
        
        # If user is an employer, limit job field to their jobs and make applicant readonly
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'employer':
            if not request.user.is_superuser:
                form.base_fields['job'].queryset = form.base_fields['job'].queryset.filter(company__user=request.user)
                if obj:  # Editing existing application
                    form.base_fields['job'].disabled = True
                    form.base_fields['applicant'].disabled = True
        
        return form
    
    # Admin actions for bulk status updates
    def mark_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} applications marked as Under Review.')
    mark_under_review.short_description = "Mark selected applications as Under Review"
    
    def mark_shortlisted(self, request, queryset):
        updated = queryset.update(status='shortlisted')
        self.message_user(request, f'{updated} applications marked as Shortlisted.')
    mark_shortlisted.short_description = "Mark selected applications as Shortlisted"
    
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications marked as Rejected.')
    mark_rejected.short_description = "Mark selected applications as Rejected"


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ['get_user_link', 'get_user_email', 'keyword', 'location', 'created_at']
    list_filter = ['created_at', 'location', 'user__userprofile__user_type']
    search_fields = ['user__username', 'user__email', 'keyword', 'location']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def get_user_link(self, obj):
        """Get user username with link to user admin"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    get_user_link.short_description = 'User'
    get_user_link.admin_order_field = 'user__username'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'user__userprofile')
    
    def has_view_permission(self, request, obj=None):
        """Allow job seekers to view their own alerts"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'jobseeker' and request.user == obj.user:
                return True
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Allow job seekers to edit their own alerts"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'jobseeker' and request.user == obj.user:
                return True
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Allow job seekers to delete their own alerts"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'jobseeker' and request.user == obj.user:
                return True
        return super().has_delete_permission(request, obj)
