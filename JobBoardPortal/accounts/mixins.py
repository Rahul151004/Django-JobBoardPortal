from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


class EmployerRequiredMixin(LoginRequiredMixin):
    """
    Mixin to ensure only employers can access the view.
    Inherits from LoginRequiredMixin to ensure user is authenticated first.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # First check if user is authenticated (handled by LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Check if user has a profile and is an employer
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'employer':
            raise PermissionDenied("Access denied. Only employers can access this page.")
        
        return super().dispatch(request, *args, **kwargs)


class JobSeekerRequiredMixin(LoginRequiredMixin):
    """
    Mixin to ensure only job seekers can access the view.
    Inherits from LoginRequiredMixin to ensure user is authenticated first.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # First check if user is authenticated (handled by LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Check if user has a profile and is a job seeker
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'jobseeker':
            raise PermissionDenied("Access denied. Only job seekers can access this page.")
        
        return super().dispatch(request, *args, **kwargs)


def employer_required(view_func):
    """
    Decorator for function-based views that require employer access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('accounts:login')
        
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'employer':
            raise PermissionDenied("Access denied. Only employers can access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def jobseeker_required(view_func):
    """
    Decorator for function-based views that require job seeker access.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('accounts:login')
        
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'jobseeker':
            raise PermissionDenied("Access denied. Only job seekers can access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def check_user_type(user):
    """
    Utility function to check user type.
    Returns 'employer', 'jobseeker', or None if not authenticated or no profile.
    """
    if not user.is_authenticated:
        return None
    
    if not hasattr(user, 'userprofile'):
        return None
    
    return user.userprofile.user_type


def is_employer(user):
    """Check if user is an employer"""
    return check_user_type(user) == 'employer'


def is_jobseeker(user):
    """Check if user is a job seeker"""
    return check_user_type(user) == 'jobseeker'