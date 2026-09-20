import os
import sys

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.asgi import get_asgi_application

application = get_asgi_application()

try:
    from workers.asgi import entrypoint
    Default = entrypoint(application)
except Exception:
    Default = application