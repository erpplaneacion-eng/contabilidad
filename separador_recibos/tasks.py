from celery import shared_task
from django.contrib.auth.models import User
import logging
import os
from datetime import datetime
from decimal import Decimal

from .models import ProcesamientoRecibo, ReciboDetectado
from .utils.pdf_processor import PDFProcessor
from .utils.image_extractor import ImageExtractor
from .utils.pdf_generator import PDFGenerator
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@shared_task
def procesar_recibo_pdf(procesamiento_id, calidad_imagen='media'):
    """Tarea asíncrona para procesar PDF de recibos
    
    Args:
        procesamiento_id: ID del procesamiento
        calidad_imagen: Calidad de imagen ('baja', 'media', 'alta'). Default: 'media'
    """
    try:
        logger.info(f"Iniciando procesamiento de PDF: {procesamiento_id}, calidad: {calidad_imagen}")
        
        # Obtener el procesamiento
        procesamiento = ProcesamientoRecibo.objects.get(id=procesamiento_id)
        
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
        
        # Paso 2: Extraer imágenes con la calidad especificada
        logger.info(f"Extrayendo imágenes de recibos con calidad: {calidad_imagen}...")
        extractor = ImageExtractor(pdf_path)
        imagenes_data = extractor.procesar_y_guardar_imagenes(recibos_detectados, procesamiento_id, calidad_imagen=calidad_imagen)
        
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
                # Continuar con el siguiente recibo
        
        # Paso 4: Generar PDF separado
        logger.info("Generando PDF separado...")
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
        
        # Generar PDF
        generator = PDFGenerator(output_path)
        try:
            generator.generar_pdf_con_imagenes(recibos_data, imagenes_generadas)
        except Exception as e:
            logger.warning(f"Error generando PDF con imágenes: {str(e)}. Intentando PDF simple...")
            generator.generar_pdf_simple(recibos_data)
        
        # Actualizar procesamiento
        procesamiento.archivo_resultado.name = output_path.replace("media/", "")
        procesamiento.total_recibos = len(recibos_detectados)
        procesamiento.estado = 'COMPLETADO'
        procesamiento.save()
        
        logger.info(f"Procesamiento completado exitosamente. Encontrados {len(recibos_detectados)} recibos")
        
        return {
            'status': 'success',
            'recibos_encontrados': len(recibos_detectados),
            'archivo_resultado': output_path
        }
        
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
        
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def limpiar_archivos_temporales():
    """Tarea para limpiar archivos temporales antiguos"""
    try:
        from django.core.files.storage import default_storage
        import glob
        import time
        
        # Limpiar archivos PDF originales antiguos (más de 30 días)
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 días
        
        pdf_paths = glob.glob('media/pdfs_originales/*.pdf')
        for path in pdf_paths:
            if os.path.getmtime(path) < cutoff_time:
                try:
                    default_storage.delete(path.replace('media/', ''))
                    logger.info(f"Archivo temporal eliminado: {path}")
                except Exception as e:
                    logger.warning(f"Error eliminando archivo {path}: {str(e)}")
        
        # Limpiar imágenes antiguas (más de 7 días)
        cutoff_time_img = time.time() - (7 * 24 * 60 * 60)  # 7 días
        img_paths = glob.glob('media/imagenes_recibos/*.png')
        for path in img_paths:
            if os.path.getmtime(path) < cutoff_time_img:
                try:
                    default_storage.delete(path.replace('media/', ''))
                    logger.info(f"Imagen temporal eliminada: {path}")
                except Exception as e:
                    logger.warning(f"Error eliminando imagen {path}: {str(e)}")
        
        logger.info("Limpieza de archivos temporales completada")
        
    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {str(e)}")


@shared_task
def generar_reporte_estadisticas(recibo_id):
    """Tarea para generar estadísticas de un recibo específico"""
    try:
        from django.db.models import Count, Sum, Avg
        
        recibo = ReciboDetectado.objects.get(id=recibo_id)
        
        # Estadísticas del procesamiento
        stats = ReciboDetectado.objects.filter(
            procesamiento=recibo.procesamiento
        ).aggregate(
            total_recibos=Count('id'),
            valor_total=Sum('valor'),
            valor_promedio=Avg('valor')
        )
        
        logger.info(f"Estadísticas generadas para recibo {recibo_id}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error generando estadísticas: {str(e)}")
        raise


@shared_task
def validar_calidad_extraccion(procesamiento_id):
    """Tarea para validar la calidad de la extracción de datos"""
    try:
        recibos = ReciboDetectado.objects.filter(procesamiento_id=procesamiento_id)
        
        calidad_stats = {
            'total_recibos': recibos.count(),
            'recibos_con_beneficiario': recibos.filter(nombre_beneficiario__isnull=False).exclude(nombre_beneficiario='').count(),
            'recibos_con_valor': recibos.filter(valor__isnull=False).count(),
            'recibos_con_entidad': recibos.filter(entidad_bancaria__isnull=False).exclude(entidad_bancaria='').count(),
            'recibos_validados': recibos.filter(validado=True).count(),
        }
        
        # Calcular porcentajes de calidad
        total = calidad_stats['total_recibos']
        if total > 0:
            calidad_stats['porcentaje_beneficiario'] = (calidad_stats['recibos_con_beneficiario'] / total) * 100
            calidad_stats['porcentaje_valor'] = (calidad_stats['recibos_con_valor'] / total) * 100
            calidad_stats['porcentaje_entidad'] = (calidad_stats['recibos_con_entidad'] / total) * 100
            calidad_stats['porcentaje_validado'] = (calidad_stats['recibos_validados'] / total) * 100
        
        logger.info(f"Validación de calidad completada para procesamiento {procesamiento_id}")
        
        return calidad_stats
        
    except Exception as e:
        logger.error(f"Error validando calidad: {str(e)}")
        raise