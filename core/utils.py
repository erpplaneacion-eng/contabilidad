"""
Utilidades generales para el proyecto
"""

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def enviar_correo_notificacion(
    asunto,
    mensaje,
    destinatarios=None,
    html_mensaje=None,
    archivo_adjunto=None,
    fail_silently=False
):
    """
    Envía un correo de notificación.

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

        # Si no hay archivo adjunto, usar send_mail simple
        if archivo_adjunto is None:
            resultado = send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                html_message=html_mensaje,
                fail_silently=fail_silently,
            )

            if resultado > 0:
                logger.info(f"Correo enviado exitosamente a {', '.join(destinatarios)}")
                return True
            else:
                logger.warning(f"No se pudo enviar el correo a {', '.join(destinatarios)}")
                return False

        # Si hay archivo adjunto, usar EmailMessage
        else:
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
            logger.info(f"Correo con adjunto enviado exitosamente a {', '.join(destinatarios)}")
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
