import os
import sys
from workers import WorkerEntrypoint, wsgi
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await wsgi.fetch(application, request, self.env)
