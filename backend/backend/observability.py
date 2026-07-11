import structlog
from django.contrib.auth import get_user
from opentelemetry.instrumentation.django import DjangoInstrumentor

logger = structlog.get_logger(__name__)

def _instrument_django():
    def response_hook(span, request, response):
        # 1. Check if user is already attached (most common case)
        user = getattr(request, "user", None)

        # 2. If not attached, only use get_user if the request has a session
        # This prevents the AttributeError during early-exit requests
        if user is None and hasattr(request, "session"):
            user = get_user(request)

        # 3. Safely attach attributes if user is authenticated
        if user and user.is_authenticated:
            span.set_attribute("enduser.id", str(user.pk))
            
            email_field = getattr(user, "get_email_field_name", lambda: "email")()
            email = getattr(user, email_field, None)
            if email:
                span.set_attribute("enduser.email", email)

    # CRITICAL: Pass the hook during instrumentation
    DjangoInstrumentor().instrument(response_hook=response_hook)
    logger.info("OpenTelemetry Django initialized with user tracking")

def instrument():
    _instrument_django()
