# 🚀 Instrucciones para Configurar Variables en Railway

## ❌ Problemas Encontrados en tu `.env` Actual

### 1. **SECRET_KEY Incompleta** (CRÍTICO)
```env
❌ SECRET_KEY="ie1s)"  # Solo 5 caracteres, necesita ~50
✅ SECRET_KEY=<tu-secret-key-generada-de-50-caracteres>
```

**Generar nueva SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. **DATABASE_URL con Sintaxis Incorrecta**
```env
❌ DATABASE_URL="${{Postgres.DATABASE_URL}}"  # Comillas dobles incorrectas
✅ DATABASE_URL=${{Postgres.DATABASE_URL}}     # Sin comillas
```

### 3. **Token de Gmail API Expirado**
```json
"expiry": "2025-11-01T04:23:18Z"  # ❌ Ya expiró
```
**Solución**: El sistema usará el `refresh_token` para renovarlo automáticamente. Si falla, ejecuta:
```bash
railway run python manage.py authorize_gmail
```

### 4. **Falta Redis para Celery**
Railway no tiene configurado Redis para las tareas asíncronas del separador de recibos.

### 5. **Variables de Seguridad Faltantes**
Falta configuración SSL adecuada para Railway.

---

## ✅ Paso a Paso: Configurar Variables en Railway

### **Opción 1: Desde el Dashboard Web** (Recomendado)

1. **Ve a tu proyecto en Railway**:
   ```
   https://railway.app/project/<tu-proyecto-id>
   ```

2. **Selecciona tu servicio** (contabilidad-production)

3. **Ve a Settings → Variables**

4. **Agrega/Actualiza estas variables** (clic en "New Variable"):

   ```env
   # BÁSICAS
   SECRET_KEY=<genera-una-nueva-con-el-comando-de-arriba>
   DEBUG=False
   ALLOWED_HOSTS=<tu-dominio-railway>.up.railway.app

   # BASE DE DATOS (usa referencia sin comillas)
   DATABASE_URL=${{Postgres.DATABASE_URL}}

   # EMAIL
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=<tu-email>@gmail.com
   EMAIL_HOST_PASSWORD=<tu-app-password-16-caracteres>
   DEFAULT_FROM_EMAIL=<tu-email>@gmail.com
   NOTIFICATION_EMAIL=<email-destino-notificaciones>@gmail.com

   # CLOUDINARY (obtén en https://cloudinary.com/console)
   CLOUDINARY_CLOUD_NAME=<tu-cloud-name>
   CLOUDINARY_API_KEY=<tu-api-key>
   CLOUDINARY_API_SECRET=<tu-api-secret>

   # SEGURIDAD
   SECURE_SSL_REDIRECT=False
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True

   # SUPERUSER
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@contabilidad.com
   DJANGO_SUPERUSER_PASSWORD=<tu-password-seguro>
   ```

5. **Gmail API Token** (variable larga):
   - Nombre: `GMAIL_TOKEN_JSON`
   - Valor: Ejecuta `python manage.py authorize_gmail` para generar el token
   - El formato es un JSON con estos campos:
   ```json
   {"token": "...", "refresh_token": "...", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "...", "client_secret": "...", "scopes": ["https://www.googleapis.com/auth/gmail.send"]}
   ```

6. **Click en "Deploy"** para aplicar cambios

---

### **Opción 2: Desde Railway CLI**

```bash
# Instalar Railway CLI (si no lo tienes)
npm install -g @railway/cli

# Login
railway login

# Link a tu proyecto
railway link

# Agregar variables (reemplaza con tus valores reales)
railway variables set SECRET_KEY="<tu-secret-key-generada>"
railway variables set DEBUG="False"
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'
railway variables set EMAIL_HOST_USER="<tu-email>@gmail.com"
railway variables set EMAIL_HOST_PASSWORD="<tu-app-password>"
# ... (repite para todas las variables del paso 4)

# Deploy
railway up
```

---

## 🔴 CONFIGURAR REDIS PARA CELERY (Importante)

El separador de recibos usa Celery para procesamiento asíncrono. Necesitas Redis:

### **1. Agregar Redis en Railway**:

1. Ve a tu proyecto en Railway
2. Click en **"New"** → **"Database"** → **"Add Redis"**
3. Espera a que se cree (1-2 minutos)

### **2. Agregar Variables de Celery**:

Después de crear Redis, agrega estas variables usando la referencia:

```env
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
```

### **3. Actualizar Procfile** (si es necesario):

Verifica que tu `Procfile` tenga el worker de Celery:

```procfile
web: gunicorn contabiliadad.wsgi --config gunicorn_config.py
worker: celery -A contabiliadad worker --loglevel=info
```

Si no está, agrégalo y haz commit:

```bash
git add Procfile
git commit -m "feat: agregar worker de Celery al Procfile"
git push
```

Luego en Railway, agrega un **nuevo servicio**:
- Settings → New Service → Worker
- Command: `celery -A contabiliadad worker --loglevel=info`

---

## 📧 Renovar Token de Gmail API (Si falla el envío)

Si los correos no se envían por token expirado:

### **Opción 1: Desde Railway (Shell)**

```bash
railway run python manage.py authorize_gmail
```

### **Opción 2: Desde Local**

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

# Ejecutar comando
python manage.py authorize_gmail

# Copiar el nuevo token generado y actualizar en Railway
```

El comando te pedirá autorizar en tu navegador y generará un nuevo token.

---

## 🧪 Verificar Configuración

Después de actualizar las variables, prueba que todo funcione:

### **1. Verificar Email**:

```bash
railway run python manage.py shell
```

Luego en el shell:

```python
from core.utils import enviar_correo_notificacion

enviar_correo_notificacion(
    asunto="Test desde Railway",
    mensaje="Probando configuración de email",
    destinatario="tu-email@gmail.com"
)
```

### **2. Verificar Base de Datos**:

```bash
railway run python manage.py dbshell
```

Deberías conectarte a PostgreSQL.

### **3. Ver Logs en Tiempo Real**:

```bash
railway logs
```

---

## 📝 Checklist Final

Antes de hacer deploy, verifica:

- [ ] `SECRET_KEY` tiene ~50 caracteres
- [ ] `DEBUG=False`
- [ ] `DATABASE_URL` usa `${{Postgres.DATABASE_URL}}` sin comillas
- [ ] `ALLOWED_HOSTS` tiene tu dominio de Railway
- [ ] Cloudinary configurado (CLOUD_NAME, API_KEY, API_SECRET)
- [ ] Email configurado (HOST_USER, HOST_PASSWORD)
- [ ] Redis agregado en Railway
- [ ] Variables `CELERY_BROKER_URL` y `CELERY_RESULT_BACKEND` configuradas
- [ ] `SECURE_SSL_REDIRECT=False` (Railway maneja SSL)
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`

---

## 🚨 Errores Comunes

### **1. "DisallowedHost at /"**
```
❌ Tu ALLOWED_HOSTS no incluye el dominio
✅ ALLOWED_HOSTS=contabilidad-production-93f3.up.railway.app
```

### **2. "connection to server failed"**
```
❌ DATABASE_URL tiene comillas o sintaxis incorrecta
✅ DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### **3. "SMTPAuthenticationError"**
```
❌ EMAIL_HOST_PASSWORD incorrecto o token expirado
✅ Verifica App Password de Gmail (16 caracteres)
```

### **4. "Celery: Cannot connect to redis"**
```
❌ Redis no está agregado en Railway
✅ Agrega Redis Database en Railway
```

### **5. "SECRET_KEY has invalid characters"**
```
❌ SECRET_KEY con caracteres especiales sin escapar
✅ Usa la generada: bvry6^g0rx@u_x#-%dp18n-gqm8d9ijp-$g83h*(!gab4vx
```

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs: `railway logs`
2. Verifica variables: Railway Dashboard → Settings → Variables
3. Prueba en local primero con `.env` actualizado
4. Consulta documentación: https://docs.railway.app/

---

**Última actualización**: 2025-11-08
**Autor**: Claude Code Assistant
