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
