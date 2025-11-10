"""
Utilidades generales para el proyecto
"""

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scope para Gmail API
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def enviar_con_gmail_api(asunto, mensaje_html, mensaje_texto, destinatarios):
    """
    Envía correo usando Gmail API (MÁS RÁPIDO que SMTP).
    Esta es la misma implementación que funciona en GESTION_HUMANA_CHVS.

    Returns:
        bool: True si se envió exitosamente, False si falló
    """
    try:
        # Cargar credenciales: primero de variable de entorno (Railway) o archivo (desarrollo local)
        token_data = None

        # Intentar cargar desde variable de entorno (Railway)
        gmail_token_json = os.getenv('GMAIL_TOKEN_JSON')
        if gmail_token_json:
            try:
                token_data = json.loads(gmail_token_json)
                logger.info('Credenciales de Gmail API cargadas desde variable de entorno')
            except json.JSONDecodeError as e:
                logger.error(f'Error parseando GMAIL_TOKEN_JSON: {str(e)}')
                return False

        # Si no hay variable de entorno, intentar cargar desde archivo (desarrollo local)
        if not token_data:
            BASE_DIR = settings.BASE_DIR
            token_path = BASE_DIR / 'token.json'

            if token_path.exists():
                try:
                    with open(token_path, 'r') as token_file:
                        token_data = json.load(token_file)
                    logger.info(f'Credenciales de Gmail API cargadas desde {token_path}')
                except Exception as e:
                    logger.error(f'Error leyendo token.json: {str(e)}')
                    return False
            else:
                logger.warning(f'No se encontró token.json en {token_path} ni variable GMAIL_TOKEN_JSON')
                # Si no hay token de Gmail API, retornar False para usar SMTP como fallback
                return False

        # Crear credenciales desde el token
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes', GMAIL_SCOPES)
        )

        # Refrescar el token si es necesario
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Construir el servicio de Gmail
        service = build('gmail', 'v1', credentials=creds)

        # Crear mensaje de correo
        message = MIMEMultipart('alternative')
        message['To'] = ', '.join(destinatarios) if isinstance(destinatarios, list) else destinatarios
        message['From'] = settings.DEFAULT_FROM_EMAIL
        message['Subject'] = asunto

        # Adjuntar contenido HTML
        if mensaje_html:
            html_part = MIMEText(mensaje_html, 'html', 'utf-8')
            message.attach(html_part)
        else:
            text_part = MIMEText(mensaje_texto, 'plain', 'utf-8')
            message.attach(text_part)

        # Codificar el mensaje en base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = {'raw': raw_message}

        # Enviar correo
        service.users().messages().send(userId='me', body=send_message).execute()

        logger.info(f'Correo enviado exitosamente vía Gmail API a {destinatarios}')
        return True

    except Exception as e:
        logger.error(f'Error al enviar correo vía Gmail API: {str(e)}')
        return False


def enviar_correo_notificacion(
    asunto,
    mensaje,
    destinatarios=None,
    html_mensaje=None,
    archivo_adjunto=None,
    fail_silently=False,
    timeout=30
):
    """
    Envía un correo de notificación usando Gmail API EXCLUSIVAMENTE.

    Args:
        asunto (str): Asunto del correo
        mensaje (str): Mensaje en texto plano
        destinatarios (list, optional): Lista de emails destinatarios.
                                       Por defecto usa NOTIFICATION_EMAIL de settings
        html_mensaje (str, optional): Mensaje en formato HTML
        archivo_adjunto (tuple, optional): Tupla con (nombre_archivo, contenido, tipo_mime)
        fail_silently (bool): Si es False, lanza excepciones en caso de error

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario

    Ejemplo de uso:
        # Envío simple
        enviar_correo_notificacion(
            asunto='Nueva factura recibida',
            mensaje='Se ha recibido una nueva factura para procesamiento.'
        )

        # Con HTML
        enviar_correo_notificacion(
            asunto='Nueva factura recibida',
            mensaje='Se ha recibido una nueva factura.',
            html_mensaje='<h1>Nueva factura</h1><p>Se ha recibido una nueva factura.</p>'
        )

        # Con archivo adjunto
        with open('factura.pdf', 'rb') as f:
            contenido = f.read()
        enviar_correo_notificacion(
            asunto='Factura adjunta',
            mensaje='Se adjunta la factura.',
            archivo_adjunto=('factura.pdf', contenido, 'application/pdf')
        )
    """
    try:
        # Si no se especifican destinatarios, usar el email de notificaciones
        if destinatarios is None:
            destinatarios = [settings.NOTIFICATION_EMAIL]

        # USAR GMAIL API EXCLUSIVAMENTE (rápido, 2-3 segundos)
        if archivo_adjunto is None:  # Gmail API solo si no hay adjuntos
            logger.info("Enviando correo vía Gmail API...")
            api_exitoso = enviar_con_gmail_api(
                asunto=asunto,
                mensaje_html=html_mensaje,
                mensaje_texto=mensaje,
                destinatarios=destinatarios
            )

            if api_exitoso:
                logger.info("✅ Correo enviado exitosamente vía Gmail API")
                return True
            else:
                logger.error("❌ Gmail API falló. Verifica que GMAIL_TOKEN_JSON esté configurado en Railway.")
                logger.error("Para configurar: python manage.py authorize_gmail y copiar token.json a Railway")
                if not fail_silently:
                    raise Exception("Gmail API no disponible. Configure GMAIL_TOKEN_JSON en Railway.")
                return False

        # Si hay archivo adjunto, usar EmailMessage con SMTP (Gmail API no soporta adjuntos fácilmente)
        else:
            logger.warning("Archivo adjunto detectado. Usando SMTP como fallback (Gmail API no soporta adjuntos).")

            # Verificar configuración de SMTP
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.error("Configuración de SMTP incompleta para adjuntos. Verifique EMAIL_HOST_USER y EMAIL_HOST_PASSWORD.")
                if not fail_silently:
                    raise Exception("SMTP no configurado para enviar adjuntos.")
                return False

            email = EmailMessage(
                subject=asunto,
                body=html_mensaje if html_mensaje else mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=destinatarios,
            )

            # Si hay HTML, configurarlo
            if html_mensaje:
                email.content_subtype = 'html'

            # Adjuntar archivo
            nombre_archivo, contenido, tipo_mime = archivo_adjunto
            email.attach(nombre_archivo, contenido, tipo_mime)

            # Enviar
            email.send(fail_silently=fail_silently)
            logger.info(f"Correo con adjunto enviado exitosamente vía SMTP a {', '.join(destinatarios)}")
            return True

    except Exception as e:
        logger.error(f"Error al enviar correo: {str(e)}")
        if not fail_silently:
            raise
        return False


def enviar_correo_desde_template(
    asunto,
    template_name,
    context,
    destinatarios=None,
    archivo_adjunto=None,
    fail_silently=False
):
    """
    Envía un correo usando un template HTML de Django.

    Args:
        asunto (str): Asunto del correo
        template_name (str): Ruta al template HTML (ej: 'emails/notificacion_factura.html')
        context (dict): Contexto para renderizar el template
        destinatarios (list, optional): Lista de emails destinatarios
        archivo_adjunto (tuple, optional): Tupla con (nombre_archivo, contenido, tipo_mime)
        fail_silently (bool): Si es False, lanza excepciones en caso de error

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario

    Ejemplo de uso:
        enviar_correo_desde_template(
            asunto='Nueva factura recibida',
            template_name='emails/notificacion_factura.html',
            context={
                'numero_factura': '12345',
                'proveedor': 'ACME Corp',
                'monto': '$1,000.00'
            }
        )
    """
    try:
        # Renderizar el template HTML
        html_mensaje = render_to_string(template_name, context)

        # Generar versión texto plano del HTML
        mensaje_texto = strip_tags(html_mensaje)

        # Enviar usando la función principal
        return enviar_correo_notificacion(
            asunto=asunto,
            mensaje=mensaje_texto,
            destinatarios=destinatarios,
            html_mensaje=html_mensaje,
            archivo_adjunto=archivo_adjunto,
            fail_silently=fail_silently
        )

    except Exception as e:
        logger.error(f"Error al enviar correo desde template: {str(e)}")
        if not fail_silently:
            raise
        return False


def notificar_nueva_factura(numero_factura, proveedor, monto, archivo_pdf=None):
    """
    Envía una notificación cuando se recibe una nueva factura.

    Args:
        numero_factura (str): Número de la factura
        proveedor (str): Nombre del proveedor
        monto (str): Monto de la factura
        archivo_pdf (bytes, optional): Contenido del PDF para adjuntar

    Returns:
        bool: True si se envió correctamente

    Ejemplo de uso:
        notificar_nueva_factura(
            numero_factura='12345',
            proveedor='ACME Corp',
            monto='$1,000.00'
        )
    """
    asunto = f'Nueva Factura Recibida - {numero_factura}'
    mensaje = f"""
    Se ha recibido una nueva factura para procesamiento:

    Número de Factura: {numero_factura}
    Proveedor: {proveedor}
    Monto: {monto}

    Por favor revise la factura en el sistema.

    ---
    Este es un correo automático generado por el Sistema de Contabilidad CHVS.
    """

    archivo_adjunto = None
    if archivo_pdf:
        archivo_adjunto = (f'factura_{numero_factura}.pdf', archivo_pdf, 'application/pdf')

    return enviar_correo_notificacion(
        asunto=asunto,
        mensaje=mensaje,
        archivo_adjunto=archivo_adjunto
    )


def notificar_error_procesamiento(descripcion_error, detalles=None):
    """
    Envía una notificación cuando ocurre un error en el procesamiento.

    Args:
        descripcion_error (str): Descripción breve del error
        detalles (str, optional): Detalles adicionales del error

    Returns:
        bool: True si se envió correctamente

    Ejemplo de uso:
        notificar_error_procesamiento(
            descripcion_error='Error al procesar PDF',
            detalles='El archivo no es un PDF válido'
        )
    """
    asunto = 'Error en el Sistema de Contabilidad CHVS'
    mensaje = f"""
    Se ha detectado un error en el sistema:

    Error: {descripcion_error}
    """

    if detalles:
        mensaje += f"""

    Detalles:
    {detalles}
    """

    mensaje += """

    Por favor revise el sistema lo antes posible.

    ---
    Este es un correo automático generado por el Sistema de Contabilidad CHVS.
    """

    return enviar_correo_notificacion(
        asunto=asunto,
        mensaje=mensaje,
        fail_silently=True  # No fallar silenciosamente en errores críticos
    )


def notificar_nuevo_proveedor(proveedor, contactos=None, impuestos=None, url_sistema=None):
    """
    Envía una notificación cuando se registra un nuevo proveedor.

    Args:
        proveedor: Instancia del modelo Proveedor
        contactos (list, optional): Lista de contactos del proveedor
        impuestos (list, optional): Lista de impuestos del proveedor
        url_sistema (str, optional): URL para ver el proveedor en el sistema

    Returns:
        bool: True si se envió correctamente

    Ejemplo de uso:
        from core.utils import notificar_nuevo_proveedor

        notificar_nuevo_proveedor(
            proveedor=proveedor,
            contactos=proveedor.contactos.all(),
            impuestos=proveedor.impuestos.all(),
            url_sistema=request.build_absolute_uri(reverse('proveedores:detalle', args=[proveedor.pk]))
        )
    """
    from django.utils import timezone

    # Mapeo de naturaleza jurídica para mostrar texto legible
    naturaleza_juridica_map = {
        'PERSONA_NATURAL': 'Persona Natural',
        'PERSONA_JURIDICA': 'Persona Jurídica',
        'SOCIEDAD': 'Sociedad',
        'ENTIDAD_PUBLICA': 'Entidad Pública',
        'EXTRANJERO': 'Extranjero'
    }

    asunto = f'Nuevo Proveedor Registrado - {proveedor.nombre_razon_social}'

    # Preparar contexto para el template
    context = {
        'proveedor': proveedor,
        'naturaleza_juridica_display': naturaleza_juridica_map.get(
            proveedor.naturaleza_juridica,
            proveedor.naturaleza_juridica
        ),
        'fecha_registro': timezone.localtime(proveedor.fecha_creacion).strftime('%d/%m/%Y %I:%M %p'),
        'contactos': contactos if contactos else [],
        'impuestos': [],
        'url_sistema': url_sistema,
        'observaciones': None
    }

    # Preparar información de impuestos (solo los que aplican)
    if impuestos:
        context['impuestos'] = [
            {
                'tipo_impuesto_display': imp.get_tipo_impuesto_display(),
                'porcentaje': imp.porcentaje
            }
            for imp in impuestos if imp.aplica
        ]

    # Enviar correo usando template
    return enviar_correo_desde_template(
        asunto=asunto,
        template_name='emails/notificacion_proveedor.html',
        context=context,
        fail_silently=True  # No fallar para no interrumpir el proceso de registro
    )
