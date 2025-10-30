from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import UserProfile
import re
import os


class BaseRegistrationForm(UserCreationForm):
    """Base registration form with common fields"""
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address"
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Enter your first name"
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Enter your last name"
    )
    phone = forms.CharField(
        max_length=15, 
        required=True,
        help_text="Enter your phone number (e.g., +1-555-123-4567)"
    )
    location = forms.CharField(
        max_length=100, 
        required=True,
        help_text="Enter your city and state/country"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'location', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and validation attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'required': field.required
            })
            
            if field_name == 'username':
                field.widget.attrs.update({
                    'placeholder': 'Choose a username',
                    'pattern': '[a-zA-Z0-9_]{3,30}',
                    'title': 'Username must be 3-30 characters, letters, numbers, and underscores only'
                })
            elif field_name == 'first_name':
                field.widget.attrs.update({
                    'placeholder': 'First name',
                    'pattern': '[a-zA-Z\\s\'\\-]{2,30}',
                    'title': 'First name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only'
                })
            elif field_name == 'last_name':
                field.widget.attrs.update({
                    'placeholder': 'Last name',
                    'pattern': '[a-zA-Z\\s\'\\-]{2,30}',
                    'title': 'Last name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only'
                })
            elif field_name == 'email':
                field.widget.attrs.update({
                    'placeholder': 'Enter email address',
                    'type': 'email'
                })
            elif field_name == 'phone':
                field.widget.attrs.update({
                    'placeholder': 'Enter phone number',
                    'pattern': '[+]?[0-9\\s\\-\\(\\)]{10,15}',
                    'title': 'Enter a valid phone number'
                })
            elif field_name == 'location':
                field.widget.attrs.update({
                    'placeholder': 'Enter your location',
                    'minlength': '2'
                })
            elif field_name in ['password1', 'password2']:
                field.widget.attrs.update({
                    'placeholder': 'Enter password',
                    'minlength': '8'
                })
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, parentheses for validation
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^[+]?[0-9]{10,15}$', clean_phone):
                raise ValidationError('Enter a valid phone number (10-15 digits).')
        return phone
    
    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip()
            if not re.match(r'^[a-zA-Z\s]{2,30}$', first_name):
                raise ValidationError('First name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only.')
        return first_name
    
    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip()
            if not re.match(r'^[a-zA-Z\s]{2,30}$', last_name):
                raise ValidationError('Last name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only.')
        return last_name
    
    def clean_location(self):
        """Validate location"""
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise ValidationError('Location must be at least 2 characters long.')
        return location


class EmployerRegistrationForm(BaseRegistrationForm):
    """Registration form for employers"""
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update the UserProfile with employer-specific data
            user_profile = user.userprofile
            user_profile.user_type = 'employer'
            user_profile.phone = self.cleaned_data['phone']
            user_profile.location = self.cleaned_data['location']
            user_profile.save()
        
        return user


class JobSeekerRegistrationForm(BaseRegistrationForm):
    """Registration form for job seekers"""
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Update the UserProfile with job seeker-specific data
            user_profile = user.userprofile
            user_profile.user_type = 'jobseeker'
            user_profile.phone = self.cleaned_data['phone']
            user_profile.location = self.cleaned_data['location']
            user_profile.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Enter your first name"
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        help_text="Enter your last name"
    )
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address"
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'location', 'profile_picture']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter phone number',
                'pattern': '[+]?[0-9\\s\\-\\(\\)]{10,15}',
                'title': 'Enter a valid phone number'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your location',
                'minlength': '2'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        help_texts = {
            'phone': 'Enter your phone number (e.g., +1-555-123-4567)',
            'location': 'Enter your city and state/country',
            'profile_picture': 'Upload a profile picture (JPG, PNG, GIF, BMP - max 5MB)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
        # Add Bootstrap classes and validation attributes
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'pattern': '[a-zA-Z\\s\'\\-]{2,30}',
            'title': 'First name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'pattern': '[a-zA-Z\\s\'\\-]{2,30}',
            'title': 'Last name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email'
        })
    
    def clean_email(self):
        """Validate email uniqueness (excluding current user)"""
        email = self.cleaned_data.get('email')
        if email and self.instance and self.instance.user:
            if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
                raise ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, parentheses for validation
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^[+]?[0-9]{10,15}$', clean_phone):
                raise ValidationError('Enter a valid phone number (10-15 digits).')
        return phone
    
    def clean_first_name(self):
        """Validate first name"""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip()
            if not re.match(r'^[a-zA-Z\s]{2,30}$', first_name):
                raise ValidationError('First name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only.')
        return first_name
    
    def clean_last_name(self):
        """Validate last name"""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip()
            if not re.match(r'^[a-zA-Z\s]{2,30}$', last_name):
                raise ValidationError('Last name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only.')
        return last_name
    
    def clean_location(self):
        """Validate location"""
        location = self.cleaned_data.get('location')
        if location:
            location = location.strip()
            if len(location) < 2:
                raise ValidationError('Location must be at least 2 characters long.')
        return location
    
    def clean_profile_picture(self):
        """Validate profile picture upload"""
        profile_picture = self.cleaned_data.get('profile_picture')
        
        if profile_picture:
            # Check file extension
            ext = os.path.splitext(profile_picture.name)[1].lower()
            if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f'Invalid file type. Allowed formats: {", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)}'
                )
            
            # Check file size
            if profile_picture.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f'File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.1f}MB'
                )
        
        return profile_picture
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update User model fields
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile
