from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import os


def validate_image_file(file):
    """Validate that uploaded file is an image with allowed extension"""
    if not file:
        return
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Invalid file extension. Allowed extensions: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}'
        )
    
    # Check file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f'File size too large. Maximum size allowed: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'
        )


class Company(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'userprofile__user_type': 'employer'}
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='logos/', 
        blank=True, 
        null=True,
        validators=[validate_image_file]
    )
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
    
    def clean(self):
        """Custom validation for Company model"""
        super().clean()
        
        # Ensure user is an employer (only if user is set)
        if hasattr(self, 'user') and self.user:
            if hasattr(self.user, 'userprofile'):
                if self.user.userprofile.user_type != 'employer':
                    raise ValidationError('Only employers can create company profiles.')
            else:
                raise ValidationError('User must have a profile to create a company.')