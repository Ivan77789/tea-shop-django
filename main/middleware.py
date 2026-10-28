from .models import SiteVisit


class SiteVisitLoggingMiddleware:
    """Save public page views for review in Django admin."""

    EXCLUDED_PREFIXES = ('/admin/', '/static/', '/media/')
    EXCLUDED_PATHS = {'/favicon.ico', '/robots.txt'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method in {'GET', 'HEAD'}
            and not request.path.startswith(self.EXCLUDED_PREFIXES)
            and request.path not in self.EXCLUDED_PATHS
        ):
            user = getattr(request, 'user', None)
            if not getattr(user, 'is_authenticated', False):
                user = None

            SiteVisit.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:1000],
                path=request.path[:500],
                method=request.method,
                status_code=response.status_code,
            )

        return response
