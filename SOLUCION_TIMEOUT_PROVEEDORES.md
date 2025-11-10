# 🔧 Solución: WORKER TIMEOUT al Guardar Proveedores

## 🔴 Problema Identificado

Al completar el formulario de registro de proveedores en Railway, la página se quedaba cargando indefinidamente y luego se caía con este error en los logs:

```
[2025-11-10 14:35:01 +0000] [1] [CRITICAL] WORKER TIMEOUT (pid:28)
[2025-11-10 09:35:01 -0500] [28] [INFO] Worker exiting (pid: 28)
[2025-11-10 14:35:02 +0000] [1] [ERROR] Worker (pid:28) exited with code 1
```

### Causa Raíz

El **envío de correos electrónicos** estaba bloqueando el worker de Gunicorn:

1. Al guardar un proveedor, se intenta enviar un correo de notificación
2. El sistema primero intenta **Gmail API** (líneas 38-78 de `core/utils.py`)
3. Si Gmail API no está disponible/falla, intenta **SMTP** (líneas 180-228)
4. **SMTP con Gmail es muy lento** (puede tardar 30-60 segundos)
5. Gunicorn tiene un timeout de 30 segundos (ahora 120, pero aún insuficiente)
6. El worker se mata antes de que el correo se envíe

Aunque se usaba `threading.Thread()` para enviar correos en background (líneas 102-107 de `proveedores/views.py`), **los threads no liberan el worker en Gunicorn workers síncronos**.

---

## ✅ Solución Implementada (TEMPORAL)

### Cambios Realizados

#### 1. **Deshabilitar notificaciones por correo en producción**

**Archivo**: `proveedores/views.py` (líneas 96-115)

```python
# TEMPORAL: Notificaciones por correo deshabilitadas en producción para evitar timeouts
# Enviar notificación por correo en un hilo separado (no bloqueante)
if settings.DEBUG:
    try:
        url_proveedor = request.build_absolute_uri(
            reverse('proveedores:detalle', args=[proveedor.pk])
        )
        # Iniciar thread para enviar correo sin bloquear la respuesta
        thread = threading.Thread(
            target=enviar_notificacion_async,
            args=(proveedor.pk, url_proveedor),
            daemon=True
        )
        thread.start()
        logger.info(f'Thread de notificación iniciado para proveedor {proveedor.pk}')
    except Exception as e:
        # Si falla al iniciar el thread, solo registrar el error
        logger.error(f'Error al iniciar thread de notificación: {str(e)}')
else:
    logger.info(f'Notificaciones por correo deshabilitadas en producción. Proveedor {proveedor.pk} registrado correctamente.')
```

**Resultado**:
- En **desarrollo local** (`DEBUG=True`): Los correos se envían normalmente
- En **producción Railway** (`DEBUG=False`): Los correos están deshabilitados, el proveedor se guarda instantáneamente

#### 2. **Deshabilitar endpoint de prueba de correos**

**Archivo**: `core/views.py` (líneas 166-197)

El endpoint `/test-email/?send=true` ahora retorna un mensaje de advertencia en producción sin intentar enviar correos.

---

## 🚀 Próximos Pasos (Solución Definitiva)

Para volver a habilitar las notificaciones por correo de forma segura, hay **3 opciones**:

### **Opción 1: Configurar Celery + Redis** ⭐ RECOMENDADA

Celery es un sistema de colas de tareas asíncronas que permite procesar trabajos pesados (como envío de correos) fuera del ciclo request-response.

#### Pasos:

1. **Agregar Redis en Railway**:
   - Dashboard de Railway → New → Database → Add Redis
   - Automáticamente se crea la variable `${{Redis.REDIS_URL}}`

2. **Configurar variables de entorno**:
   ```env
   CELERY_BROKER_URL=${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
   ```

3. **Crear archivo `contabiliadad/celery.py`**:
   ```python
   from celery import Celery
   import os

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')

   app = Celery('contabiliadad')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()
   ```

4. **Crear tarea asíncrona en `proveedores/tasks.py`**:
   ```python
   from celery import shared_task
   from core.utils import notificar_nuevo_proveedor
   from .models import Proveedor

   @shared_task
   def enviar_notificacion_proveedor(proveedor_id, url_proveedor):
       proveedor = Proveedor.objects.get(pk=proveedor_id)
       notificar_nuevo_proveedor(
           proveedor=proveedor,
           contactos=proveedor.contactos.all(),
           impuestos=proveedor.impuestos.all(),
           url_sistema=url_proveedor
       )
   ```

5. **Actualizar `proveedores/views.py`**:
   ```python
   from .tasks import enviar_notificacion_proveedor

   # En lugar de threading.Thread(), usar:
   enviar_notificacion_proveedor.delay(proveedor.pk, url_proveedor)
   ```

6. **Actualizar `Procfile`**:
   ```
   web: gunicorn contabiliadad.wsgi --config gunicorn_config.py
   worker: celery -A contabiliadad worker --loglevel=info
   ```

7. **Agregar worker en Railway**:
   - Settings → New Service → Worker
   - Command: `celery -A contabiliadad worker --loglevel=info`

**Ventajas**:
- ✅ Envío de correos 100% asíncrono
- ✅ Reintentos automáticos en caso de fallo
- ✅ Escalable para otras tareas pesadas (procesamiento de PDFs, etc.)

**Desventajas**:
- ⚠️ Requiere Redis (costo adicional en Railway si superas el free tier)
- ⚠️ Más complejidad en la arquitectura

---

### **Opción 2: Usar Gmail API exclusivamente** ⚡ RÁPIDA

Gmail API es 10x más rápida que SMTP (2-3 segundos vs 30-60 segundos).

#### Pasos:

1. **Configurar `GMAIL_TOKEN_JSON` en Railway**:
   - Ejecutar localmente: `python manage.py authorize_gmail`
   - Copiar el contenido de `token.json`
   - Agregar variable en Railway: `GMAIL_TOKEN_JSON=<contenido-del-token>`

2. **Eliminar fallback a SMTP**:
   - Modificar `core/utils.py` línea 177 para NO intentar SMTP si Gmail API falla
   - Retornar False inmediatamente si no hay credenciales

3. **Habilitar correos en producción**:
   - Revertir cambio en `proveedores/views.py` (quitar `if settings.DEBUG`)

**Ventajas**:
- ✅ Muy rápido (2-3 segundos)
- ✅ No requiere infraestructura adicional
- ✅ Solución simple

**Desventajas**:
- ⚠️ Requiere mantener token OAuth actualizado
- ⚠️ Límite de 500 correos/día (Gmail API quota)
- ⚠️ Si el token expira, los correos fallan hasta renovar manualmente

---

### **Opción 3: Webhook externo / API de terceros**

Usar servicios como SendGrid, Mailgun, Amazon SES o Resend para envío de correos vía API.

#### Pasos:

1. **Crear cuenta en servicio de email (ejemplo: SendGrid)**:
   - Obtener API Key

2. **Instalar librería**:
   ```bash
   pip install sendgrid
   ```

3. **Actualizar `requirements.txt`**:
   ```
   sendgrid==6.11.0
   ```

4. **Configurar en `core/utils.py`**:
   ```python
   from sendgrid import SendGridAPIClient
   from sendgrid.helpers.mail import Mail

   def enviar_con_sendgrid(asunto, mensaje, destinatarios):
       message = Mail(
           from_email=settings.DEFAULT_FROM_EMAIL,
           to_emails=destinatarios,
           subject=asunto,
           html_content=mensaje
       )
       sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
       response = sg.send(message)
       return response.status_code == 202
   ```

5. **Agregar variable en Railway**:
   ```env
   SENDGRID_API_KEY=<tu-api-key>
   ```

**Ventajas**:
- ✅ Muy rápido (API asíncrona)
- ✅ Alto volumen de correos
- ✅ Reportes y analytics incluidos

**Desventajas**:
- ⚠️ Costo mensual (después del free tier)
- ⚠️ Dependencia de servicio externo

---

## 📊 Comparación de Soluciones

| Solución | Velocidad | Costo | Complejidad | Recomendación |
|----------|-----------|-------|-------------|---------------|
| **Celery + Redis** | ⚡⚡⚡⚡⚡ | 💰 (Redis) | 🔧🔧🔧 | ⭐⭐⭐⭐⭐ |
| **Gmail API** | ⚡⚡⚡⚡ | 💰 (Gratis) | 🔧🔧 | ⭐⭐⭐⭐ |
| **SendGrid/API** | ⚡⚡⚡⚡⚡ | 💰💰 | 🔧🔧 | ⭐⭐⭐ |
| **SMTP (actual)** | ⚡ | 💰 (Gratis) | 🔧 | ❌ NO USAR |

---

## 🧪 Verificar la Solución

Después de hacer deploy con los cambios actuales:

1. **Probar registro de proveedor**:
   - Ir a: `https://tu-app.railway.app/proveedores/nuevo/`
   - Completar el formulario
   - Click en "Completar Registro"
   - ✅ Debería redirigir a la página de éxito instantáneamente

2. **Verificar en logs de Railway**:
   ```
   [INFO] Notificaciones por correo deshabilitadas en producción. Proveedor <UUID> registrado correctamente.
   ```

3. **Verificar endpoint de diagnóstico**:
   - Ir a: `https://tu-app.railway.app/test-email/`
   - Debería mostrar:
     ```json
     {
       "configuracion": { ... },
       "info": "Para enviar correo de prueba, agrega ?send=true a la URL"
     }
     ```
   - Ir a: `https://tu-app.railway.app/test-email/?send=true`
   - Debería mostrar:
     ```json
     {
       "advertencia": "⚠️ ENVÍO DE CORREOS DESHABILITADO TEMPORALMENTE EN PRODUCCIÓN",
       "razon": "Los correos causan WORKER TIMEOUT en Railway (>30 segundos)",
       "solucion": "Configurar sistema de colas (Celery + Redis) o usar webhooks/API asíncrona"
     }
     ```

---

## 📝 Resumen de Cambios

### Archivos Modificados:

1. **`proveedores/views.py`**:
   - Línea 10: Agregado `from django.conf import settings`
   - Líneas 96-115: Notificaciones solo en modo DEBUG

2. **`core/views.py`**:
   - Líneas 166-197: Endpoint de prueba deshabilitado en producción

### ¿Qué funciona ahora?

- ✅ Guardar proveedores en Railway (sin timeout)
- ✅ Formulario completa exitosamente
- ✅ Proveedor se guarda en la base de datos
- ✅ Redirección a página de éxito
- ❌ Notificaciones por correo (temporalmente deshabilitadas)

---

## 🔮 Próximo Commit

Para hacer deploy de estos cambios:

```bash
git add proveedores/views.py core/views.py SOLUCION_TIMEOUT_PROVEEDORES.md
git commit -m "fix: deshabilitar envío de correos en producción para evitar worker timeout

- Notificaciones por correo solo en modo DEBUG
- Endpoint de prueba deshabilitado en producción
- Proveedor se guarda instantáneamente sin timeouts
- Documentar solución temporal y opciones definitivas (Celery/Gmail API)"
git push
```

Railway desplegará automáticamente y el problema estará resuelto.

---

**Fecha**: 2025-11-10
**Autor**: Claude Code Assistant
**Estado**: ✅ SOLUCIONADO (temporal)
**Siguiente paso**: Implementar Celery + Redis para correos asíncronos
