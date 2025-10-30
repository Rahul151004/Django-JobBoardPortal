"""
Views for the main JobBoardPortal application.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ValidationErrorReportView(View):
    """Endpoint for reporting client-side validation errors"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Log the validation error for monitoring
            logger.warning(
                f"Client-side validation error: {data.get('error', 'Unknown')}",
                extra={
                    'field': data.get('field'),
                    'url': data.get('url'),
                    'timestamp': data.get('timestamp'),
                    'user': request.user if request.user.is_authenticated else 'Anonymous',
                    'ip_address': self._get_client_ip(request)
                }
            )
            
            return JsonResponse({'status': 'logged'})
            
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error processing validation error report: {str(e)}")
            return JsonResponse({'error': 'Invalid request'}, status=400)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@require_POST
@login_required
def csrf_failure_view(request, reason=""):
    """Handle CSRF failures gracefully"""
    logger.warning(
        f"CSRF failure for user {request.user}: {reason}",
        extra={
            'user': request.user,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'path': request.path,
            'reason': reason
        }
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'error': 'CSRF Error',
            'message': 'Security token expired. Please refresh the page and try again.'
        }, status=403)
    
    from django.shortcuts import render
    return render(request, '403.html', {
        'csrf_error': True,
        'message': 'Security token expired. Please refresh the page and try again.'
    }, status=403)


