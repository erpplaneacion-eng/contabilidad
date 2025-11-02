"""
Módulo para procesamiento y detección de recibos en archivos PDF
"""
import pdfplumber
import re
import logging
from typing import List, Dict, Tuple
from decimal import Decimal, InvalidOperation

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
                    
                    # Extraer palabras con coordenadas
                    texto_coordenadas = pagina.extract_words(
                        x_tolerance=3, 
                        y_tolerance=3,
                        extra_attrs=["text", "x0", "y0", "x1", "y1"]
                    )
                    
                    # Buscar patrones de recibos
                    recibos_pagina = self._buscar_patrones_recibo(texto_coordenadas, pagina_num)
                    
                    for recibo in recibos_pagina:
                        # Extraer información específica del recibo
                        recibo_info = self._extraer_info_recibo(texto_coordenadas, recibo)
                        self.recibos_detectados.append(recibo_info)
            
            logger.info(f"Detección completada. Encontrados {len(self.recibos_detectados)} recibos")
            return self.recibos_detectados
            
        except Exception as e:
            logger.error(f"Error procesando PDF: {str(e)}")
            raise
    
    def _buscar_patrones_recibo(self, texto_coordenadas: List[Dict], pagina_num: int) -> List[Dict]:
        """Busca patrones específicos de recibos en el texto"""
        recibos = []
        
        for i, word in enumerate(texto_coordenadas):
            if "Recibo individual de pagos" in word.get('text', ''):
                recibo_info = {
                    'pagina': pagina_num + 1,
                    'coordenada_x': word['x0'],
                    'coordenada_y': word['y0'],
                    'word_index': i
                }
                recibos.append(recibo_info)
        
        return recibos
    
    def _extraer_info_recibo(self, texto_coordenadas: List[Dict], recibo_base: Dict) -> Dict:
        """Extrae información específica del recibo"""
        recibo_info = {
            'pagina': recibo_base['pagina'],
            'x': recibo_base['coordenada_x'],
            'y': recibo_base['coordenada_y'],
            'width': 0,
            'height': 0,
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
        
        # Extraer área del recibo (desde el título hasta el final del recibo)
        recibo_info['width'] = 595  # A4 width en puntos
        recibo_info['height'] = 800  # Altura estimada del recibo
        
        # Recopilar texto del recibo
        texto_recibo = []
        for word in texto_coordenadas:
            if self._esta_en_area_recibo(word, recibo_base):
                texto_recibo.append(word['text'])
                recibo_info['texto_completo'] += f"{word['text']} "
        
        # Extraer información específica
        recibo_info.update(self._parsear_texto_recibo(' '.join(texto_recibo)))
        
        return recibo_info
    
    def _esta_en_area_recibo(self, word: Dict, recibo_base: Dict) -> bool:
        """Determina si una palabra está en el área del recibo"""
        # Buscar palabras desde el título hasta aproximadamente 800 puntos hacia abajo
        return (word['y0'] >= recibo_base['coordenada_y'] and 
                word['y0'] <= recibo_base['coordenada_y'] + 800)
    
    def _parsear_texto_recibo(self, texto: str) -> Dict:
        """Parsea el texto del recibo para extraer información específica"""
        info = {}
        
        # Patrones para extraer información
        patrones = {
            'valor': r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            'referencia': r'([A-Z]{2,}\d{10,})',
            'documento': r'DA\d+',
            'beneficiario': r'([A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+)*)'
        }
        
        # Extraer valor (buscar el más grande que parezca una cantidad)
        valores = re.findall(patrones['valor'], texto)
        if valores:
            try:
                # Tomar el valor más alto que parezca razonable
                valor_max = max([self._limpiar_valor(v) for v in valores if self._limpiar_valor(v) > 1000])
                info['valor'] = valor_max
            except:
                pass
        
        # Extraer referencia
        referencias = re.findall(patrones['referencia'], texto)
        if referencias:
            info['referencia'] = referencias[0]
        
        # Extraer documento
        documentos = re.findall(patrones['documento'], texto)
        if documentos:
            info['documento'] = documentos[0]
        
        # Extraer beneficiario (buscar nombres después de patrones conocidos)
        beneficiarios = re.findall(patrones['beneficiario'], texto)
        if beneficiarios:
            # Filtrar nombres que no parezcan ser entidades bancarias
            nombres_validos = [b for b in beneficiarios if not self._es_entidad_bancaria(b)]
            if nombres_validos:
                info['beneficiario'] = nombres_validos[0]
        
        # Extraer entidad bancaria
        entidades = ['BANCOLOMBIA', 'BANCO CAJA SOCIAL', 'NEQUI', 'DAVIPLATA', 
                    'BANCO DE BOGOTA', 'BANCO FALABELLA', 'BANCO BBVA']
        for entidad in entidades:
            if entidad in texto.upper():
                info['entidad'] = entidad
                break
        
        # Extraer concepto
        if 'PAGO' in texto.upper():
            info['concepto'] = 'PAGO'
        elif 'PAGOS' in texto.upper():
            info['concepto'] = 'PAGOS'
        
        # Extraer estado
        if 'PAGO EXITOSO' in texto.upper():
            info['estado'] = 'PAGO EXITOSO Y ABONADO'
        
        # Extraer fecha (27 de Octubre de 2025)
        fechas = re.findall(r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})', texto, re.IGNORECASE)
        if fechas:
            info['fecha_str'] = fechas[0]
        
        return info
    
    def _limpiar_valor(self, valor_str: str) -> Decimal:
        """Convierte string de valor a Decimal"""
        try:
            # Remover puntos de miles y cambiar coma por punto decimal
            valor_limpio = valor_str.replace('.', '').replace(',', '.')
            return Decimal(valor_limpio)
        except (InvalidOperation, ValueError):
            return Decimal('0')
    
    def _es_entidad_bancaria(self, texto: str) -> bool:
        """Verifica si el texto es el nombre de una entidad bancaria"""
        entidades = ['BANCOLOMBIA', 'BANCO', 'CAJA SOCIAL', 'NEQUI', 'DAVIPLATA', 
                    'FALABELLA', 'BBVA']
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