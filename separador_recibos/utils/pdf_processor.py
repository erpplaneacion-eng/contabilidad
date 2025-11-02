"""
Módulo para procesamiento y detección de recibos en archivos PDF
"""
import pdfplumber
import re
import logging
from typing import List, Dict, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Clase principal para procesar archivos PDF y detectar recibos"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.recibos_detectados = []
    
    def detectar_recibos_coordenadas(self) -> List[Dict]:
        """
        Detecta recibos en el PDF usando coordenadas y texto
        """
        try:
            logger.info(f"Iniciando detección de recibos en: {self.pdf_path}")

            with pdfplumber.open(self.pdf_path) as pdf:
                for pagina_num, pagina in enumerate(pdf.pages):
                    logger.info(f"Procesando página {pagina_num + 1}")

                    # Extraer palabras con coordenadas (SIN x_tolerance ni y_tolerance)
                    # Esto extrae palabras completas en lugar de letras individuales
                    texto_coordenadas = pagina.extract_words()

                    logger.info(f"  Palabras extraídas: {len(texto_coordenadas)}")

                    # Buscar patrones de recibos
                    recibos_pagina = self._buscar_patrones_recibo(texto_coordenadas, pagina_num)

                    for recibo in recibos_pagina:
                        # Extraer información específica del recibo
                        recibo_info = self._extraer_info_recibo(texto_coordenadas, recibo, pagina)
                        self.recibos_detectados.append(recibo_info)

            logger.info(f"Detección completada. Encontrados {len(self.recibos_detectados)} recibos")
            return self.recibos_detectados

        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}")
            raise
    
    def _buscar_patrones_recibo(self, texto_coordenadas: List[Dict], pagina_num: int) -> List[Dict]:
        """Busca patrones específicos de recibos en el texto"""
        recibos = []

        logger.info(f"Buscando recibos en página {pagina_num + 1}, total palabras: {len(texto_coordenadas)}")

        # Buscar el patrón "Recibo individual de pagos" juntando palabras consecutivas
        for i, word in enumerate(texto_coordenadas):
            texto_palabra = word.get('text', '').strip()

            # Verificar si encontramos la palabra "Recibo"
            if texto_palabra.lower() == 'recibo':
                # Obtener coordenadas Y de forma más robusta
                y_coord = word.get('y0') or word.get('top') or word.get('y') or 0
                x_coord = word.get('x0') or word.get('x') or 0

                logger.info(f"[DEBUG] Encontrada 'Recibo' en índice {i}, Y={y_coord}, palabra completa: {word}")

                # Juntar las siguientes 10 palabras para formar la frase
                frase_completa = []
                coordenadas_inicio = {'x0': x_coord, 'y0': y_coord}

                # Tomar hasta 10 palabras siguientes en la misma línea
                for j in range(i, min(i + 10, len(texto_coordenadas))):
                    palabra_actual = texto_coordenadas[j]
                    y_actual = palabra_actual.get('y0') or palabra_actual.get('top') or palabra_actual.get('y') or 0

                    # Verificar que estén en la misma línea (misma coordenada Y aproximada)
                    if abs(y_actual - y_coord) < 5:
                        frase_completa.append(palabra_actual.get('text', ''))
                    else:
                        break

                # Unir las palabras y verificar si contiene el patrón
                texto_junto = ' '.join(frase_completa)
                logger.info(f"   Frase formada ({len(frase_completa)} palabras): '{texto_junto}'")

                # Buscar "recibo individual de pagos" con o sin "sucursal virtual"
                texto_junto_lower = texto_junto.lower()
                if 'individual' in texto_junto_lower and 'pagos' in texto_junto_lower:
                    # AJUSTE: La palabra "Recibo" está centrada en el encabezado del recibo
                    # Necesitamos restar un offset para capturar la parte izquierda del recibo
                    # Offset típico: 155-30 puntos para capturar el margen izquierdo completo
                    OFFSET_X_RECIBO = 155
                    x_coord_ajustado = max(0, x_coord - OFFSET_X_RECIBO)
                    
                    recibo_info = {
                        'pagina': pagina_num + 1,
                        'coordenada_x': x_coord_ajustado,
                        'coordenada_y': coordenadas_inicio['y0'],
                        'word_index': i
                    }
                    recibos.append(recibo_info)
                    logger.info(f"✅ Recibo DETECTADO en página {pagina_num + 1}: '{texto_junto}'")
                    logger.info(f"   Coordenada X original: {x_coord:.1f}, ajustada: {x_coord_ajustado:.1f} (offset: -{OFFSET_X_RECIBO})")
                else:
                    logger.warning(f"   ❌ No coincide con patrón esperado")

        logger.info(f"Total recibos encontrados en página {pagina_num + 1}: {len(recibos)}")
        return recibos
    
    def _extraer_info_recibo(self, texto_coordenadas: List[Dict], recibo_base: Dict, pagina=None) -> Dict:
        """Extrae información específica del recibo"""

        # Calcular altura del recibo de forma más precisa
        # Buscar todos los "Recibo" en la misma página para calcular la distancia
        y_inicio = recibo_base['coordenada_y']
        y_recibos = []

        for word in texto_coordenadas:
            if word.get('text', '').strip().lower() == 'recibo':
                # Intentar obtener la coordenada Y de diferentes formas
                y_coord = word.get('y0') or word.get('top') or word.get('y') or 0
                y_recibos.append(y_coord)

        # Ordenar las coordenadas Y
        y_recibos_ordenados = sorted(y_recibos)

        # Encontrar el índice del recibo actual
        try:
            idx_actual = y_recibos_ordenados.index(y_inicio)
            # Si hay un siguiente recibo, usar esa distancia; si no, usar 228 puntos (altura típica)
            if idx_actual + 1 < len(y_recibos_ordenados):
                altura_recibo = y_recibos_ordenados[idx_actual + 1] - y_inicio
            else:
                altura_recibo = 225  # Altura estimada basada en los datos
        except ValueError:
            altura_recibo = 225

        logger.info(f"  Recibo en Y={y_inicio:.1f}, altura calculada={altura_recibo:.1f}")

        recibo_info = {
            'pagina': recibo_base['pagina'],
            'x': recibo_base['coordenada_x'],
            'y': y_inicio,
            'width': 612,  # Letter (Carta) width en puntos (8.5 pulgadas = 612 puntos)
            'height': altura_recibo,
            'texto_completo': '',
            'beneficiario': '',
            'valor': None,
            'entidad': '',
            'cuenta': '',
            'referencia': '',
            'fecha': None,
            'concepto': '',
            'estado': ''
        }

        # Recopilar texto del recibo (desde Y hasta Y + altura)
        texto_recibo = []
        for word in texto_coordenadas:
            word_y = word.get('y0') or word.get('top') or word.get('y') or 0
            # Solo incluir palabras dentro del área del recibo
            if y_inicio <= word_y < (y_inicio + altura_recibo):
                texto_word = word.get('text', '')
                texto_recibo.append(texto_word)
                recibo_info['texto_completo'] += f"{texto_word} "

        logger.info(f"  Texto extraído: {len(texto_recibo)} palabras")

        # Extraer información específica
        recibo_info.update(self._parsear_texto_recibo(' '.join(texto_recibo)))

        return recibo_info
    
    def _esta_en_area_recibo(self, word: Dict, recibo_base: Dict, altura: float = 228) -> bool:
        """Determina si una palabra está en el área del recibo"""
        word_y = word.get('y0', word.get('top', 0))
        y_inicio = recibo_base['coordenada_y']
        return (word_y >= y_inicio and word_y < (y_inicio + altura))
    
    def _parsear_texto_recibo(self, texto: str) -> Dict:
        """Parsea el texto del recibo para extraer información específica"""
        info = {}
        
        # Patrones para extraer información
        patrones = {
            'valor': r'Valor:\s*([\d.,]+)',
            'referencia': r'Referencia:\s*(\w+)',
            'documento': r'Documento:\s*(\d+)',
            'beneficiario': r'Nombre de beneficiario:\s*([A-ZÁÉÍÓÚÑÜ\s]+,)',
            'numero_cuenta': r'Número de cuenta:\s*([\d-]+)',
            'tipo_cuenta': r'Tipo de cuenta:\s*(\w+)',
            'fecha_aplicacion': r'Fecha de aplicación:\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            'concepto': r'Concepto:\s*(\w+)',
            'estado': r'Estado:\s*(PAGO EXITOSO Y ABONADO[\w\s]+)'
        }
        
        for campo, patron in patrones.items():
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                valor_extraido = match.group(1).strip()
                if campo == 'valor':
                    info[campo] = self._limpiar_valor(valor_extraido)
                elif campo == 'beneficiario':
                    info[campo] = valor_extraido.rstrip(',')
                elif campo == 'fecha_aplicacion':
                    info['fecha'] = self._limpiar_fecha(valor_extraido)
                else:
                    info[campo] = valor_extraido

        # Extracción de la entidad bancaria (lógica especial)
        entidades = [
            'BANCO CAJA SOCIAL',
            'BANCO DE BOGOTA',
            'BANCO FALABELLA',
            'BANCO BBVA',
            'BANCOLOMBIA',
            'DAVIPLATA',
            'NEQUI',
        ]
        texto_upper = texto.upper()
        for entidad in entidades:
            if entidad in texto_upper:
                info['entidad'] = entidad
                break

        return info
    
    def _limpiar_valor(self, valor_str: str) -> Decimal:
        """Convierte string de valor a Decimal"""
        try:
            # Remover puntos de miles y cambiar coma por punto decimal
            valor_limpio = valor_str.replace('.', '').replace(',', '.')
            return Decimal(valor_limpio)
        except (InvalidOperation, ValueError):
            return Decimal('0')

    def _limpiar_fecha(self, fecha_str: str):
        """Convierte string de fecha a objeto date"""
        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        try:
            partes = fecha_str.lower().split(' de ')
            dia = int(partes[0])
            mes = meses[partes[1]]
            año = int(partes[2])
            return datetime(año, mes, dia).date()
        except (ValueError, KeyError, IndexError):
            return None
    
    def _es_entidad_bancaria(self, texto: str) -> bool:
        """Verifica si el texto es el nombre de una entidad bancaria"""
        entidades = [
            'BANCO CAJA SOCIAL',
            'BANCO DE BOGOTA',
            'BANCO FALABELLA',
            'BANCO BBVA',
            'BANCOLOMBIA',
            'DAVIPLATA',
            'NEQUI',
            'BANCO',  # Genérico al final para no causar falsos positivos
        ]
        texto_upper = texto.upper()
        return any(entidad in texto_upper for entidad in entidades)
    
    def get_resumen_procesamiento(self) -> Dict:
        """Retorna resumen del procesamiento"""
        if not self.recibos_detectados:
            return {'total': 0, 'con_valor': 0, 'entidades': []}
        
        entidades = set()
        con_valor = 0
        
        for recibo in self.recibos_detectados:
            if recibo.get('entidad'):
                entidades.add(recibo['entidad'])
            if recibo.get('valor'):
                con_valor += 1
        
        return {
            'total': len(self.recibos_detectados),
            'con_valor': con_valor,
            'entidades': list(entidades)
        }