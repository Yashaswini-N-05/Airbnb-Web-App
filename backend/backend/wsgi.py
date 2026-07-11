import os

from django.core.wsgi import get_wsgi_application

from backend import observability

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

observability.instrument()

application = get_wsgi_application()
