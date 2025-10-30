def last_visited_job(request):
    """
    Context processor to add last visited job information to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        context['last_visited_job'] = {
            'job_id': request.session.get('last_visited_job_id'),
            'job_url': request.session.get('last_visited_job_url'),
        }
    
    return context


def user_navigation(request):
    """
    Context processor to add user-specific navigation information
    """
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile
        context['user_navigation'] = {
            'user_type': user_profile.user_type,
            'is_employer': user_profile.user_type == 'employer',
            'is_jobseeker': user_profile.user_type == 'jobseeker',
            'display_name': request.user.first_name or request.user.username,
        }
    
    return context