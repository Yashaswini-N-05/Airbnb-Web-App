"""
DRF exception handler: returns the default DRF response and records structured logs.
"""

import structlog
from rest_framework.views import exception_handler as drf_exception_handler

logger = structlog.get_logger("tripnest.drf")


def drf_structlog_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    request = context.get("request")
    view = context.get("view")
    view_name = view.__class__.__name__ if view is not None else None

    user_id = None
    if request is not None and getattr(request, "user", None) is not None:
        if request.user.is_authenticated:
            user_id = str(request.user.pk)

    path = getattr(request, "path", None) if request is not None else None
    method = getattr(request, "method", None) if request is not None else None

    detail = getattr(exc, "detail", None)
    if detail is None:
        detail = str(exc)

    if response is not None:
        if response.status_code >= 500:
            logger.error(
                "drf_server_error",
                status_code=response.status_code,
                exc_type=exc.__class__.__name__,
                view=view_name,
                path=path,
                method=method,
                user_id=user_id,
                detail=detail,
            )
        elif response.status_code >= 400:
            logger.warning(
                "drf_client_error",
                status_code=response.status_code,
                exc_type=exc.__class__.__name__,
                view=view_name,
                path=path,
                method=method,
                user_id=user_id,
                detail=detail,
            )
    else:
        logger.error(
            "drf_unhandled_exception",
            exc_type=exc.__class__.__name__,
            view=view_name,
            path=path,
            method=method,
            user_id=user_id,
            exc_info=(type(exc), exc, exc.__traceback__),
        )

    return response
