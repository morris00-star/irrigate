from rest_framework.throttling import SimpleRateThrottle


class DeviceRateThrottle(SimpleRateThrottle):
    scope = 'device'

    def get_cache_key(self, request, view):
        # Use the API key as the cache key for throttling
        if hasattr(request, 'auth') and request.auth:
            return f'device_{request.auth}'
        return None  # No throttling if no auth
