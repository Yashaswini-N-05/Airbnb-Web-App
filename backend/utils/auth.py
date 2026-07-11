from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
import structlog

logger = structlog.get_logger(__name__)

class AutoUserAuthentication(BaseAuthentication):
    """
    Custom authentication class that automatically logs in a user.
    Prioritizes a query param '?user_id=...' or header 'X-User-Id'.
    If not specified, falls back to the first Guest user, or first Host user, or first user in the DB.
    """
    def authenticate(self, request):
        User = get_user_model()
        user_id = request.query_params.get("user_id") or request.query_params.get("userId")
        if not user_id:
            user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except Exception:
                # Try finding by username or other field if uuid parse fails
                try:
                    user = User.objects.get(username=user_id)
                except Exception:
                    pass

        if not user:
            user = User.objects.filter(role="guest").first() or User.objects.filter(role="host").first() or User.objects.first()
        
        if user:
            return (user, None)
        return None
