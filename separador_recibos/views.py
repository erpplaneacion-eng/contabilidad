from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
import os
import io
import logging
from .models import ProcesamientoRecibo, ReciboDetectado
from .forms import PDFUploadForm, FiltrosRecibosForm, EditarReciboForm, ConfiguracionProcesamientoForm
from .tasks import procesar_recibo_pdf
from .utils.pdf_processor import PDFProcessor
from .utils.image_extractor import ImageExtractor
from .utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


@login_required
def upload_pdf(request):
    """Vista para subir archivo PDF"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                procesamiento = form.save(commit=False)
                procesamiento.usuario = request.user
                procesamiento.save()
                
                # Iniciar procesamiento asíncrono
                procesar_recibo_pdf.delay(procesamiento.id)
                
                logger.info(f"Procesamiento iniciado para usuario {request.user.username}")
                return redirect('process_status', procesamiento_id=procesamiento.id)
                
            except Exception as e:
                logger.error(f"Error guardando procesamiento: {str(e)}")
                form.add_error(None, f"Error procesando archivo: {str(e)}")
    else:
        form = PDFUploadForm()
    
    context = {
        'form': form,
        'titulo': 'Subir PDF de Recibos'
    }
    return render(request, 'separador_recibos/upload.html', context)


@login_required
def process_status(request, procesamiento_id):
    """Vista para mostrar estado del procesamiento"""
    procesamiento = get_object_or_404(
        ProcesamientoRecibo, 
        id=procesamiento_id, 
        usuario=request.user
    )
    
    # Obtener datos de recibos si están disponibles
    recibos = ReciboDetectado.objects.filter(procesamiento=procesamiento)
    
    context = {
        'procesamiento': procesamiento,
        'recibos': recibos,
        'titulo': 'Estado del Procesamiento'
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Respuesta AJAX para actualizar estado
        return JsonResponse({
            'estado': procesamiento.estado,
            'total_recibos': procesamiento.total_recibos,
            'mensaje_error': procesamiento.mensaje_error,
            'porcentaje': calcular_porcentaje_progreso(procesamiento),
        })
    
    return render(request, 'separador_recibos/process_status.html', context)


@login_required
def results(request, procesamiento_id):
    """Vista para mostrar resultados del procesamiento"""
    procesamiento = get_object_or_404(
        ProcesamientoRecibo, 
        id=procesamiento_id, 
        usuario=request.user
    )
    
    recibos = ReciboDetectado.objects.filter(procesamiento=procesamiento)
    
    context = {
        'procesamiento': procesamiento,
        'recibos': recibos,
        'total_valor': sum([r.valor or 0 for r in recibos]),
        'titulo': 'Resultados del Procesamiento'
    }
    
    return render(request, 'separador_recibos/results.html', context)


@login_required
def download_result(request, procesamiento_id):
    """Vista para descargar PDF resultado"""
    procesamiento = get_object_or_404(
        ProcesamientoRecibo, 
        id=procesamiento_id, 
        usuario=request.user
    )
    
    if not procesamiento.archivo_resultado:
        return HttpResponse("Archivo no disponible", status=404)
    
    try:
        response = FileResponse(
            procesamiento.archivo_resultado.open('rb'),
            as_attachment=True,
            filename=f'recibos_separados_{procesamiento.id}.pdf'
        )
        return response
    except Exception as e:
        logger.error(f"Error descargando archivo: {str(e)}")
        return HttpResponse("Error descargando archivo", status=500)


class TablaRecibosView(LoginRequiredMixin, ListView):
    """Vista para mostrar tabla completa de todos los recibos"""
    model = ReciboDetectado
    template_name = 'separador_recibos/tabla_recibos.html'
    context_object_name = 'recibos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = ReciboDetectado.objects.filter(
            procesamiento__usuario=self.request.user
        ).select_related('procesamiento')
        
        # Aplicar filtros
        form = FiltrosRecibosForm(self.request.GET)
        if form.is_valid():
            queryset = self._aplicar_filtros(queryset, form)
        
        return queryset.order_by('numero_secuencial')
    
    def _aplicar_filtros(self, queryset, form):
        """Aplica filtros a la consulta"""
        beneficiario = form.cleaned_data.get('beneficiario')
        entidad = form.cleaned_data.get('entidad')
        valor_minimo = form.cleaned_data.get('valor_minimo')
        valor_maximo = form.cleaned_data.get('valor_maximo')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        estado = form.cleaned_data.get('estado')
        orden_por = form.cleaned_data.get('orden_por', 'numero_secuencial')
        direccion = form.cleaned_data.get('direccion', 'asc')
        
        if beneficiario:
            queryset = queryset.filter(nombre_beneficiario__icontains=beneficiario)
        
        if entidad:
            queryset = queryset.filter(entidad_bancaria=entidad)
        
        if valor_minimo:
            queryset = queryset.filter(valor__gte=valor_minimo)
        
        if valor_maximo:
            queryset = queryset.filter(valor__lte=valor_maximo)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_aplicacion__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_aplicacion__lte=fecha_hasta)
        
        if estado == 'validado':
            queryset = queryset.filter(validado=True)
        elif estado == 'no_validado':
            queryset = queryset.filter(validado=False)
        
        # Aplicar ordenamiento
        if direccion == 'desc':
            orden_por = f'-{orden_por}'
        
        queryset = queryset.order_by(orden_por)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        recibos = self.get_queryset()
        context['total_recibos'] = recibos.count()
        context['valor_total'] = recibos.aggregate(total=Sum('valor'))['total'] or 0
        context['recibos_validados'] = recibos.filter(validado=True).count()
        
        # Formulario de filtros
        context['form_filtros'] = FiltrosRecibosForm(self.request.GET)
        context['titulo'] = 'Tabla de Seguimiento de Recibos'
        
        return context


@login_required
def ver_recibo(request, recibo_id):
    """Vista para ver detalles de un recibo específico"""
    recibo = get_object_or_404(
        ReciboDetectado, 
        id=recibo_id,
        procesamiento__usuario=request.user
    )
    
    context = {
        'recibo': recibo,
        'titulo': f'Recibo #{recibo.numero_secuencial}'
    }
    
    return render(request, 'separador_recibos/recibo_detail.html', context)


@login_required
def editar_recibo(request, recibo_id):
    """Vista para editar información de un recibo"""
    recibo = get_object_or_404(
        ReciboDetectado, 
        id=recibo_id,
        procesamiento__usuario=request.user
    )
    
    if request.method == 'POST':
        form = EditarReciboForm(request.POST, instance=recibo)
        if form.is_valid():
            form.save()
            return redirect('ver_recibo', recibo_id=recibo.id)
    else:
        form = EditarReciboForm(instance=recibo)
    
    context = {
        'form': form,
        'recibo': recibo,
        'titulo': f'Editar Recibo #{recibo.numero_secuencial}'
    }
    
    return render(request, 'separador_recibos/editar_recibo.html', context)


@login_required
def descargar_imagen(request, recibo_id):
    """Vista para descargar imagen de un recibo"""
    recibo = get_object_or_404(
        ReciboDetectado, 
        id=recibo_id,
        procesamiento__usuario=request.user
    )
    
    if not recibo.imagen_recibo:
        return HttpResponse("Imagen no disponible", status=404)
    
    try:
        response = FileResponse(
            recibo.imagen_recibo.open('rb'),
            as_attachment=True,
            filename=f'recibo_{recibo.numero_secuencial}.png'
        )
        return response
    except Exception as e:
        logger.error(f"Error descargando imagen: {str(e)}")
        return HttpResponse("Error descargando imagen", status=500)


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas"""
    # Obtener estadísticas generales
    total_procesamientos = ProcesamientoRecibo.objects.filter(usuario=request.user).count()
    total_recibos = ReciboDetectado.objects.filter(procesamiento__usuario=request.user).count()
    valor_total = ReciboDetectado.objects.filter(
        procesamiento__usuario=request.user
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Procesamientos recientes
    procesamientos_recientes = ProcesamientoRecibo.objects.filter(
        usuario=request.user
    ).order_by('-fecha_subida')[:5]
    
    # Top entidades bancarias
    entidades_stats = ReciboDetectado.objects.filter(
        procesamiento__usuario=request.user
    ).values('entidad_bancaria').annotate(
        total_recibos=Count('id'),
        valor_total=Sum('valor')
    ).order_by('-valor_total')[:10]
    
    context = {
        'total_procesamientos': total_procesamientos,
        'total_recibos': total_recibos,
        'valor_total': valor_total,
        'procesamientos_recientes': procesamientos_recientes,
        'entidades_stats': entidades_stats,
        'titulo': 'Dashboard'
    }
    
    return render(request, 'separador_recibos/dashboard.html', context)


def calcular_porcentaje_progreso(procesamiento):
    """Calcula porcentaje de progreso basado en el estado"""
    estados_orden = {
        'PENDIENTE': 10,
        'PROCESANDO': 50,
        'COMPLETADO': 100,
        'ERROR': 0
    }
    return estados_orden.get(procesamiento.estado, 0)


@login_required
def validar_recibo(request, recibo_id):
    """Vista AJAX para validar/invalidar un recibo"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        recibo = get_object_or_404(
            ReciboDetectado, 
            id=recibo_id,
            procesamiento__usuario=request.user
        )
        
        action = request.POST.get('action')
        if action == 'validate':
            recibo.validado = True
        elif action == 'invalidate':
            recibo.validado = False
        else:
            return JsonResponse({'error': 'Acción inválida'}, status=400)
        
        recibo.save()
        
        return JsonResponse({
            'success': True,
            'validado': recibo.validado,
            'message': 'Recibo validado exitosamente' if recibo.validado else 'Recibo invalidado'
        })
        
    except Exception as e:
        logger.error(f"Error validando recibo: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def exportar_recibos(request):
    """Vista para exportar recibos a CSV"""
    try:
        import csv
        from django.http import HttpResponse
        
        # Obtener datos filtrados
        queryset = ReciboDetectado.objects.filter(
            procesamiento__usuario=request.user
        )
        
        # Crear respuesta HTTP
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="recibos_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Número', 'Beneficiario', 'Valor', 'Entidad', 'Cuenta', 
            'Referencia', 'Fecha', 'Concepto', 'Estado', 'Validado'
        ])
        
        for recibo in queryset:
            writer.writerow([
                recibo.numero_secuencial,
                recibo.nombre_beneficiario or '',
                recibo.valor or '',
                recibo.entidad_bancaria or '',
                recibo.numero_cuenta or '',
                recibo.referencia or '',
                recibo.fecha_aplicacion or '',
                recibo.concepto or '',
                recibo.estado_pago or '',
                'Sí' if recibo.validado else 'No'
            ])
        
        return response
        
    except Exception as e:
        logger.error(f"Error exportando recibos: {str(e)}")
        return HttpResponse(f"Error exportando: {str(e)}", status=500)