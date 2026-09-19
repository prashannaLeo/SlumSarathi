"""
WSGI config for slumSarathi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slumSarathi.settings')

application = get_wsgi_application()

try:
    from workers.wsgi import entrypoint
    Default = entrypoint(application)
except Exception:
    try:
        from asgiref.wsgi import WsgiToAsgi
        Default = WsgiToAsgi(application)
    except Exception:
        pass
