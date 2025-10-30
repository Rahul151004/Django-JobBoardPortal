from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Job, JobAlert, JobAlertNotification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Job)
def check_job_alerts(sender, instance, created, **kwargs):
    """
    Check for matching job alerts when a new job is posted
    and notify users about relevant opportunities.
    """
    if not created:
        return  # Only process new jobs, not updates
    
    job = instance
    
    # Find matching job alerts
    matching_alerts = JobAlert.objects.filter(
        keyword__icontains=job.title
    ).filter(
        location__icontains=job.location
    )
    
    # Also check for partial matches in job description
    keyword_matches = JobAlert.objects.filter(
        keyword__icontains=job.title
    ) | JobAlert.objects.filter(
        keyword__in=[keyword.strip() for keyword in job.title.split()]
    )
    
    location_matches = JobAlert.objects.filter(
        location__icontains=job.location
    )
    
    # Combine all potential matches
    all_matches = (matching_alerts | keyword_matches | location_matches).distinct()
    
    notification_count = 0
    
    for alert in all_matches:
        try:
            # Check if the alert criteria actually match
            keyword_match = (
                alert.keyword.lower() in job.title.lower() or
                alert.keyword.lower() in job.description.lower() or
                any(word.lower() in job.title.lower() for word in alert.keyword.split())
            )
            
            location_match = (
                alert.location.lower() in job.location.lower() or
                job.location.lower() in alert.location.lower()
            )
            
            if keyword_match and location_match:
                # Send notification (you can implement email, in-app notifications, etc.)
                send_job_alert_notification(alert, job)
                notification_count += 1
                
        except Exception as e:
            logger.error(f"Error processing job alert {alert.id}: {str(e)}")
    
    if notification_count > 0:
        logger.info(f"Sent {notification_count} job alert notifications for job: {job.title}")


def send_job_alert_notification(alert, job):
    """
    Send notification to user about matching job.
    Creates an in-app notification and optionally sends email.
    """
    try:
        # Create in-app notification
        message = f"New job alert match: {job.title} at {job.company.name} in {job.location}"
        
        notification = JobAlertNotification.objects.create(
            user=alert.user,
            job=job,
            job_alert=alert,
            message=message
        )
        
        logger.info(f"Created notification {notification.id}: User {alert.user.username} - Job: {job.title} at {job.company.name}")
        
        # Optional: Send email notification
        if hasattr(settings, 'EMAIL_HOST') and alert.user.email:
            try:
                subject = f"Job Alert: {job.title} at {job.company.name}"
                email_message = f'''Hi {alert.user.first_name or alert.user.username},

A new job matching your alert "{alert.keyword}" in "{alert.location}" has been posted:

Job Title: {job.title}
Company: {job.company.name}
Location: {job.location}
Salary: ${job.salary:,.2f}

View the job: http://localhost:8000/jobs/{job.id}/

Best regards,
Job Board Portal Team'''
                
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [alert.user.email],
                    fail_silently=True,
                )
                logger.info(f"Sent email notification to {alert.user.email}")
            except Exception as e:
                logger.error(f"Error sending email notification: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating job alert notification: {str(e)}")
        return False