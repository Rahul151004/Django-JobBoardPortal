from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Company
import os


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'logo', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your company...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company location'
            }),
        }
    
    def clean_logo(self):
        """Validate logo upload"""
        logo = self.cleaned_data.get('logo')
        
        if logo:
            # Check file extension
            ext = os.path.splitext(logo.name)[1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f'Invalid file type. Allowed formats: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}'
                )
            
            # Check file size
            if logo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f'File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'
                )
        
        return logo
    
    def clean_name(self):
        """Validate company name"""
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError('Company name must be at least 2 characters long.')
        return name
    
    def clean_description(self):
        """Validate company description"""
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            if len(description) < 10:
                raise ValidationError('Company description must be at least 10 characters long.')
        return description