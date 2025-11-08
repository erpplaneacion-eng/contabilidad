"""
URL configuration for contabiliadad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.views import test_email_production, test_gmail_api

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # URLs de core (dashboard principal)
    path('dashboard/', include('core.urls')),

    # URLs de proveedores
    path('proveedores/', include('proveedores.urls')),

    # URLs del Separador de Recibos PDF
    path('separador/', include('separador_recibos.urls')),

    # Endpoints de diagnóstico de email (TEMPORAL - Eliminar después de verificar)
    path('test-email/', test_email_production, name='test_email_production'),
    path('test-gmail-api/', test_gmail_api, name='test_gmail_api'),

    # Redirigir la raíz al login
    path('', RedirectView.as_view(url='/login/', permanent=False)),
]

# Servir archivos media en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
