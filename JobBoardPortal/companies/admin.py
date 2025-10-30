from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_employer', 'get_employer_email', 'location', 'get_website_link', 'get_job_count', 'created_at']
    list_filter = ['location', 'created_at', 'user__userprofile__user_type']
    search_fields = ['name', 'user__username', 'user__email', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_job_count', 'get_logo_preview']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Company Information', {
            'fields': ('user', 'name', 'description', 'location')
        }),
        ('Contact & Branding', {
            'fields': ('website', 'logo', 'get_logo_preview')
        }),
        ('Statistics', {
            'fields': ('get_job_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_employer(self, obj):
        """Get employer username with link to user admin"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    get_employer.short_description = 'Employer'
    get_employer.admin_order_field = 'user__username'
    
    def get_employer_email(self, obj):
        return obj.user.email
    get_employer_email.short_description = 'Email'
    get_employer_email.admin_order_field = 'user__email'
    
    def get_website_link(self, obj):
        """Display website as clickable link"""
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
        return '-'
    get_website_link.short_description = 'Website'
    
    def get_job_count(self, obj):
        """Get number of jobs posted by this company"""
        return obj.jobs.count()
    get_job_count.short_description = 'Total Jobs'
    
    def get_logo_preview(self, obj):
        """Display logo preview in admin"""
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.logo.url)
        return 'No logo uploaded'
    get_logo_preview.short_description = 'Logo Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related('user', 'user__userprofile').prefetch_related('jobs')
    
    def has_view_permission(self, request, obj=None):
        """Allow employers to view their own company profiles"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.user:
                return True
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Allow employers to edit their own company profiles"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.user:
                return True
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Allow employers to delete their own company profiles"""
        if obj and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.user_type == 'employer' and request.user == obj.user:
                return True
        return super().has_delete_permission(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on user permissions"""
        form = super().get_form(request, obj, **kwargs)
        
        # If user is an employer (not superuser), limit user field to themselves
        if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'employer':
            if not request.user.is_superuser:
                form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(pk=request.user.pk)
                form.base_fields['user'].initial = request.user
        
        return form