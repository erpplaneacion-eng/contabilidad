"""
Módulo para generación de PDF separado con cada recibo en página individual
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import black, green
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.enums import TA_CENTER
import io
import logging
from typing import List, Dict
from PIL import Image

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Clase para generar PDF separado con cada recibo individual"""
    
    def __init__(self, output_path: str | None = None):
        self.output_path = output_path
        self.width, self.height = LETTER  # Letter (Carta) tamaño: 612 x 792 puntos
        self.margin = 1 * inch
    
    def generar_pdf_con_imagenes(self, recibos_data: List[Dict], imagenes_data: List[Dict]) -> bytes:
        """
        Genera PDF con cada recibo en su propia página individual usando las imágenes extraídas
        Cada página contiene: Título del recibo + Información + Imagen
        """
        try:
            logger.info(f"Generando PDF con {len(recibos_data)} recibos (1 recibo por página)")

            buffer = io.BytesIO()

            # Crear documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=LETTER,  # Letter (Carta) tamaño: 612 x 792 puntos
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )

            # Lista para almacenar elementos del PDF
            story = []
            styles = getSampleStyleSheet()

            # Procesar cada recibo
            for i, (recibo_data, imagen_data) in enumerate(zip(recibos_data, imagenes_data)):
                # Título del recibo
                recibo_title_style = styles['Heading1']
                recibo_title_style.textColor = green
                recibo_title_style.alignment = TA_CENTER
                story.append(Paragraph(f"Recibo #{recibo_data.get('numero_secuencial', i + 1)}", recibo_title_style))
                story.append(Spacer(1, 0.2 * inch))

                # Información del recibo
                info_style = styles['Normal']
                info_style.fontSize = 11
                info_style.leading = 14

                # Crear información del recibo
                info_fields = [
                    f"<b>Beneficiario:</b> {recibo_data.get('nombre_beneficiario', 'N/A')}",
                    f"<b>Valor:</b> ${recibo_data.get('valor', 'N/A')}",
                    f"<b>Entidad:</b> {recibo_data.get('entidad_bancaria', 'N/A')}",
                    f"<b>Cuenta:</b> {recibo_data.get('numero_cuenta', 'N/A')}",
                    f"<b>Referencia:</b> {recibo_data.get('referencia', 'N/A')}",
                    f"<b>Fecha:</b> {recibo_data.get('fecha_aplicacion', 'N/A')}",
                    f"<b>Estado:</b> {recibo_data.get('estado_pago', 'N/A')}",
                    f"<b>Concepto:</b> {recibo_data.get('concepto', 'N/A')}"
                ]

                for field in info_fields:
                    story.append(Paragraph(field, info_style))
                    story.append(Spacer(1, 0.08 * inch))

                story.append(Spacer(1, 0.25 * inch))

                # Agregar imagen del recibo
                if imagen_data and imagen_data.get('imagen_data'):
                    try:
                        # Crear imagen desde datos
                        img = self._crear_imagen_desde_data(imagen_data['imagen_data'])

                        # Calcular dimensiones optimizadas para que quepa en la página
                        # Espacio disponible: altura total - espacio usado por título e información
                        # Aproximadamente: 792 - 72 (márgenes top/bottom) - 150 (info) = 570 puntos
                        max_width = self.width - (2 * self.margin)
                        max_height = 4.5 * inch  # Espacio seguro para la imagen

                        # Escalar imagen manteniendo proporción
                        img_width, img_height = img.size
                        scale = min(max_width / img_width, max_height / img_height)

                        final_width = img_width * scale
                        final_height = img_height * scale

                        # Agregar imagen al PDF
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)

                        rl_image = RLImage(img_buffer, width=final_width, height=final_height)
                        story.append(rl_image)

                    except Exception as e:
                        logger.error(f"Error agregando imagen del recibo {i + 1}: {str(e)}")
                        error_msg = f"<i>Error cargando imagen: {str(e)}</i>"
                        story.append(Paragraph(error_msg, info_style))
                else:
                    story.append(Paragraph("<i>Imagen no disponible</i>", info_style))

                # Forzar salto de página después de cada recibo (excepto el último)
                if i < len(recibos_data) - 1:
                    story.append(PageBreak())

            # Construir PDF
            doc.build(story)

            pdf_bytes = buffer.getvalue()

            if self.output_path:
                with open(self.output_path, 'wb') as output_file:
                    output_file.write(pdf_bytes)
                logger.info(f"PDF generado exitosamente en: {self.output_path}")
            else:
                logger.info("PDF generado exitosamente en memoria")

            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            raise
    
    def _crear_imagen_desde_data(self, imagen_data: bytes) -> Image.Image:
        """Crea objeto PIL Image desde datos binarios"""
        try:
            return Image.open(io.BytesIO(imagen_data))
        except Exception as e:
            logger.error(f"Error creando imagen desde datos: {str(e)}")
            raise
    
    def generar_pdf_simple(self, recibos_data: List[Dict]) -> bytes:
        """
        Genera PDF simple sin imágenes (fallback)
        """
        try:
            logger.info("Generando PDF simple sin imágenes")
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=LETTER)  # Letter (Carta) tamaño: 612 x 792 puntos
            width, height = LETTER
            
            y_position = height - 50
            
            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredText(width / 2, y_position, "Recibos Separados")
            y_position -= 40
            
            for i, recibo in enumerate(recibos_data):
                # Nueva página si es necesario
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica-Bold", 14)
                
                # Título del recibo
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, f"Recibo #{recibo.get('numero_secuencial', i + 1)}")
                y_position -= 20
                
                # Información del recibo
                c.setFont("Helvetica", 10)
                info_lines = [
                    f"Beneficiario: {recibo.get('nombre_beneficiario', 'N/A')}",
                    f"Valor: ${recibo.get('valor', 'N/A')}",
                    f"Entidad: {recibo.get('entidad_bancaria', 'N/A')}",
                    f"Cuenta: {recibo.get('numero_cuenta', 'N/A')}",
                    f"Referencia: {recibo.get('referencia', 'N/A')}",
                    f"Fecha: {recibo.get('fecha_aplicacion', 'N/A')}",
                    f"Estado: {recibo.get('estado_pago', 'N/A')}",
                    f"Concepto: {recibo.get('concepto', 'N/A')}"
                ]
                
                for line in info_lines:
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
                        c.setFont("Helvetica", 10)
                    
                    c.drawString(70, y_position, line)
                    y_position -= 15
                
                y_position -= 20
            
            c.save()
            pdf_bytes = buffer.getvalue()

            if self.output_path:
                with open(self.output_path, 'wb') as output_file:
                    output_file.write(pdf_bytes)
                logger.info(f"PDF simple generado en: {self.output_path}")
            else:
                logger.info("PDF simple generado en memoria")

            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generando PDF simple: {str(e)}")
            raise
    
    def agregar_metadatos_pdf(self, metadatos: Dict):
        """Agrega metadatos al PDF guardado en disco"""
        if not self.output_path:
            logger.warning("No se proporcionó output_path para agregar metadatos al PDF")
            return
        try:
            c = canvas.Canvas(self.output_path)
            c.setTitle(metadatos.get('titulo', 'Recibos Separados'))
            c.setAuthor(metadatos.get('autor', 'Sistema de Separación de Recibos'))
            c.setSubject(metadatos.get('subject', 'Separación de Recibos PDF'))
            c.setCreator(metadatos.get('creator', 'Aplicación Django'))
            c.setProducer(metadatos.get('producer', 'Separador de Recibos v1.0'))
            
            # Agregar marca de agua si se especifica
            if metadatos.get('marca_agua'):
                c.saveState()
                c.setFillColor(black)
                c.setFont("Helvetica", 8)
                c.drawCentredText(
                    self.width / 2, 
                    20, 
                    metadatos['marca_agua']
                )
                c.restoreState()
            
            c.save()
            
        except Exception as e:
            logger.error(f"Error agregando metadatos: {str(e)}")
    
    def generar_reporte_estadisticas(self, recibos_data: List[Dict]) -> bytes:
        """
        Genera un reporte con estadísticas de los recibos
        """
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=LETTER)  # Letter (Carta) tamaño: 612 x 792 puntos
            width, height = LETTER
            
            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredText(width / 2, height - 50, "Reporte de Estadísticas")
            y_position = height - 80
            
            # Calcular estadísticas
            total_recibos = len(recibos_data)
            valores = [float(r.get('valor', 0)) for r in recibos_data if r.get('valor')]
            valor_total = sum(valores) if valores else 0
            valor_promedio = valor_total / len(valores) if valores else 0
            
            entidades = [r.get('entidad_bancaria', '') for r in recibos_data if r.get('entidad_bancaria')]
            entidades_unicas = list(set(entidades))
            
            # Escribir estadísticas
            c.setFont("Helvetica", 12)
            stats = [
                f"Total de Recibos: {total_recibos}",
                f"Valor Total: ${valor_total:,.2f}",
                f"Valor Promedio: ${valor_promedio:,.2f}",
                f"Entidades Bancarias: {len(entidades_unicas)}",
                "",
                "Entidades encontradas:",
            ]
            
            for stat in stats:
                c.drawString(50, y_position, stat)
                y_position -= 20
            
            # Listar entidades
            for entidad in sorted(entidades_unicas):
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
                    c.setFont("Helvetica", 12)
                
                c.drawString(70, y_position, f"• {entidad}")
                y_position -= 15
            
            c.save()

            pdf_bytes = buffer.getvalue()

            if self.output_path:
                stats_path = self.output_path.replace('.pdf', '_estadisticas.pdf')
                with open(stats_path, 'wb') as output_file:
                    output_file.write(pdf_bytes)
                logger.info(f"Reporte de estadísticas generado: {stats_path}")
            else:
                logger.info("Reporte de estadísticas generado en memoria")

            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            raise