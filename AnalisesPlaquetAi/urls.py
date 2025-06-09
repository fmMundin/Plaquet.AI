from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('accounts:login') if not request.user.is_authenticated else redirect('Analises:index')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('analises/', include('Analises.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)