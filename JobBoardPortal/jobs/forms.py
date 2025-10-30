from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from .models import Job, Application, JobAlert
import os
import re


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'salary', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title',
                'minlength': '3',
                'maxlength': '200',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the job role and responsibilities',
                'minlength': '10',
                'required': True
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List the required qualifications and skills',
                'minlength': '10',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job location (e.g., New York, NY)',
                'minlength': '2',
                'maxlength': '100',
                'required': True
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1',
                'max': '9999999.99',
                'placeholder': 'Annual salary in INR',
                'required': True
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
        }
        help_texts = {
            'title': 'Enter a descriptive job title (3-200 characters)',
            'description': 'Provide detailed job description (minimum 10 characters)',
            'requirements': 'List required qualifications and skills (minimum 10 characters)',
            'location': 'Specify job location or "Remote" (2-100 characters)',
            'salary': 'Enter annual salary in INR (minimum ₹1)',
            'deadline': 'Select application deadline (must be in the future)'
        }
    
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline:
            if deadline <= timezone.now().date():
                raise ValidationError('Job deadline must be in the future.')
            # Check if deadline is not too far in the future (e.g., 2 years)
            max_deadline = timezone.now().date().replace(year=timezone.now().year + 2)
            if deadline > max_deadline:
                raise ValidationError('Job deadline cannot be more than 2 years in the future.')
        return deadline
    
    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary:
            if salary <= 0:
                raise ValidationError('Salary must be greater than 0.')
            if salary > 9999999.99:
                raise ValidationError('Salary cannot exceed $9,999,999.99.')
        return salary
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise ValidationError('Job title must be at least 3 characters long.')
            if len(title) > 200:
                raise ValidationError('Job title cannot exceed 200 characters.')
            # Check for inappropriate content (basic check)
            if re.search(r'\b(spam|scam|fake)\b', title.lower()):
                raise ValidationError('Job title contains inappropriate content.')
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            if len(description) < 10:
                raise ValidationError('Job description must be at least 10 characters long.')
        return description
    
    def clean_requirements(self):
        requirements = self.cleaned_data.get('requirements')
        if requirements:
            requirements = requirements.strip()
            if len(requirements) < 10:
                raise ValidationError('Job requirements must be at least 10 characters long.')
        return requirements
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise ValidationError('Location must be at least 2 characters long.')
        return location


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'required': True
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Write a cover letter explaining why you are interested in this position (optional)',
                'maxlength': '2000'
            }),
        }
        help_texts = {
            'resume': 'Upload your resume in PDF format (max 5MB)',
            'cover_letter': 'Optional cover letter (max 2000 characters)'
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if not resume:
            raise ValidationError('Resume is required.')
        
        # Check file extension
        ext = os.path.splitext(resume.name)[1].lower()
        if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
            raise ValidationError(
                f'Invalid file type. Allowed formats: {", ".join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}'
            )
        
        # Check file size
        if resume.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(
                f'File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'
            )
        
        # Basic filename validation
        if not re.match(r'^[a-zA-Z0-9._\-\s]+$', resume.name):
            raise ValidationError('Filename contains invalid characters. Use only letters, numbers, spaces, dots, hyphens, and underscores.')
        
        return resume
    
    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter:
            cover_letter = cover_letter.strip()
            if len(cover_letter) > 2000:
                raise ValidationError('Cover letter cannot exceed 2000 characters.')
        return cover_letter


class JobAlertForm(forms.ModelForm):
    class Meta:
        model = JobAlert
        fields = ['keyword', 'location']
        widgets = {
            'keyword': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter keywords (e.g., Python Developer, Marketing)',
                'minlength': '2',
                'maxlength': '100',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location (e.g., New York, Remote)',
                'minlength': '2',
                'maxlength': '100',
                'required': True
            }),
        }
        help_texts = {
            'keyword': 'Enter job-related keywords to search for (2-100 characters)',
            'location': 'Enter preferred job location or "Remote" (2-100 characters)'
        }
    
    def clean_keyword(self):
        keyword = self.cleaned_data.get('keyword')
        if keyword:
            keyword = keyword.strip()
            if len(keyword) < 2:
                raise ValidationError('Keyword must be at least 2 characters long.')
            if len(keyword) > 100:
                raise ValidationError('Keyword cannot exceed 100 characters.')
            # Basic validation for meaningful keywords
            if not re.match(r'^[a-zA-Z0-9\s\-\+\#\.]+$', keyword):
                raise ValidationError('Keyword contains invalid characters. Use only letters, numbers, spaces, and common symbols.')
        return keyword
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise ValidationError('Location must be at least 2 characters long.')
            if len(location) > 100:
                raise ValidationError('Location cannot exceed 100 characters.')
        return location


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class JobSearchForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by job title or keywords',
            'maxlength': '100'
        }),
        help_text='Enter keywords to search for jobs'
    )
    location = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by location',
            'maxlength': '100'
        }),
        help_text='Enter location to filter jobs'
    )
    
    def clean_keyword(self):
        keyword = self.cleaned_data.get('keyword')
        if keyword:
            keyword = keyword.strip()
            if keyword and not re.match(r'^[a-zA-Z0-9\s\-\+\#\.]+$', keyword):
                raise ValidationError('Search keyword contains invalid characters.')
        return keyword
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
        return location