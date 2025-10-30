from django.utils.deprecation import MiddlewareMixin


class LastVisitedJobMiddleware(MiddlewareMixin):
    """
    Middleware to track the last visited job page for authenticated users
    """
    
    def process_request(self, request):
        # Only track for authenticated users
        if request.user.is_authenticated:
            # Check if this is a job detail page (will be implemented when jobs app is created)
            # For now, we'll set up the structure
            if request.path.startswith('/jobs/') and request.path != '/jobs/':
                # Extract job ID from URL pattern like /jobs/123/
                path_parts = request.path.strip('/').split('/')
                if len(path_parts) >= 2 and path_parts[1].isdigit():
                    job_id = path_parts[1]
                    request.session['last_visited_job_id'] = job_id
                    request.session['last_visited_job_url'] = request.path
        
        return None
    
    def get_last_visited_job(self, request):
        """
        Helper method to get the last visited job information
        """
        if request.user.is_authenticated:
            return {
                'job_id': request.session.get('last_visited_job_id'),
                'job_url': request.session.get('last_visited_job_url'),
            }
        return None