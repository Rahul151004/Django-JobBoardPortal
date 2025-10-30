from .models import JobAlertNotification


def notifications_context(request):
    """
    Add notification count to template context for authenticated jobseekers
    """
    context = {
        'unread_notifications_count': 0,
    }
    
    if request.user.is_authenticated:
        try:
            if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'jobseeker':
                context['unread_notifications_count'] = JobAlertNotification.objects.filter(
                    user=request.user,
                    is_read=False
                ).count()
        except Exception:
            # If there's any error, just return 0 count
            pass
    
    return context