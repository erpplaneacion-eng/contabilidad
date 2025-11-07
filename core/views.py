"""
Vistas de la aplicación core (dashboard principal y funcionalidades compartidas).
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import datetime, timedelta


@login_required
def dashboard_principal(request):
    """
    Dashboard principal que muestra estadísticas unificadas de ambas aplicaciones.

    Muestra:
    - Estadísticas de proveedores
    - Estadísticas de procesamiento de recibos
    - Accesos rápidos según el área del usuario
    """
    # Inicializar contexto
    context = {
        'titulo': 'Dashboard Principal',
        'fecha_actual': datetime.now(),
    }

    # Obtener perfil del usuario
    user_profile = None
    if hasattr(request.user, 'profile'):
        user_profile = request.user.profile
        context['user_profile'] = user_profile

    # --- ESTADÍSTICAS DE PROVEEDORES ---
    try:
        from proveedores.models import Proveedor, Contacto

        # Total de proveedores
        total_proveedores = Proveedor.objects.count()
        context['total_proveedores'] = total_proveedores

        # Proveedores registrados este mes
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        proveedores_mes = Proveedor.objects.filter(fecha_creacion__gte=inicio_mes).count()
        context['proveedores_mes'] = proveedores_mes

        # Proveedores recientes (últimos 5)
        proveedores_recientes = Proveedor.objects.order_by('-fecha_creacion')[:5]
        context['proveedores_recientes'] = proveedores_recientes

        # Distribución por naturaleza jurídica
        distribucion_naturaleza = Proveedor.objects.values('naturaleza_juridica').annotate(
            total=Count('id')
        ).order_by('-total')
        context['distribucion_naturaleza'] = distribucion_naturaleza

    except Exception as e:
        context['error_proveedores'] = f"Error al cargar datos de proveedores: {str(e)}"

    # --- ESTADÍSTICAS DE SEPARADOR DE RECIBOS ---
    try:
        from separador_recibos.models import ProcesamientoRecibo, ReciboDetectado

        # Total de procesamientos
        total_procesamientos = ProcesamientoRecibo.objects.filter(usuario=request.user).count()
        context['total_procesamientos'] = total_procesamientos

        # Total de recibos detectados
        total_recibos = ReciboDetectado.objects.filter(
            procesamiento__usuario=request.user
        ).count()
        context['total_recibos'] = total_recibos

        # Valor total procesado
        valor_total = ReciboDetectado.objects.filter(
            procesamiento__usuario=request.user
        ).aggregate(total=Sum('valor'))['total'] or 0
        context['valor_total_procesado'] = valor_total

        # Procesamientos recientes (últimos 5)
        procesamientos_recientes = ProcesamientoRecibo.objects.filter(
            usuario=request.user
        ).order_by('-fecha_subida')[:5]
        context['procesamientos_recientes'] = procesamientos_recientes

        # Procesamientos este mes
        procesamientos_mes = ProcesamientoRecibo.objects.filter(
            usuario=request.user,
            fecha_subida__gte=inicio_mes
        ).count()
        context['procesamientos_mes'] = procesamientos_mes

        # Top 5 entidades bancarias
        top_entidades = ReciboDetectado.objects.filter(
            procesamiento__usuario=request.user
        ).values('entidad_bancaria').annotate(
            total=Count('id'),
            valor_total=Sum('valor')
        ).order_by('-total')[:5]
        context['top_entidades'] = top_entidades

        # Estado de procesamientos
        estados = ProcesamientoRecibo.objects.filter(
            usuario=request.user
        ).values('estado').annotate(total=Count('id'))
        context['estados_procesamientos'] = estados

    except Exception as e:
        context['error_separador'] = f"Error al cargar datos de recibos: {str(e)}"

    return render(request, 'dashboard/main.html', context)

from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Municipio
import logging

logger = logging.getLogger(__name__)

def get_municipios(request, departamento_id):
    """Devuelve una lista de municipios para un departamento dado en formato JSON."""
    municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre_municipio')
    data = list(municipios.values('id', 'nombre_municipio'))
    return JsonResponse(data, safe=False)


@csrf_exempt
def test_email_production(request):
    """
    Endpoint de diagnóstico para probar configuración de email en producción.
    URL: /test-email/

    Este endpoint muestra:
    1. Si las variables de entorno están configuradas
    2. Intenta enviar un correo de prueba
    3. Muestra errores detallados

    IMPORTANTE: Este endpoint debe ser ELIMINADO en producción final por seguridad.
    """
    from django.core.mail import send_mail

    resultado = {
        'servidor': 'Railway' if not settings.DEBUG else 'Local',
        'debug_mode': settings.DEBUG,
    }

    # 1. Verificar variables de entorno
    resultado['configuracion'] = {
        'EMAIL_BACKEND': settings.EMAIL_BACKEND,
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': settings.EMAIL_PORT,
        'EMAIL_USE_TLS': settings.EMAIL_USE_TLS,
        'EMAIL_HOST_USER_configurado': bool(settings.EMAIL_HOST_USER),
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else '❌ NO CONFIGURADO',
        'EMAIL_HOST_PASSWORD_configurado': bool(settings.EMAIL_HOST_PASSWORD),
        'EMAIL_HOST_PASSWORD': f"***{settings.EMAIL_HOST_PASSWORD[-4:]}" if settings.EMAIL_HOST_PASSWORD else '❌ NO CONFIGURADO',
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
        'NOTIFICATION_EMAIL': settings.NOTIFICATION_EMAIL,
    }

    # 2. Verificar si la configuración es válida
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        resultado['error'] = 'Variables de email NO configuradas en Railway'
        resultado['solucion'] = 'Agrega EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en Railway Variables'
        return JsonResponse(resultado, status=500)

    # 3. Intentar enviar correo de prueba (solo si se envía parámetro send=true)
    if request.GET.get('send') == 'true':
        try:
            resultado['enviando'] = f"Intentando enviar a {settings.NOTIFICATION_EMAIL}..."

            num_enviados = send_mail(
                subject='🧪 Test desde Railway - Sistema Contabilidad',
                message='Este es un correo de prueba desde el servidor de producción.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFICATION_EMAIL],
                fail_silently=False,
            )

            if num_enviados > 0:
                resultado['exito'] = True
                resultado['mensaje'] = '✅ Correo enviado exitosamente desde Railway'
            else:
                resultado['exito'] = False
                resultado['mensaje'] = '❌ send_mail retornó 0'

        except Exception as e:
            resultado['exito'] = False
            resultado['error'] = str(e)
            resultado['tipo_error'] = type(e).__name__
            logger.error(f"Error en test_email_production: {str(e)}")
    else:
        resultado['info'] = 'Para enviar correo de prueba, agrega ?send=true a la URL'

    return JsonResponse(resultado, json_dumps_params={'indent': 2})

