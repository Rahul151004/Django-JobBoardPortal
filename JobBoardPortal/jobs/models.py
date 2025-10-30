from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from JobBoardPortal.companies.models import Company
import os


def validate_pdf_file(file):
    """Validate that uploaded file is a PDF"""
    if not file:
        return
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f'Invalid file extension. Only PDF files are allowed.'
        )
    
    # Check file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'File size too large. Maximum size allowed: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'
        )


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ['-posted_date']
    
    def clean(self):
        """Custom validation for Job model"""
        super().clean()
        
        # Ensure deadline is in the future
        if self.deadline and self.deadline <= timezone.now().date():
            raise ValidationError('Job deadline must be in the future.')
    
    @property
    def is_active(self):
        """Check if job is still active (deadline not passed)"""
        return self.deadline > timezone.now().date()
    
    @property
    def days_until_deadline(self):
        """Calculate days remaining until deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return 0


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/', validators=[validate_pdf_file])
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    applied_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"
    
    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ['-applied_date']
        unique_together = ['job', 'applicant']  # Prevent duplicate applications
    
    def clean(self):
        """Custom validation for Application model"""
        super().clean()
        
        # Note: Validation is handled in the view layer to avoid RelatedObjectDoesNotExist
        # errors during form processing. The view ensures:
        # 1. Only job seekers can apply (via @jobseeker_required decorator)
        # 2. Jobs are still active (checked in apply_for_job view)
        # 3. No duplicate applications (checked in apply_for_job view)
        pass


class JobAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    keyword = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.keyword} in {self.location}"
    
    class Meta:
        verbose_name = "Job Alert"
        verbose_name_plural = "Job Alerts"
        ordering = ['-created_at']
    
    def clean(self):
        """Custom validation for JobAlert model"""
        super().clean()
        
        # Ensure user is a job seeker (only if user is set)
        if hasattr(self, 'user') and self.user:
            if hasattr(self.user, 'userprofile'):
                if self.user.userprofile.user_type != 'jobseeker':
                    raise ValidationError('Only job seekers can create job alerts.')
            else:
                raise ValidationError('User must have a profile to create job alerts.')
        
        # Ensure keyword and location are not empty
        if hasattr(self, 'keyword') and self.keyword and not self.keyword.strip():
            raise ValidationError('Keyword cannot be empty.')
        
        if hasattr(self, 'location') and self.location and not self.location.strip():
            raise ValidationError('Location cannot be empty.')


class JobAlertNotification(models.Model):
    """Model to store job alert notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_notifications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_alert = models.ForeignKey(JobAlert, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.job.title}"
    
    class Meta:
        verbose_name = "Job Alert Notification"
        verbose_name_plural = "Job Alert Notifications"
        ordering = ['-created_at']
