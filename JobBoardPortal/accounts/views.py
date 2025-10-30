from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from .forms import EmployerRegistrationForm, JobSeekerRegistrationForm, UserProfileForm


class CustomLoginView(LoginView):
    """Custom login view with role-based redirection"""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        # Redirect based on user type
        if hasattr(self.request.user, 'userprofile'):
            if self.request.user.userprofile.user_type == 'employer':
                return '/companies/profile/'  # Will be implemented in companies app
            else:
                return '/jobs/'  # Will be implemented in jobs app
        return '/'


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = '/'


def register_choice(request):
    """View to choose registration type"""
    return render(request, 'accounts/register_choice.html')


def employer_register(request):
    """Registration view for employers"""
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in as an employer.')
            return redirect('accounts:login')
    else:
        form = EmployerRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'Employer',
        'registration_type': 'employer'
    })


def jobseeker_register(request):
    """Registration view for job seekers"""
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}! You can now log in as a job seeker.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobSeekerRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'Job Seeker',
        'registration_type': 'jobseeker'
    })


@login_required
def profile_view(request):
    """View for displaying and updating user profile"""
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user_profile': user_profile
    })