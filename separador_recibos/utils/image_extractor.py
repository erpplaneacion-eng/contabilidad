"""
Módulo para extracción de imágenes de recibos usando coordenadas
"""
import fitz  # PyMuPDF
from PIL import Image
import io
import logging
from typing import Dict, Tuple
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Clase para extraer imágenes de recibos usando coordenadas"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def extraer_imagen_recibo(self, coordenadas: Dict, output_size: Tuple[int, int] = (600, 800)) -> Image.Image:
        """
        Extrae el pantallazo visual de cada recibo usando coordenadas
        """
        try:
            logger.info(f"Extrayendo imagen de recibo - Coordenadas: {coordenadas}")
            
            doc = fitz.open(self.pdf_path)
            pagina_num = coordenadas['pagina'] - 1  # 0-indexed
            
            if pagina_num >= len(doc):
                raise ValueError(f"Página {pagina_num + 1} no existe en el PDF")
            
            page = doc[pagina_num]
            
            # Definir rectángulo basado en coordenadas detectadas
            x = coordenadas.get('x', 0)
            y = coordenadas.get('y', 0)
            width = coordenadas.get('width', 595)  # A4 width por defecto
            height = coordenadas.get('height', 800)  # Altura estimada
            
            # Asegurar que las coordenadas estén dentro de los límites de la página
            page_width = page.rect.width
            page_height = page.rect.height
            
            x = max(0, min(x, page_width - 10))
            y = max(0, min(y, page_height - 10))
            width = min(width, page_width - x)
            height = min(height, page_height - y)
            
            rect = fitz.Rect(x, y, x + width, y + height)
            
            # Extraer como imagen con alta calidad
            mat = fitz.Matrix(2, 2)  # Factor de escala para mejor calidad
            pix = page.get_pixmap(matrix=mat, clip=rect)
            
            # Convertir a PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Redimensionar si es necesario
            if output_size:
                img = self._redimensionar_imagen(img, output_size)
            
            doc.close()
            return img
            
        except Exception as e:
            logger.error(f"Error extrayendo imagen de recibo: {str(e)}")
            raise
    
    def _redimensionar_imagen(self, img: Image.Image, output_size: Tuple[int, int]) -> Image.Image:
        """Redimensiona imagen manteniendo proporción"""
        target_width, target_height = output_size
        
        # Calcular factor de escala para mantener proporción
        img_width, img_height = img.size
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        scale = min(scale_w, scale_h)
        
        # Calcular nuevas dimensiones
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Redimensionar con alta calidad
        resized_img = img.resize(
            (new_width, new_height), 
            Image.Resampling.LANCZOS
        )
        
        return resized_img
    
    def procesar_y_guardar_imagenes(self, recibos_detectados: list, procesamiento_id: str) -> list:
        """
        Procesa todos los recibos y guarda sus imágenes
        """
        logger.info(f"Procesando {len(recibos_detectados)} imágenes de recibos")
        imagenes_procesadas = []
        
        for i, recibo in enumerate(recibos_detectados):
            try:
                logger.info(f"Procesando imagen del recibo {i + 1}")
                
                # Extraer imagen
                img = self.extraer_imagen_recibo(recibo)
                
                # Preparar para guardar
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG', quality=95)
                img_buffer.seek(0)
                
                # Crear información de la imagen
                img_info = {
                    'numero_recibo': i + 1,
                    'imagen_data': img_buffer.getvalue(),
                    'filename': f'recibo_{i + 1}.png',
                    'coordenadas': recibo
                }
                
                imagenes_procesadas.append(img_info)
                
            except Exception as e:
                logger.error(f"Error procesando imagen del recibo {i + 1}: {str(e)}")
                # Crear imagen placeholder en caso de error
                img_info = self._crear_imagen_placeholder(i + 1, str(e))
                imagenes_procesadas.append(img_info)
        
        return imagenes_procesadas
    
    def _crear_imagen_placeholder(self, numero_recibo: int, mensaje_error: str) -> Dict:
        """Crea una imagen placeholder en caso de error"""
        try:
            from PIL import ImageDraw, ImageFont
            
            # Crear imagen placeholder
            img = Image.new('RGB', (600, 800), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Intentar cargar fuente por defecto
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Agregar texto
            texto = f"Error al cargar recibo #{numero_recibo}"
            draw.text((50, 100), texto, fill='red', font=font)
            draw.text((50, 150), mensaje_error[:50], fill='black', font=font)
            
            # Guardar en buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return {
                'numero_recibo': numero_recibo,
                'imagen_data': img_buffer.getvalue(),
                'filename': f'recibo_error_{numero_recibo}.png',
                'coordenadas': {},
                'error': mensaje_error
            }
            
        except Exception as e:
            logger.error(f"Error creando imagen placeholder: {str(e)}")
            # Fallback simple
            return {
                'numero_recibo': numero_recibo,
                'imagen_data': b'',
                'filename': f'recibo_error_{numero_recibo}.png',
                'coordenadas': {},
                'error': f"Error creando placeholder: {str(e)}"
            }
    
    def generar_vista_previa(self, recibo_info: Dict, max_size: Tuple[int, int] = (300, 400)) -> Image.Image:
        """Genera una vista previa pequeña de la imagen del recibo"""
        try:
            img_completa = self.extraer_imagen_recibo(recibo_info)
            
            # Crear vista previa
            preview = img_completa.copy()
            preview.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generando vista previa: {str(e)}")
            # Retornar imagen placeholder
            return self._crear_vista_previa_placeholder()
    
    def _crear_vista_previa_placeholder(self) -> Image.Image:
        """Crea una vista previa placeholder"""
        try:
            from PIL import ImageDraw, ImageFont
            
            img = Image.new('RGB', (300, 400), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 200), "Vista previa no disponible", fill='black', font=font)
            return img
            
        except Exception as e:
            logger.error(f"Error creando vista previa placeholder: {str(e)}")
            return Image.new('RGB', (300, 400), color='lightgray')