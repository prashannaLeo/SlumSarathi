from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="homepage.html"), name='homepage'),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('resources/', include('resources.urls')),
    path('events/', include('events.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
