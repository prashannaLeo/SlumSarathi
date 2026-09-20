import io
import os

from django.conf import settings
from django.contrib import admin
from django.core.management import call_command
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static

try:
    from workers import env as workers_env
except Exception:
    workers_env = None


def run_migrations_view(request):
    token = request.GET.get('token')
    expected = os.environ.get('MIGRATE_TOKEN') or getattr(workers_env, 'MIGRATE_TOKEN', 'change-me-please')
    if token != expected:
        return HttpResponseForbidden("Forbidden")
    out = io.StringIO()
    try:
        call_command('migrate', stdout=out, interactive=False)
        return JsonResponse({'ok': True, 'output': out.getvalue()})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e), 'output': out.getvalue()}, status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="homepage.html"), name='homepage'),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('resources/', include('resources.urls')),
    path('events/', include('events.urls')),
    path('__run_migrations__/', run_migrations_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
