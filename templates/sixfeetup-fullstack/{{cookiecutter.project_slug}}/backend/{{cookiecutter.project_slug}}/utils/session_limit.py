from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django_redis import get_redis_connection


class ActiveSessionMiddleware:
    """Record active session IPs in Redis and limit concurrent sessions."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = get_redis_connection("default")

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        response = self.get_response(request)
        return response

    def process_request(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            key = f"active_sessions:{user.pk}"
            ip = self._get_client_ip(request)
            pipe = self.redis.pipeline()
            pipe.hset(key, session_key, ip)
            pipe.hlen(key)
            pipe.expire(key, request.session.get_expiry_age())
            _, count, _ = pipe.execute()
            if count > 20:
                self.redis.hdel(key, session_key)
                logout(request)
                return HttpResponseForbidden("Too many active sessions")
        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

