"""
WSGI config for barhop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

# import os
#
# from django.core.wsgi import get_wsgi_application
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barhop.settings")
#
# # application = get_wsgi_application()
#
#
# from django.conf import settings
# from django.core.wsgi import get_wsgi_application
# from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
#
# _django_app = get_wsgi_application()
# _websocket_app = uWSGIWebsocketServer()
#
#
# def application(environ, start_response):
#     if environ.get('PATH_INFO').startswith(settings.WEBSOCKET_URL):
#         return _websocket_app(environ, start_response)
#     return _django_app(environ, start_response)


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barhop.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
