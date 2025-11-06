# Guía Rápida de Inicio - Configuración para Despliegue

## 📋 Resumen

Tu aplicación ya está lista para despliegue. He configurado:

- ✅ Variables de entorno con `python-decouple`
- ✅ Cloudinary para almacenamiento de archivos
- ✅ Gmail para envío de correos a `recepcionfacturaschvs@gmail.com`
- ✅ WhiteNoise para archivos estáticos
- ✅ PostgreSQL para producción (SQLite en desarrollo)
- ✅ Configuraciones de seguridad
- ✅ Archivos de despliegue (Procfile, runtime.txt)
- ✅ Utilidades para envío de correos

## 🚀 Pasos Inmediatos

### 1. Crear archivo .env local

```bash
cp .env.example .env
```

Luego edita `.env` y configura al menos estas variables para desarrollo:

```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generar SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 2. Probar localmente

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias (si aún no lo has hecho)
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar servidor
python manage.py runserver
```

### 3. Configurar Gmail (IMPORTANTE)

Para enviar correos a `recepcionfacturaschvs@gmail.com`:

1. Ve a https://myaccount.google.com/apppasswords
2. Genera una "App Password"
3. Actualiza tu `.env`:

```env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password de 16 caracteres
```

**Probar envío de correos:**
```bash
python manage.py shell
```

```python
from core.utils import enviar_correo_notificacion

enviar_correo_notificacion(
    asunto='Prueba desde Django',
    mensaje='Este es un correo de prueba.'
)
```

### 4. Configurar Cloudinary

1. Crea cuenta en https://cloudinary.com
2. Obtén tus credenciales del dashboard
3. Actualiza tu `.env`:

```env
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz
```

## 📧 Usar el Sistema de Correos

He creado utilidades en `core/utils.py` para facilitar el envío de correos:

### Envío simple:

```python
from core.utils import enviar_correo_notificacion

enviar_correo_notificacion(
    asunto='Nueva factura',
    mensaje='Se ha recibido una nueva factura.'
)
```

### Envío con HTML:

```python
from core.utils import enviar_correo_notificacion

enviar_correo_notificacion(
    asunto='Nueva factura',
    mensaje='Se ha recibido una nueva factura.',
    html_mensaje='<h1>Nueva Factura</h1><p>Detalles...</p>'
)
```

### Envío con template:

```python
from core.utils import enviar_correo_desde_template

enviar_correo_desde_template(
    asunto='Nueva factura',
    template_name='emails/notificacion_factura.html',
    context={
        'numero_factura': '12345',
        'proveedor': 'ACME Corp',
        'monto': '$1,000.00'
    }
)
```

### Notificar nueva factura:

```python
from core.utils import notificar_nueva_factura

notificar_nueva_factura(
    numero_factura='12345',
    proveedor='ACME Corp',
    monto='$1,000.00'
)
```

## 🌐 Despliegue a Producción

### Opción 1: Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Crear app
heroku create nombre-app

# Agregar PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# Configurar variables de entorno
heroku config:set SECRET_KEY="tu-secret-key"
heroku config:set DEBUG=False
heroku config:set EMAIL_HOST_USER="tu-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="tu-app-password"
heroku config:set CLOUDINARY_CLOUD_NAME="tu-cloud-name"
heroku config:set CLOUDINARY_API_KEY="tu-api-key"
heroku config:set CLOUDINARY_API_SECRET="tu-api-secret"

# Deploy
git push heroku main

# Ejecutar migraciones
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py collectstatic --noinput
```

### Opción 2: Railway

1. Ve a https://railway.app
2. Conecta tu repositorio de GitHub
3. Agrega PostgreSQL
4. Configura las variables de entorno en el dashboard
5. Railway desplegará automáticamente

### Opción 3: Render

1. Ve a https://render.com
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio
4. Agrega PostgreSQL
5. Configura las variables de entorno
6. Render desplegará automáticamente

## 📁 Archivos Creados

- `contabiliadad/settings.py` - Actualizado con todas las configuraciones
- `.env.example` - Plantilla de variables de entorno
- `Procfile` - Para Heroku/Railway
- `runtime.txt` - Versión de Python
- `.slugignore` - Archivos a ignorar en despliegue
- `core/utils.py` - Utilidades para envío de correos
- `templates/emails/` - Templates para correos
- `DEPLOYMENT.md` - Documentación completa de despliegue
- `QUICKSTART.md` - Esta guía

## 🔐 Variables de Entorno Críticas

Para producción, DEBES configurar:

```env
SECRET_KEY=<genera-una-nueva>
DEBUG=False
ALLOWED_HOSTS=<tu-dominio.com>
DATABASE_URL=<url-postgresql>
EMAIL_HOST_USER=<tu-email@gmail.com>
EMAIL_HOST_PASSWORD=<app-password>
CLOUDINARY_CLOUD_NAME=<cloud-name>
CLOUDINARY_API_KEY=<api-key>
CLOUDINARY_API_SECRET=<api-secret>
```

## 📚 Documentación Adicional

- `DEPLOYMENT.md` - Guía completa de despliegue
- `.env.example` - Todas las variables disponibles
- `core/utils.py` - Documentación de funciones de correo

## ⚠️ Notas Importantes

1. **NUNCA** subas el archivo `.env` a GitHub (ya está en `.gitignore`)
2. Usa **App Password** de Gmail, no tu contraseña normal
3. En producción, siempre usa `DEBUG=False`
4. Genera una nueva `SECRET_KEY` para producción
5. Los correos se enviarán a `recepcionfacturaschvs@gmail.com` por defecto

## 🆘 ¿Necesitas Ayuda?

1. Lee `DEPLOYMENT.md` para instrucciones detalladas
2. Verifica el archivo `.env.example` para todas las variables
3. Revisa los logs de tu plataforma de despliegue
4. Ejecuta `python manage.py check --deploy` para verificar configuración

## ✅ Checklist Pre-Despliegue

- [ ] Crear archivo `.env` con tus credenciales
- [ ] Generar nueva `SECRET_KEY`
- [ ] Configurar App Password de Gmail
- [ ] Crear cuenta en Cloudinary y obtener credenciales
- [ ] Probar envío de correos localmente
- [ ] Ejecutar migraciones localmente
- [ ] Recopilar archivos estáticos
- [ ] Hacer commit de los cambios
- [ ] Elegir plataforma de despliegue (Heroku/Railway/Render)
- [ ] Configurar variables de entorno en producción
- [ ] Desplegar aplicación
- [ ] Ejecutar migraciones en producción
- [ ] Crear superusuario en producción
- [ ] Probar funcionalidad básica
- [ ] Verificar envío de correos en producción
- [ ] Verificar subida de archivos a Cloudinary

---

**¡Tu aplicación está lista para despegar! 🚀**
