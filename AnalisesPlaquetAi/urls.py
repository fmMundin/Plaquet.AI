# Version: 1.0
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_analises(request):
    return redirect('Analises/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Analises/', include('Analises.urls')),
    path('', redirect_to_analises, name='root'),  # Nova rota para o caminho raiz
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)