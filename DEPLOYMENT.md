# Guía de Despliegue - Sistema de Contabilidad CHVS

Esta guía te ayudará a preparar y desplegar tu aplicación Django en producción.

## Tabla de Contenidos

- [Configuración Inicial](#configuración-inicial)
- [Configuración de Gmail](#configuración-de-gmail)
- [Configuración de Cloudinary](#configuración-de-cloudinary)
- [Variables de Entorno](#variables-de-entorno)
- [Despliegue en Heroku](#despliegue-en-heroku)
- [Despliegue en Railway](#despliegue-en-railway)
- [Despliegue en Render](#despliegue-en-render)
- [Verificación Post-Despliegue](#verificación-post-despliegue)

---

## Configuración Inicial

### 1. Clonar y configurar el proyecto localmente

```bash
# Copiar archivo de ejemplo de variables de entorno
cp .env.example .env

# Editar .env con tus valores reales
nano .env  # o usa tu editor preferido
```

### 2. Generar una SECRET_KEY segura

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copia el resultado y actualiza la variable `SECRET_KEY` en tu archivo `.env`.

---

## Configuración de Gmail

Para que la aplicación pueda enviar correos a `recepcionfacturaschvs@gmail.com`, necesitas configurar Gmail con una **App Password**.

### Pasos:

1. **Inicia sesión en tu cuenta de Gmail** que se usará para enviar correos

2. **Habilita la verificación en dos pasos:**
   - Ve a https://myaccount.google.com/security
   - En "Acceso a Google", habilita "Verificación en dos pasos"
   - Sigue los pasos para configurarla

3. **Genera una App Password:**
   - Ve a https://myaccount.google.com/apppasswords
   - En "Seleccionar app", elige "Correo"
   - En "Seleccionar dispositivo", elige "Otro" y ponle un nombre como "Django CHVS"
   - Haz clic en "Generar"
   - **Copia la contraseña de 16 caracteres** (sin espacios)

4. **Actualiza tu archivo .env:**
   ```env
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=abcd-efgh-ijkl-mnop  # La App Password que generaste
   DEFAULT_FROM_EMAIL=tu-email@gmail.com
   NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com
   ```

### Probar el envío de correos (opcional):

```python
# En el shell de Django
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Prueba de correo',
    'Este es un mensaje de prueba.',
    settings.DEFAULT_FROM_EMAIL,
    [settings.NOTIFICATION_EMAIL],
    fail_silently=False,
)
```

---

## Configuración de Cloudinary

Cloudinary se usará para almacenar archivos y PDFs en la nube.

### Pasos:

1. **Crear cuenta en Cloudinary:**
   - Ve a https://cloudinary.com/
   - Crea una cuenta gratuita
   - Verifica tu email

2. **Obtener credenciales:**
   - Ve al Dashboard: https://cloudinary.com/console
   - Encontrarás tus credenciales:
     - **Cloud Name**
     - **API Key**
     - **API Secret**

3. **Actualiza tu archivo .env:**
   ```env
   CLOUDINARY_CLOUD_NAME=tu-cloud-name
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz
   ```

4. **Configuración opcional - Carpetas de organización:**

   En tu dashboard de Cloudinary, puedes crear carpetas para organizar:
   - `chvs/pdfs_originales/`
   - `chvs/pdfs_procesados/`
   - `chvs/imagenes_recibos/`

---

## Variables de Entorno

### Variables Obligatorias para Producción:

```env
# Django
SECRET_KEY=tu-secret-key-generada
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos (PostgreSQL)
DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_bd

# Email
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret
```

### Variables Opcionales:

```env
# Security (se configuran automáticamente a True cuando DEBUG=False)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Celery (si usas tareas asíncronas)
CELERY_BROKER_URL=redis://...
CELERY_RESULT_BACKEND=redis://...
```

---

## Despliegue en Heroku

### Requisitos previos:
- Cuenta en Heroku (https://heroku.com)
- Heroku CLI instalado

### Pasos:

1. **Instalar Heroku CLI:**
   ```bash
   # Windows
   # Descargar desde: https://devcenter.heroku.com/articles/heroku-cli

   # Mac
   brew tap heroku/brew && brew install heroku

   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login en Heroku:**
   ```bash
   heroku login
   ```

3. **Crear aplicación:**
   ```bash
   heroku create nombre-de-tu-app
   ```

4. **Agregar PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:essential-0
   ```

5. **Configurar variables de entorno:**
   ```bash
   heroku config:set SECRET_KEY="tu-secret-key"
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS="nombre-de-tu-app.herokuapp.com"

   # Gmail
   heroku config:set EMAIL_HOST_USER="tu-email@gmail.com"
   heroku config:set EMAIL_HOST_PASSWORD="tu-app-password"
   heroku config:set DEFAULT_FROM_EMAIL="tu-email@gmail.com"
   heroku config:set NOTIFICATION_EMAIL="recepcionfacturaschvs@gmail.com"

   # Cloudinary
   heroku config:set CLOUDINARY_CLOUD_NAME="tu-cloud-name"
   heroku config:set CLOUDINARY_API_KEY="tu-api-key"
   heroku config:set CLOUDINARY_API_SECRET="tu-api-secret"
   ```

6. **Desplegar:**
   ```bash
   git push heroku main
   ```

7. **Ejecutar migraciones:**
   ```bash
   heroku run python manage.py migrate
   ```

8. **Crear superusuario:**
   ```bash
   heroku run python manage.py createsuperuser
   ```

9. **Recopilar archivos estáticos:**
   ```bash
   heroku run python manage.py collectstatic --noinput
   ```

---

## Despliegue en Railway

Railway es una alternativa moderna y más fácil que Heroku.

### Pasos:

1. **Crear cuenta en Railway:**
   - Ve a https://railway.app
   - Regístrate con GitHub

2. **Nuevo proyecto:**
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio

3. **Agregar PostgreSQL:**
   - En tu proyecto, click en "+ New"
   - Selecciona "Database" → "PostgreSQL"

4. **Configurar variables de entorno:**
   - Ve a tu servicio → "Variables"
   - Agrega todas las variables del archivo `.env.example`:
     - `SECRET_KEY`
     - `DEBUG=False`
     - `ALLOWED_HOSTS` (Railway te da un dominio automático)
     - Variables de Gmail
     - Variables de Cloudinary

5. **Railway detectará automáticamente** tu `Procfile` y `runtime.txt`

6. **El despliegue es automático** cada vez que hagas push a tu repo

---

## Despliegue en Render

Render es otra excelente opción para Django.

### Pasos:

1. **Crear cuenta en Render:**
   - Ve a https://render.com
   - Regístrate con GitHub

2. **Nuevo Web Service:**
   - Dashboard → "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

3. **Configurar servicio:**
   - **Name:** nombre-de-tu-app
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn contabiliadad.wsgi:application`

4. **Agregar PostgreSQL:**
   - Dashboard → "New +" → "PostgreSQL"
   - Conecta la base de datos a tu Web Service

5. **Variables de entorno:**
   - En tu Web Service → "Environment"
   - Agrega todas las variables necesarias
   - Render automáticamente provee `DATABASE_URL`

---

## Verificación Post-Despliegue

### Checklist de verificación:

- [ ] La aplicación carga correctamente
- [ ] Puedes hacer login
- [ ] Los archivos estáticos se cargan (CSS, JS, imágenes)
- [ ] Puedes subir archivos (se guardan en Cloudinary)
- [ ] Los correos se envían correctamente a `recepcionfacturaschvs@gmail.com`
- [ ] Las migraciones se aplicaron correctamente
- [ ] HTTPS funciona correctamente
- [ ] No hay errores 500 en los logs

### Comandos útiles para debugging:

```bash
# Heroku
heroku logs --tail
heroku run python manage.py check --deploy

# Railway
railway logs

# Render
# Ver logs en el dashboard
```

### Probar envío de correos en producción:

```bash
# Heroku
heroku run python manage.py shell

# Railway
railway run python manage.py shell

# Render
# Usar la consola en el dashboard
```

Luego ejecuta:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Prueba desde producción',
    'Este correo es una prueba desde el servidor de producción.',
    settings.DEFAULT_FROM_EMAIL,
    [settings.NOTIFICATION_EMAIL],
    fail_silently=False,
)
```

---

## Troubleshooting

### Error: "Secret key not set"
- Verifica que `SECRET_KEY` esté configurada en las variables de entorno

### Error: "DisallowedHost"
- Agrega tu dominio a `ALLOWED_HOSTS` en las variables de entorno

### Los archivos no se suben a Cloudinary
- Verifica las credenciales de Cloudinary
- Revisa los logs para errores específicos

### Los correos no se envían
- Verifica que estés usando una App Password, no tu contraseña normal
- Verifica que la verificación en dos pasos esté habilitada en Gmail
- Revisa los logs para errores de autenticación

### Error 500
- Establece `DEBUG=False` (nunca uses DEBUG=True en producción)
- Revisa los logs de tu plataforma
- Ejecuta `python manage.py check --deploy` localmente

---

## Soporte

Para más información o ayuda, contacta al equipo de desarrollo.

**Importante:** Nunca compartas tus credenciales (SECRET_KEY, contraseñas, API secrets) en repositorios públicos o chats.
