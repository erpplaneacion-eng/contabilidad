from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.files.base import ContentFile
import os
import io
import logging
from .models import ProcesamientoRecibo, ReciboDetectado
from .forms import PDFUploadForm, FiltrosRecibosForm
from .utils.pdf_processor import PDFProcessor
from .utils.image_extractor import ImageExtractor
from .utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


def procesar_recibo_sincrono(procesamiento_id):
    """
    Procesa un PDF de recibos de forma síncrona (sin Celery/Redis).
    Versión simplificada para desarrollo local.

    Args:
        procesamiento_id: ID del procesamiento
    """
    try:
        # Obtener el procesamiento
        procesamiento = ProcesamientoRecibo.objects.get(id=procesamiento_id)

        # Leer configuración del modelo
        calidad_imagen = procesamiento.calidad_imagen
        tamaño_imagen = procesamiento.tamaño_imagen
        formato_salida = procesamiento.formato_salida
        extraer_imagenes = procesamiento.extraer_imagenes
        generar_reporte = procesamiento.generar_reporte

        logger.info(f"Iniciando procesamiento síncrono de PDF: {procesamiento_id}")
        logger.info(f"Configuración - calidad: {calidad_imagen}, tamaño: {tamaño_imagen}, formato: {formato_salida}")

        # Actualizar estado
        procesamiento.estado = 'PROCESANDO'
        procesamiento.save()

        # Verificar que el archivo existe
        if not procesamiento.archivo_original:
            raise FileNotFoundError("Archivo PDF no encontrado")

        pdf_path = procesamiento.archivo_original.path

        # Paso 1: Detectar recibos
        logger.info("Detectando recibos en el PDF...")
        processor = PDFProcessor(pdf_path)
        recibos_detectados = processor.detectar_recibos_coordenadas()

        if not recibos_detectados:
            raise ValueError("No se encontraron recibos en el archivo PDF")

        # Paso 2: Extraer imágenes con la calidad y tamaño especificados (si está habilitado)
        imagenes_data = []
        if extraer_imagenes:
            logger.info(f"Extrayendo imágenes de recibos con calidad: {calidad_imagen}, tamaño: {tamaño_imagen}...")
            extractor = ImageExtractor(pdf_path)
            imagenes_data = extractor.procesar_y_guardar_imagenes(
                recibos_detectados,
                procesamiento_id,
                calidad_imagen=calidad_imagen,
                tamaño_imagen=tamaño_imagen
            )
        else:
            logger.info("Extracción de imágenes deshabilitada")
            # Crear datos vacíos para cada recibo
            imagenes_data = [{'imagen_data': None} for _ in recibos_detectados]

        # Paso 3: Guardar información en base de datos
        logger.info("Guardando información de recibos en base de datos...")
        for i, (recibo_info, imagen_info) in enumerate(zip(recibos_detectados, imagenes_data)):
            try:
                # Crear instancia de ReciboDetectado
                recibo = ReciboDetectado.objects.create(
                    procesamiento=procesamiento,
                    numero_secuencial=i + 1,
                    coordenada_x=recibo_info.get('x', 0),
                    coordenada_y=recibo_info.get('y', 0),
                    ancho=recibo_info.get('width', 0),
                    alto=recibo_info.get('height', 0),
                    nombre_beneficiario=recibo_info.get('beneficiario', ''),
                    valor=recibo_info.get('valor'),
                    entidad_bancaria=recibo_info.get('entidad', ''),
                    numero_cuenta=recibo_info.get('cuenta', ''),
                    referencia=recibo_info.get('referencia', ''),
                    fecha_aplicacion=recibo_info.get('fecha'),
                    concepto=recibo_info.get('concepto', ''),
                    estado_pago=recibo_info.get('estado', ''),
                    texto_extraido=recibo_info.get('texto_completo', '')
                )

                # Guardar imagen si está disponible
                if imagen_info and imagen_info.get('imagen_data'):
                    try:
                        recibo.imagen_recibo.save(
                            imagen_info['filename'],
                            ContentFile(imagen_info['imagen_data']),
                            save=True
                        )
                    except Exception as e:
                        logger.warning(f"Error guardando imagen para recibo {i + 1}: {str(e)}")

            except Exception as e:
                logger.error(f"Error guardando recibo {i + 1}: {str(e)}")

        # Paso 4: Generar PDF separado según formato_salida
        logger.info(f"Generando PDF separado con formato: {formato_salida}...")
        output_path = f"media/pdfs_procesados/recibos_separados_{procesamiento_id}.pdf"

        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Obtener datos de recibos para el generador
        recibos_db = ReciboDetectado.objects.filter(procesamiento=procesamiento)
        recibos_data = []
        imagenes_generadas = []

        for recibo_db in recibos_db:
            recibo_data = {
                'numero_secuencial': recibo_db.numero_secuencial,
                'nombre_beneficiario': recibo_db.nombre_beneficiario,
                'valor': float(recibo_db.valor) if recibo_db.valor else 0,
                'entidad_bancaria': recibo_db.entidad_bancaria,
                'numero_cuenta': recibo_db.numero_cuenta,
                'referencia': recibo_db.referencia,
                'fecha_aplicacion': str(recibo_db.fecha_aplicacion) if recibo_db.fecha_aplicacion else '',
                'concepto': recibo_db.concepto,
                'estado_pago': recibo_db.estado_pago
            }
            recibos_data.append(recibo_data)

            # Crear datos de imagen para el generador
            imagen_data = {}
            if recibo_db.imagen_recibo:
                try:
                    with open(recibo_db.imagen_recibo.path, 'rb') as f:
                        imagen_data['imagen_data'] = f.read()
                except Exception as e:
                    logger.warning(f"Error leyendo imagen para recibo {recibo_db.numero_secuencial}: {str(e)}")
                    imagen_data['imagen_data'] = None
            else:
                imagen_data['imagen_data'] = None

            imagenes_generadas.append(imagen_data)

        # Generar PDF según formato especificado
        generator = PDFGenerator(output_path)
        try:
            if formato_salida == 'pdf_imagenes':
                generator.generar_pdf_con_imagenes(recibos_data, imagenes_generadas)
            elif formato_salida == 'pdf_texto':
                generator.generar_pdf_simple(recibos_data)
            elif formato_salida == 'ambos':
                # Generar ambos formatos
                generator.generar_pdf_con_imagenes(recibos_data, imagenes_generadas)
                # Generar PDF de texto con sufijo
                output_path_texto = f"media/pdfs_procesados/recibos_separados_texto_{procesamiento_id}.pdf"
                generator_texto = PDFGenerator(output_path_texto)
                generator_texto.generar_pdf_simple(recibos_data)
                logger.info(f"PDF de texto generado: {output_path_texto}")
        except Exception as e:
            logger.warning(f"Error generando PDF con formato {formato_salida}: {str(e)}. Intentando PDF simple...")
            generator.generar_pdf_simple(recibos_data)

        # Paso 5: Generar reporte estadístico (si está habilitado)
        if generar_reporte:
            try:
                logger.info("Generando reporte estadístico...")
                reporte_path = generator.generar_reporte_estadisticas(recibos_data)
                procesamiento.archivo_reporte.name = reporte_path.replace("media/", "")
                logger.info(f"Reporte generado: {reporte_path}")
            except Exception as e:
                logger.warning(f"Error generando reporte: {str(e)}")

        # Actualizar procesamiento
        procesamiento.archivo_resultado.name = output_path.replace("media/", "")
        procesamiento.total_recibos = len(recibos_detectados)
        procesamiento.estado = 'COMPLETADO'
        procesamiento.save()

        logger.info(f"Procesamiento completado exitosamente. Encontrados {len(recibos_detectados)} recibos")

        return True

    except Exception as e:
        logger.error(f"Error procesando PDF: {str(e)}")

        # Actualizar estado de error
        try:
            procesamiento = ProcesamientoRecibo.objects.get(id=procesamiento_id)
            procesamiento.estado = 'ERROR'
            procesamiento.mensaje_error = str(e)
            procesamiento.save()
        except:
            pass

        raise


@login_required
def upload_pdf(request):
    """Vista para subir archivo PDF (procesamiento automático con alta calidad)"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                procesamiento = form.save(commit=False)
                procesamiento.usuario = request.user
                # Los valores por defecto del modelo ya están configurados para alta calidad:
                # calidad_imagen='alta', tamaño_imagen='grande', formato_salida='pdf_imagenes'
                # extraer_imagenes=True, generar_reporte=True
                procesamiento.save()

                logger.info(f"Iniciando procesamiento de alta calidad para usuario {request.user.username}")

                # Procesar de forma síncrona (sin Celery/Redis)
                # Para usar procesamiento asíncrono, reemplazar con: procesar_recibo_pdf.delay(procesamiento.id)
                try:
                    procesar_recibo_sincrono(procesamiento.id)
                    logger.info(f"Procesamiento completado exitosamente")
                except Exception as e:
                    logger.error(f"Error en procesamiento: {str(e)}")
                    # El error ya fue guardado en la base de datos por procesar_recibo_sincrono

                return redirect('separador_recibos:process_status', procesamiento_id=procesamiento.id)

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
    
    
    