from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseNotFound
from django.conf import settings


class ThrottleHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 429 and hasattr(request, 'throttled'):
            if hasattr(request.throttled, 'wait'):
                response['Retry-After'] = int(request.throttled.wait)
        return response


class BlockMediaRequestsInProduction:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is a media request in production
        if (settings.IS_PRODUCTION and
                request.path.startswith(settings.MEDIA_URL) and
                not request.path.startswith(f"{settings.MEDIA_URL}profile_pics/")):
            return HttpResponseNotFound("Media files are served through Cloudinary")

        response = self.get_response(request)
        return response

