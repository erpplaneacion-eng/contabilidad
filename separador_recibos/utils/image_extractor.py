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
    
    def extraer_imagen_recibo(self, coordenadas: Dict, tamaño_imagen: str = 'mediana', calidad_imagen: str = 'media') -> Image.Image:
        """
        Extrae el pantallazo visual de cada recibo usando coordenadas

        Args:
            coordenadas: Diccionario con coordenadas del recibo
            tamaño_imagen: Tamaño de salida ('pequeña', 'mediana', 'grande')
            calidad_imagen: Calidad de extracción ('baja', 'media', 'alta')
        """
        try:
            logger.info(f"Extrayendo imagen de recibo - Coordenadas: {coordenadas}, Calidad: {calidad_imagen}, Tamaño: {tamaño_imagen}")

            doc = fitz.open(self.pdf_path)
            pagina_num = coordenadas['pagina'] - 1  # 0-indexed

            if pagina_num >= len(doc):
                raise ValueError(f"Página {pagina_num + 1} no existe en el PDF")

            page = doc[pagina_num]

            # Definir rectángulo basado en coordenadas detectadas
            x = coordenadas.get('x', 0)
            y = coordenadas.get('y', 0)
            width = coordenadas.get('width', 612)  # Letter (Carta) width por defecto (8.5 pulgadas = 612 puntos)
            height = coordenadas.get('height', 800)  # Altura estimada

            # Asegurar que las coordenadas estén dentro de los límites de la página
            page_width = page.rect.width
            page_height = page.rect.height

            x = max(0, min(x, page_width - 10))
            y = max(0, min(y, page_height - 10))
            width = min(width, page_width - x)
            height = min(height, page_height - y)

            rect = fitz.Rect(x, y, x + width, y + height)

            # Determinar factor de escala según calidad
            # Factor de escala afecta la resolución del pixmap
            factores_escala = {
                'baja': 1.0,   # Más rápido, menor resolución
                'media': 2.0,  # Balance velocidad/calidad
                'alta': 3.0    # Más lento, mayor resolución
            }
            escala = factores_escala.get(calidad_imagen.lower(), 2.0)

            logger.info(f"  Factor de escala: {escala}x para calidad {calidad_imagen}")

            # Extraer como imagen con calidad ajustada
            mat = fitz.Matrix(escala, escala)
            pix = page.get_pixmap(matrix=mat, clip=rect)

            # Convertir a PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Determinar tamaño de salida según configuración
            tamaños_salida = {
                'pequeña': (300, 400),
                'mediana': (600, 800),
                'grande': (900, 1200)
            }
            output_size = tamaños_salida.get(tamaño_imagen.lower(), (600, 800))

            # Redimensionar
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
    
    def procesar_y_guardar_imagenes(self, recibos_detectados: list, procesamiento_id: str, calidad_imagen: str = 'media', tamaño_imagen: str = 'mediana') -> list:
        """
        Procesa todos los recibos y guarda sus imágenes

        Args:
            recibos_detectados: Lista de recibos detectados
            procesamiento_id: ID del procesamiento
            calidad_imagen: Calidad de imagen ('baja', 'media', 'alta')
            tamaño_imagen: Tamaño de imagen ('pequeña', 'mediana', 'grande')
        """
        logger.info(f"Procesando {len(recibos_detectados)} imágenes de recibos con calidad: {calidad_imagen}, tamaño: {tamaño_imagen}")
        imagenes_procesadas = []

        # Determinar formato y calidad de guardado según calidad_imagen
        # PNG no tiene parámetro quality, es lossless
        # Para mejor control, usamos JPEG con quality o PNG según calidad
        configuraciones_guardado = {
            'baja': {'format': 'JPEG', 'quality': 75, 'optimize': False},   # JPEG con compresión
            'media': {'format': 'JPEG', 'quality': 85, 'optimize': True},    # JPEG calidad media
            'alta': {'format': 'PNG', 'optimize': True}                      # PNG lossless
        }
        config = configuraciones_guardado.get(calidad_imagen.lower(), configuraciones_guardado['media'])

        for i, recibo in enumerate(recibos_detectados):
            try:
                logger.info(f"Procesando imagen del recibo {i + 1}")

                # Extraer imagen con calidad y tamaño especificados
                img = self.extraer_imagen_recibo(recibo, tamaño_imagen=tamaño_imagen, calidad_imagen=calidad_imagen)
                
                # Preparar para guardar con formato y calidad ajustada
                img_buffer = io.BytesIO()
                
                # Si la imagen tiene transparencia y vamos a usar JPEG, convertir a RGB
                if config['format'] == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    # Crear fondo blanco para transparencias
                    fondo = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    fondo.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = fondo
                
                # Guardar con configuración según calidad
                if config['format'] == 'JPEG':
                    img.save(img_buffer, format='JPEG', quality=config['quality'], optimize=config.get('optimize', False))
                else:  # PNG
                    # PNG usa compress_level (0-9) para controlar compresión, no quality
                    # 0 = sin compresión (rápido), 9 = máxima compresión (lento)
                    compress_level = 3 if calidad_imagen.lower() == 'baja' else 6 if calidad_imagen.lower() == 'media' else 9
                    img.save(img_buffer, format='PNG', optimize=config.get('optimize', True), compress_level=compress_level)
                
                img_buffer.seek(0)
                
                # Determinar extensión según formato usado
                extension = 'jpg' if config['format'] == 'JPEG' else 'png'
                
                # Crear información de la imagen
                img_info = {
                    'numero_recibo': i + 1,
                    'imagen_data': img_buffer.getvalue(),
                    'filename': f'recibo_{i + 1}.{extension}',
                    'coordenadas': recibo,
                    'formato': config['format'],
                    'calidad': calidad_imagen
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