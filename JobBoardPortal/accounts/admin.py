from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('user_type', 'phone', 'location', 'profile_picture')


class UserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'userprofile__user_type', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'userprofile__phone')
    date_hierarchy = 'date_joined'
    
    def get_user_type(self, obj):
        """Get user type from profile"""
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.get_user_type_display()
        return 'No Profile'
    get_user_type.short_description = 'User Type'
    get_user_type.admin_order_field = 'userprofile__user_type'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    list_display = ('get_username', 'get_email', 'user_type', 'phone', 'location', 'get_date_joined')
    list_filter = ('user_type', 'user__date_joined', 'user__is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone', 'location')
    readonly_fields = ('user', 'get_date_joined')
    list_per_page = 25
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'get_date_joined')
        }),
        ('Profile Information', {
            'fields': ('user_type', 'phone', 'location', 'profile_picture')
        }),
    )
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_date_joined(self, obj):
        return obj.user.date_joined
    get_date_joined.short_description = 'Date Joined'
    get_date_joined.admin_order_field = 'user__date_joined'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Customize admin site headers
admin.site.site_header = "Job Board Portal Administration"
admin.site.site_title = "Job Board Admin"
admin.site.index_title = "Welcome to Job Board Portal Administration"