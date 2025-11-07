# 📧 Configurar Email en Railway

## Problema Actual
El formulario de proveedores se guarda correctamente, pero los correos de notificación NO se envían porque **faltan las variables de entorno de Gmail en Railway**.

## Solución: Configurar Variables de Entorno en Railway

### Paso 1: Acceder a tu proyecto en Railway

1. Ve a [railway.app](https://railway.app)
2. Inicia sesión
3. Selecciona tu proyecto de contabilidad

### Paso 2: Agregar Variables de Entorno

1. Haz clic en tu servicio web
2. Ve a la pestaña **"Variables"**
3. Agrega las siguientes variables (haz clic en "+ New Variable" para cada una):

```bash
# Configuración de Email (REQUERIDAS)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Credenciales de Gmail (USA LAS QUE TIENES EN .env LOCAL)
EMAIL_HOST_USER=erp.planeacion@vallesolidario.com
EMAIL_HOST_PASSWORD=nyczispxalvsymco

# Email remitente y destinatario
DEFAULT_FROM_EMAIL=erp.planeacion@vallesolidario.com
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com
```

### Paso 3: Guardar y Redesplegar

1. Haz clic en **"Save"** o **"Update Variables"**
2. Railway automáticamente redesplegará tu aplicación
3. Espera 2-3 minutos para que termine el despliegue

### Paso 4: Verificar que Funciona

1. Ve a tu aplicación en Railway
2. Diligencia un formulario de proveedor
3. Verifica que:
   - El formulario se guarde correctamente ✓
   - Llegue el correo a `recepcionfacturaschvs@gmail.com` ✓

## 🔍 Diagnóstico Local (Opcional)

Si quieres probar la configuración localmente antes de desplegar:

```bash
python test_email_config.py
```

Este script:
- Verifica que todas las variables estén configuradas
- Te permite enviar un correo de prueba
- Te muestra errores detallados si algo falla

## 📋 Checklist de Variables Requeridas

Asegúrate de que TODAS estas variables estén configuradas en Railway:

- [ ] `EMAIL_BACKEND`
- [ ] `EMAIL_HOST`
- [ ] `EMAIL_PORT`
- [ ] `EMAIL_USE_TLS`
- [ ] `EMAIL_HOST_USER` ⭐ (Esta falta actualmente)
- [ ] `EMAIL_HOST_PASSWORD` ⭐ (Esta falta actualmente)
- [ ] `DEFAULT_FROM_EMAIL`
- [ ] `NOTIFICATION_EMAIL`

## 🔐 Nota de Seguridad

El password `nyczispxalvsymco` que estás usando es un **App Password de Gmail**, que es lo correcto.

**NUNCA** uses la contraseña normal de Gmail, siempre usa App Passwords.

## ❓ Preguntas Frecuentes

### ¿Cómo genero un nuevo App Password de Gmail?

1. Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Inicia sesión con tu cuenta de Gmail
3. Selecciona "Correo" y "Otro (nombre personalizado)"
4. Pon nombre: "Django Railway"
5. Haz clic en "Generar"
6. Copia el password de 16 caracteres que te da
7. Úsalo en `EMAIL_HOST_PASSWORD`

### ¿Por qué no llegan los correos?

Revisa los logs de Railway buscando estos mensajes:

- `✓` **"Thread de notificación iniciado"** → El thread se creó correctamente
- `✓` **"Correo enviado exitosamente"** → El correo se envió
- `✗` **"Configuración de email incompleta"** → Faltan variables de entorno
- `✗` **"Error al enviar correo"** → Problema con credenciales o Gmail

### ¿Puedo usar otro servicio de email que no sea Gmail?

Sí, solo cambia estas variables:

```bash
# Para Outlook/Office365
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587

# Para SendGrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587

# Etc.
```

## 📞 Soporte

Si después de configurar las variables los correos NO se envían:

1. Revisa los logs de Railway (pestaña "Deployments" → último deploy → "View Logs")
2. Busca mensajes que empiecen con "Error al enviar correo"
3. Ejecuta localmente: `python test_email_config.py` para diagnosticar

---

**Última actualización**: 2025-11-07
