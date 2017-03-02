# entry point for the Django loop
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barhop.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
