"""
WSGI config for slumSarathi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import importlib.util
import os
import sys

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Preload slumSarathi.settings from file so Django can import it
# even if the bundler does not preserve the package directory.
_settings_path = BASE_DIR / 'slumSarathi' / 'settings.py'
if 'slumSarathi.settings' not in sys.modules and _settings_path.exists():
    _spec = importlib.util.spec_from_file_location('slumSarathi.settings', _settings_path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules['slumSarathi.settings'] = _module
    try:
        _spec.loader.exec_module(_module)
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slumSarathi.settings')

from django.core.wsgi import get_wsgi_application

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
