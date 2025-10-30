from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from .models import Job, Application, JobAlert, JobAlertNotification
from .forms import JobForm, ApplicationForm, JobAlertForm, JobSearchForm, ApplicationStatusForm
from JobBoardPortal.companies.models import Company
from JobBoardPortal.accounts.mixins import EmployerRequiredMixin, JobSeekerRequiredMixin, employer_required, jobseeker_required, is_employer, is_jobseeker


class JobListView(ListView):
    """Display all active jobs"""
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        # Filter out expired jobs
        queryset = Job.objects.filter(deadline__gt=timezone.now().date()).select_related('company')
        
        # Handle search functionality
        form = JobSearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            location = form.cleaned_data.get('location')
            
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(description__icontains=keyword) |
                    Q(requirements__icontains=keyword)
                )
            
            if location:
                queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-posted_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        return context


class JobDetailView(DetailView):
    """Display job details with company information"""
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        return Job.objects.select_related('company')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if user has already applied
        if self.request.user.is_authenticated:
            context['has_applied'] = Application.objects.filter(
                job=self.object,
                applicant=self.request.user
            ).exists()
        else:
            context['has_applied'] = False
        
        return context
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Store last visited job in session
        if request.user.is_authenticated:
            request.session['last_visited_job'] = {
                'id': self.object.id,
                'title': self.object.title,
                'company': self.object.company.name
            }
        
        return response


class JobCreateView(EmployerRequiredMixin, CreateView):
    """Create new job posting (employers only)"""
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job_list')
    
    def form_valid(self, form):
        # Get or create company for the employer
        try:
            company = Company.objects.get(user=self.request.user)
        except Company.DoesNotExist:
            messages.error(self.request, 'You must create a company profile before posting jobs.')
            return redirect('companies:profile')
        
        form.instance.company = company
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Post New Job'
        return context


class JobUpdateView(EmployerRequiredMixin, UpdateView):
    """Update job posting (job owner only)"""
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job_list')
    
    def get_queryset(self):
        # Only allow editing own jobs
        return Job.objects.filter(company__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Job updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Job'
        return context


class JobDeleteView(EmployerRequiredMixin, DeleteView):
    """Delete job posting (job owner only)"""
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('jobs:job_list')
    
    def get_queryset(self):
        # Only allow deleting own jobs
        return Job.objects.filter(company__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job deleted successfully!')
        return super().delete(request, *args, **kwargs)


@jobseeker_required
def apply_for_job(request, pk):
    """Apply for a job (job seekers only)"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if job is still active
    if not job.is_active:
        messages.error(request, 'This job posting has expired.')
        return redirect('jobs:job_detail', pk=pk)
    
    # Check if user has already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create application instance manually to avoid validation issues
                application = Application(
                    job=job,
                    applicant=request.user,
                    resume=form.cleaned_data['resume'],
                    cover_letter=form.cleaned_data.get('cover_letter', '')
                )
                application.save()
                messages.success(request, 'Application submitted successfully!')
                return redirect('jobs:job_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {
        'form': form,
        'job': job
    })


class ApplicationListView(JobSeekerRequiredMixin, ListView):
    """Display user's job applications"""
    model = Application
    template_name = 'jobs/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__company').order_by('-applied_date')


class JobAlertListView(JobSeekerRequiredMixin, ListView):
    """Display and manage job alerts"""
    model = JobAlert
    template_name = 'jobs/job_alert_list.html'
    context_object_name = 'alerts'
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = JobAlertForm()
        return context


@jobseeker_required
def create_job_alert(request):
    """Create a new job alert (job seekers only)"""
    if request.method == 'POST':
        form = JobAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            messages.success(request, 'Job alert created successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('jobs:job_alerts')


@jobseeker_required
def delete_job_alert(request, pk):
    """Delete a job alert"""
    alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, 'Job alert deleted successfully!')
    return redirect('jobs:job_alerts')


class NotificationListView(JobSeekerRequiredMixin, ListView):
    """Display job alert notifications for the user"""
    model = JobAlertNotification
    template_name = 'jobs/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20
    
    def get_queryset(self):
        return JobAlertNotification.objects.filter(user=self.request.user).select_related('job', 'job_alert', 'job__company')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mark all notifications as read when user views them
        JobAlertNotification.objects.filter(user=self.request.user, is_read=False).update(is_read=True)
        return context


@jobseeker_required
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    notification = get_object_or_404(JobAlertNotification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('jobs:job_detail', pk=notification.job.pk)


class EmployerApplicationListView(EmployerRequiredMixin, ListView):
    """Display applications for employer's jobs"""
    model = Application
    template_name = 'jobs/employer_applications.html'
    context_object_name = 'applications'
    paginate_by = 10
    
    def get_queryset(self):
        # Get applications for jobs posted by this employer
        return Application.objects.filter(
            job__company__user=self.request.user
        ).select_related('job', 'job__company', 'applicant', 'applicant__userprofile').order_by('-applied_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get summary statistics
        queryset = self.get_queryset()
        context['total_applications'] = queryset.count()
        context['pending_applications'] = queryset.filter(status='applied').count()
        context['under_review'] = queryset.filter(status='under_review').count()
        context['shortlisted'] = queryset.filter(status='shortlisted').count()
        context['rejected'] = queryset.filter(status='rejected').count()
        return context


@employer_required
def update_application_status(request, pk):
    """Update application status (employers only)"""
    application = get_object_or_404(Application, pk=pk)
    
    # Check if user owns the job
    if application.job.company.user != request.user:
        raise PermissionDenied("You can only update applications for your own jobs.")
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}.')
            return redirect('jobs:employer_applications')
    else:
        form = ApplicationStatusForm(instance=application)
    
    return render(request, 'jobs/update_application_status.html', {
        'form': form,
        'application': application
    })


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """View application details"""
    model = Application
    template_name = 'jobs/application_detail.html'
    context_object_name = 'application'
    
    def get_queryset(self):
        return Application.objects.select_related('job', 'job__company', 'applicant', 'applicant__userprofile')
    
    def dispatch(self, request, *args, **kwargs):
        application = self.get_object()
        
        # Check permissions: either the applicant or the employer can view
        if request.user == application.applicant:
            # Job seeker viewing their own application
            return super().dispatch(request, *args, **kwargs)
        elif (is_employer(request.user) and application.job.company.user == request.user):
            # Employer viewing application for their job
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied("You don't have permission to view this application.")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if current user is the employer
        context['is_employer'] = (
            is_employer(self.request.user) and 
            self.object.job.company.user == self.request.user
        )
        return context
