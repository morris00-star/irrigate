from django.utils.deprecation import MiddlewareMixin


class ThrottleHeaderMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 429 and hasattr(request, 'throttled'):
            if hasattr(request.throttled, 'wait'):
                response['Retry-After'] = int(request.throttled.wait)
        return response
