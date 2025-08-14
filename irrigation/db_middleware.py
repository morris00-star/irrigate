import os
from django.db import close_old_connections
from django.core.exceptions import MiddlewareNotUsed


IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production'


class DBConnectionMiddleware:
    def __init__(self, get_response):
        if IS_PRODUCTION:
            raise MiddlewareNotUsed
        self.get_response = get_response

    def __call__(self, request):
        close_old_connections()
        response = self.get_response(request)
        close_old_connections()
        return response
