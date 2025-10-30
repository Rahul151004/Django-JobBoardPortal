"""
Custom validators for the Job Board Portal application.
"""

import os
import re
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.core.files.uploadedfile import UploadedFile


@deconstructible
class FileExtensionValidator:
    """Validate file extensions"""
    
    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def __call__(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    f'Invalid file extension. Allowed: {", ".join(self.allowed_extensions)}'
                )


@deconstructible
class FileSizeValidator:
    """Validate file size"""
    
    def __init__(self, max_size):
        self.max_size = max_size
    
    def __call__(self, value):
        if value and hasattr(value, 'size'):
            if value.size > self.max_size:
                max_mb = self.max_size / (1024 * 1024)
                raise ValidationError(
                    f'File too large. Maximum size: {max_mb:.1f}MB'
                )


@deconstructible
class FileContentTypeValidator:
    """Validate file content type"""
    
    def __init__(self, allowed_types):
        self.allowed_types = allowed_types
    
    def __call__(self, value):
        if value and hasattr(value, 'content_type'):
            if value.content_type not in self.allowed_types:
                raise ValidationError(
                    f'Invalid file type. Allowed: {", ".join(self.allowed_types)}'
                )


@deconstructible
class FilenameValidator:
    """Validate filename for security"""
    
    def __call__(self, value):
        if value:
            filename = os.path.basename(value.name)
            # Check for dangerous characters
            if not re.match(r'^[a-zA-Z0-9._\-\s]+$', filename):
                raise ValidationError(
                    'Filename contains invalid characters. Use only letters, numbers, spaces, dots, hyphens, and underscores.'
                )
            
            # Check for dangerous extensions or patterns
            dangerous_patterns = [
                r'\.exe$', r'\.bat$', r'\.cmd$', r'\.com$', r'\.scr$',
                r'\.vbs$', r'\.js$', r'\.jar$', r'\.php$', r'\.asp$'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, filename.lower()):
                    raise ValidationError('File type not allowed for security reasons.')


def validate_phone_number(value):
    """Validate phone number format"""
    if value:
        # Remove spaces, dashes, parentheses for validation
        clean_phone = re.sub(r'[\s\-\(\)]', '', value)
        if not re.match(r'^[+]?[0-9]{10,15}$', clean_phone):
            raise ValidationError('Enter a valid phone number (10-15 digits).')


def validate_name(value):
    """Validate name fields (first name, last name)"""
    if value:
        value = value.strip()
        if not re.match(r'^[a-zA-Z\s\'\-]{2,30}$', value):
            raise ValidationError('Name must be 2-30 characters, letters, spaces, apostrophes, and hyphens only.')


def validate_job_title(value):
    """Validate job title"""
    if value:
        value = value.strip()
        if len(value) < 3:
            raise ValidationError('Job title must be at least 3 characters long.')
        if len(value) > 200:
            raise ValidationError('Job title cannot exceed 200 characters.')
        
        # Check for inappropriate content (basic check)
        inappropriate_words = ['spam', 'scam', 'fake', 'fraud']
        for word in inappropriate_words:
            if word in value.lower():
                raise ValidationError('Job title contains inappropriate content.')


def validate_salary(value):
    """Validate salary amount"""
    if value is not None:
        if value <= 0:
            raise ValidationError('Salary must be greater than 0.')
        if value > 9999999.99:
            raise ValidationError('Salary cannot exceed $9,999,999.99.')


def validate_future_date(value):
    """Validate that date is in the future"""
    if value:
        from django.utils import timezone
        if value <= timezone.now().date():
            raise ValidationError('Date must be in the future.')
        
        # Check if date is not too far in the future (2 years)
        max_date = timezone.now().date().replace(year=timezone.now().year + 2)
        if value > max_date:
            raise ValidationError('Date cannot be more than 2 years in the future.')


def validate_search_query(value):
    """Validate search query for security"""
    if value:
        value = value.strip()
        # Basic XSS prevention
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        for char in dangerous_chars:
            if char.lower() in value.lower():
                raise ValidationError('Search query contains invalid characters.')


def validate_text_content(value, min_length=10, max_length=None):
    """Validate text content (descriptions, requirements, etc.)"""
    if value:
        value = value.strip()
        if len(value) < min_length:
            raise ValidationError(f'Content must be at least {min_length} characters long.')
        
        if max_length and len(value) > max_length:
            raise ValidationError(f'Content cannot exceed {max_length} characters.')


# Predefined validators for common use cases
image_file_validator = FileExtensionValidator(settings.ALLOWED_IMAGE_EXTENSIONS)
document_file_validator = FileExtensionValidator(settings.ALLOWED_DOCUMENT_EXTENSIONS)
file_size_validator = FileSizeValidator(settings.MAX_UPLOAD_SIZE)
filename_validator = FilenameValidator()

# Content type validators
image_content_validator = FileContentTypeValidator(settings.ALLOWED_IMAGE_TYPES)
document_content_validator = FileContentTypeValidator(settings.ALLOWED_DOCUMENT_TYPES)


def validate_no_malicious_content(value):
    """Validate that text content doesn't contain malicious code"""
    if value:
        value_lower = value.lower()
        
        # Check for script tags and javascript
        dangerous_patterns = [
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
            r'<form',
            r'<input',
            r'<link',
            r'<meta'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower):
                raise ValidationError('Content contains potentially dangerous code.')
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'\b(select|insert|update|delete|drop|create|alter|exec|union)\b.*\b(from|where|into)\b',
            r'(--|\/\*|\*\/)',
            r"(\b(or|and)\b.*=.*')",
            r"'.*(\bor\b|\band\b).*'"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value_lower):
                raise ValidationError('Content contains invalid characters.')


def validate_email_security(value):
    """Enhanced email validation with security checks"""
    if value:
        # Basic format validation
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            raise ValidationError('Enter a valid email address.')
        
        # Length validation
        if len(value) > 254:
            raise ValidationError('Email address is too long.')
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        for char in dangerous_chars:
            if char in value:
                raise ValidationError('Email contains invalid characters.')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'^\.|\.$',  # Starting or ending with dot
            r'@.*@',  # Multiple @ symbols
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value):
                raise ValidationError('Email format is invalid.')


def validate_url_security(value):
    """Validate URL with security checks"""
    if value:
        # Basic URL validation
        if not re.match(r'^https?://', value):
            raise ValidationError('URL must start with http:// or https://')
        
        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'data:', 'file:', 'ftp:']
        for protocol in dangerous_protocols:
            if value.lower().startswith(protocol):
                raise ValidationError('URL protocol not allowed.')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'\.\./',  # Directory traversal
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value.lower()):
                raise ValidationError('URL contains invalid content.')


def validate_password_strength(value):
    """Validate password strength"""
    if value:
        errors = []
        
        if len(value) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Z]', value):
            errors.append('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', value):
            errors.append('Password must contain at least one lowercase letter.')
        
        if not re.search(r'\d', value):
            errors.append('Password must contain at least one number.')
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '12345678', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', '1234567890'
        ]
        
        if value.lower() in weak_passwords:
            errors.append('Password is too common. Please choose a stronger password.')
        
        if errors:
            raise ValidationError(' '.join(errors))


@deconstructible
class ComprehensiveFileValidator:
    """Comprehensive file validation combining multiple checks"""
    
    def __init__(self, allowed_extensions, allowed_types, max_size, check_content=True):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        self.allowed_types = allowed_types
        self.max_size = max_size
        self.check_content = check_content
    
    def __call__(self, value):
        if not value:
            return
        
        # File extension validation
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f'Invalid file extension. Allowed: {", ".join(self.allowed_extensions)}'
            )
        
        # File size validation
        if hasattr(value, 'size') and value.size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            raise ValidationError(f'File too large. Maximum size: {max_mb:.1f}MB')
        
        # Content type validation
        if hasattr(value, 'content_type') and value.content_type not in self.allowed_types:
            raise ValidationError(
                f'Invalid file type. Allowed: {", ".join(self.allowed_types)}'
            )
        
        # Filename security validation
        filename = os.path.basename(value.name)
        if not re.match(r'^[a-zA-Z0-9._\-\s]+$', filename):
            raise ValidationError(
                'Filename contains invalid characters. Use only letters, numbers, spaces, dots, hyphens, and underscores.'
            )
        
        # Check for dangerous file extensions
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', '.jar',
            '.php', '.asp', '.aspx', '.jsp', '.sh', '.ps1'
        ]
        
        if ext in dangerous_extensions:
            raise ValidationError('File type not allowed for security reasons.')
        
        # Content validation for text files (if enabled)
        if self.check_content and ext in ['.txt', '.csv']:
            try:
                content = value.read().decode('utf-8')
                validate_no_malicious_content(content)
                value.seek(0)  # Reset file pointer
            except UnicodeDecodeError:
                pass  # Binary files are OK
            except Exception as e:
                raise ValidationError('File content validation failed.')


# Predefined comprehensive validators
comprehensive_image_validator = ComprehensiveFileValidator(
    settings.ALLOWED_IMAGE_EXTENSIONS,
    settings.ALLOWED_IMAGE_TYPES,
    settings.MAX_UPLOAD_SIZE,
    check_content=False
)

comprehensive_document_validator = ComprehensiveFileValidator(
    settings.ALLOWED_DOCUMENT_EXTENSIONS,
    settings.ALLOWED_DOCUMENT_TYPES,
    settings.MAX_UPLOAD_SIZE,
    check_content=True
)