"""
Custom middleware for the Job Board Portal application.
"""

import logging
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        response['Content-Security-Policy'] = csp
        
        return response


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Enhanced error handling middleware"""
    
    def process_exception(self, request, exception):
        """Handle exceptions and provide appropriate responses"""
        
        # Get client IP for logging
        client_ip = self._get_client_ip(request)
        
        # Log the exception with additional context
        logger.error(
            f"Exception in {request.path}: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                'request': request,
                'user': getattr(request, 'user', None),
                'ip_address': client_ip,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'method': request.method,
                'post_data': dict(request.POST) if request.method == 'POST' else None
            }
        )
        
        # Handle specific exception types
        if isinstance(exception, PermissionDenied):
            context = {
                'message': str(exception) if str(exception) else 'You do not have permission to access this resource.'
            }
            return render(request, '403.html', context, status=403)
        
        elif isinstance(exception, Http404):
            # Log 404s for monitoring
            logger.warning(
                f"404 Not Found: {request.path}",
                extra={
                    'ip_address': client_ip,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'referer': request.META.get('HTTP_REFERER', '')
                }
            )
            return render(request, '404.html', status=404)
        
        elif isinstance(exception, ValidationError):
            # Log validation errors for security monitoring
            logger.warning(
                f"Validation error in {request.path}: {str(exception)}",
                extra={
                    'ip_address': client_ip,
                    'user': getattr(request, 'user', None),
                    'form_data': dict(request.POST) if request.method == 'POST' else None
                }
            )
            
            # For AJAX requests, return JSON error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'Validation Error',
                    'message': str(exception),
                    'field_errors': getattr(exception, 'error_dict', {})
                }, status=400)
            
            # For regular requests, redirect with error message
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, f'Validation Error: {str(exception)}')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        # Handle file upload errors
        elif 'upload' in str(exception).lower() or 'file' in str(exception).lower():
            logger.warning(
                f"File upload error in {request.path}: {str(exception)}",
                extra={
                    'ip_address': client_ip,
                    'user': getattr(request, 'user', None),
                    'files': list(request.FILES.keys()) if request.FILES else []
                }
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'File Upload Error',
                    'message': 'There was an error uploading your file. Please check the file format and size.'
                }, status=400)
        
        # Handle database errors
        from django.db import DatabaseError
        if isinstance(exception, DatabaseError):
            logger.critical(
                f"Database error in {request.path}: {str(exception)}",
                exc_info=True,
                extra={'ip_address': client_ip}
            )
            
            if not settings.DEBUG:
                return render(request, '500.html', {
                    'error_type': 'Database Error',
                    'message': 'We are experiencing technical difficulties. Please try again later.'
                }, status=500)
        
        # For development, let Django handle it
        if settings.DEBUG:
            return None
        
        # For production, show generic error page
        logger.critical(
            f"Unhandled exception in {request.path}: {type(exception).__name__}",
            exc_info=True,
            extra={'ip_address': client_ip}
        )
        
        return render(request, '500.html', {
            'error_type': 'Server Error',
            'message': 'An unexpected error occurred. Our team has been notified.'
        }, status=500)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class FileUploadSecurityMiddleware(MiddlewareMixin):
    """Security middleware for file uploads"""
    
    def process_request(self, request):
        """Check file uploads for security issues"""
        
        if request.method == 'POST' and request.FILES:
            for field_name, uploaded_file in request.FILES.items():
                try:
                    self._validate_uploaded_file(uploaded_file)
                except ValidationError as e:
                    logger.warning(
                        f"File upload validation failed for {field_name}: {str(e)}",
                        extra={'request': request}
                    )
                    # Let the form validation handle the error
                    pass
        
        return None
    
    def _validate_uploaded_file(self, uploaded_file):
        """Validate uploaded file for security"""
        
        # Check file size
        if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError('File too large')
        
        # Check filename for dangerous characters
        import re
        if not re.match(r'^[a-zA-Z0-9._\-\s]+$', uploaded_file.name):
            raise ValidationError('Invalid filename')
        
        # Check for dangerous file extensions
        import os
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', 
            '.js', '.jar', '.php', '.asp', '.aspx', '.jsp'
        ]
        
        if ext in dangerous_extensions:
            raise ValidationError('File type not allowed')
        
        # Basic content type validation
        if hasattr(uploaded_file, 'content_type'):
            dangerous_types = [
                'application/x-executable',
                'application/x-msdownload',
                'text/javascript',
                'application/javascript'
            ]
            
            if uploaded_file.content_type in dangerous_types:
                raise ValidationError('File content type not allowed')


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log important requests for security monitoring"""
    
    def process_request(self, request):
        """Log security-relevant requests"""
        
        # Log authentication attempts
        if request.path in ['/accounts/login/', '/accounts/register/']:
            logger.info(
                f"Authentication attempt: {request.method} {request.path}",
                extra={
                    'ip_address': self._get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'user': getattr(request, 'user', None)
                }
            )
        
        # Log file upload attempts
        if request.method == 'POST' and request.FILES:
            logger.info(
                f"File upload attempt: {request.path}",
                extra={
                    'ip_address': self._get_client_ip(request),
                    'files': list(request.FILES.keys()),
                    'user': getattr(request, 'user', None)
                }
            )
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFFailureMiddleware(MiddlewareMixin):
    """Handle CSRF failures gracefully"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Handle CSRF token failures"""
        return None
    
    def process_exception(self, request, exception):
        """Handle CSRF failures"""
        from django.middleware.csrf import CsrfViewMiddleware
        
        if isinstance(exception, Exception) and 'CSRF' in str(exception):
            logger.warning(
                f"CSRF failure: {request.path}",
                extra={
                    'ip_address': self._get_client_ip(request),
                    'user': getattr(request, 'user', None)
                }
            )
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'CSRF Error',
                    'message': 'Security token expired. Please refresh the page and try again.'
                }, status=403)
            
            # For regular requests
            from django.shortcuts import render
            return render(request, '403.html', {
                'csrf_error': True,
                'message': 'Security token expired. Please refresh the page and try again.'
            }, status=403)
        
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip