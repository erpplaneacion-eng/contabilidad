# 📊 Sistema de Contabilidad CHVS

Sistema integral de gestión contable desarrollado con Django, diseñado para automatizar y optimizar los procesos de registro de proveedores y procesamiento de recibos bancarios.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Despliegue](#-despliegue)
- [API Reference](#-api-reference)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## ✨ Características

### 🏢 Gestión de Proveedores

- **Registro completo de proveedores** (personas naturales y jurídicas)
- **Gestión de contactos** asociados a cada proveedor
- **Control de impuestos y retenciones** (Fuente, ICA, Transporte)
- **Gestión documental** (RUT, certificados, documentos bancarios)
- **Firma electrónica** con canvas integrado
- **Notificaciones automáticas** por correo al registrar proveedores
- **Sistema de roles** (Administrador, Contador, Operador)
- **Dashboard con estadísticas** y reportes visuales

### 📄 Procesamiento de Recibos PDF

- **Detección automática de recibos** en PDFs multipágina
- **Extracción de información** (beneficiario, valor, banco, fecha)
- **Generación de PDFs individuales** por recibo
- **Exportación de imágenes** de alta calidad por recibo
- **Procesamiento asíncrono** con threads (opcional: Celery)
- **Almacenamiento en la nube** con Cloudinary
- **Validación y seguimiento** de recibos procesados
- **Reportes y estadísticas** de procesamiento

### 🔐 Seguridad y Autenticación

- **Sistema de autenticación** integrado con Django
- **Perfiles de usuario** con roles y permisos
- **Control de acceso** por áreas (Proveedores, Recibos)
- **Tokens OAuth 2.0** para Gmail API
- **HTTPS** y certificados SSL en producción
- **Variables de entorno** para secretos sensibles

### 📧 Sistema de Notificaciones

- **Envío de correos** con Gmail API (2-3 segundos)
- **Templates HTML** personalizables
- **Notificaciones automáticas** al registrar proveedores
- **Sistema de fallback** a SMTP para adjuntos
- **Logs detallados** de envíos

---

## 🏗️ Arquitectura

### Stack Tecnológico

```
┌─────────────────────────────────────────┐
│         Frontend (Templates)            │
│   Django Templates + Bootstrap 5        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Backend (Django 5.2)           │
│  ├── core (autenticación, utils)       │
│  ├── proveedores (gestión)             │
│  └── separador_recibos (procesamiento) │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Base de Datos & Storage           │
│  ├── PostgreSQL (producción)           │
│  ├── SQLite (desarrollo)               │
│  └── Cloudinary (archivos)             │
└─────────────────────────────────────────┘
```

### Aplicaciones Django

#### 1. **core** - Funcionalidad Compartida
```python
core/
├── models.py          # UserProfile, Departamento, Municipio
├── views.py           # Dashboard principal, diagnósticos
├── utils.py           # Envío de correos (Gmail API + SMTP)
├── decorators.py      # Decoradores de permisos
├── context_processors.py  # Contexto global
└── management/
    └── commands/
        └── import_csv_data.py  # Importar datos geográficos
```

**Responsabilidades:**
- Gestión de usuarios y perfiles
- Sistema de roles y permisos
- Utilidades de correo (Gmail API)
- Datos geográficos (Colombia)
- Dashboard unificado

#### 2. **proveedores** - Gestión de Proveedores
```python
proveedores/
├── models.py          # Proveedor, Contacto, Impuesto, DocumentoRequerido
├── views.py           # CRUD de proveedores
├── forms.py           # Formularios con validaciones
├── admin.py           # Administración Django
└── templates/
    └── proveedores/
        ├── formulario_proveedor.html
        ├── proveedor_list.html
        ├── proveedor_detail.html
        └── success.html
```

**Modelos principales:**
- `Proveedor`: Información general, identificación, ubicación
- `Contacto`: Contactos adicionales del proveedor
- `Impuesto`: Retenciones y tarifas aplicables
- `DocumentoRequerido`: RUT, certificados, documentos legales

#### 3. **separador_recibos** - Procesamiento de PDFs
```python
separador_recibos/
├── models.py          # ProcesamientoRecibo, ReciboDetectado
├── views.py           # Upload, procesamiento, visualización
├── tasks.py           # Tareas asíncronas (Celery)
├── forms.py           # Formulario de configuración
└── utils/
    ├── pdf_processor.py      # Detección de recibos
    ├── image_extractor.py    # Extracción de imágenes
    ├── pdf_generator.py      # Generación de PDFs
    └── storage_utils.py      # Cloudinary/FileSystem
```

**Flujo de procesamiento:**
1. Usuario sube PDF con múltiples recibos
2. Sistema detecta coordenadas de cada recibo
3. Extrae imágenes de alta calidad
4. Genera PDFs individuales
5. Guarda en Cloudinary (producción) o filesystem (local)
6. Notifica por correo al usuario

---

## 📦 Requisitos

### Requisitos del Sistema

- **Python**: 3.12+
- **PostgreSQL**: 13+ (producción)
- **Redis**: 6+ (opcional, para Celery)
- **Poppler**: Para procesamiento de PDFs (`pdf2image`)
- **ImageMagick**: Para procesamiento avanzado de imágenes

### Dependencias Python

```txt
Django>=5.2.0
gunicorn==21.2.0
psycopg[binary]>=3.1.18
python-decouple==3.8
whitenoise==6.6.0
dj-database-url==2.1.0

# Almacenamiento
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
django-storages==1.14.2

# Procesamiento de PDFs
PyPDF2==3.0.1
pdfplumber==0.10.3
reportlab==4.0.7
PyMuPDF>=1.24.0
pdf2image==1.17.0
Pillow>=12.0.0

# Computer Vision
opencv-python==4.8.1.78
matplotlib==3.7.2
Wand==0.6.13

# Correos (Gmail API)
google-api-python-client>=2.0.0
google-auth-oauthlib>=1.0.0

# Tareas asíncronas (opcional)
celery==5.3.4
redis==5.0.1

# Utilidades
python-dateutil==2.8.2
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/erpplaneacion-eng/contabilidad.git
cd contabilidad
```

### 2. Crear Entorno Virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Poppler (para pdf2image)

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Descargar de: https://github.com/oschwartz10612/poppler-windows/releases
# Agregar al PATH
```

### 5. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 6. Generar SECRET_KEY

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copia el resultado en `.env`:
```env
SECRET_KEY=tu-secret-key-generada
```

---

## ⚙️ Configuración

### Archivo `.env`

Crea un archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos (dejar vacío para SQLite en desarrollo)
DATABASE_URL=

# Gmail API (para notificaciones)
GMAIL_TOKEN_JSON={"token":"...","refresh_token":"..."}

# Cloudinary (almacenamiento de archivos)
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# Email de notificaciones
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com

# Celery (opcional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Configurar Gmail API

#### 1. Crear proyecto en Google Cloud Console

1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto
3. Habilita **Gmail API**
4. Crea credenciales OAuth 2.0
5. Descarga el archivo `credentials.json`

#### 2. Autorizar la aplicación

```bash
python manage.py authorize_gmail
```

Esto abrirá tu navegador para autorizar. Generará un archivo `token.json`.

#### 3. Configurar en Railway/Producción

```bash
# Convertir token a una línea
cat token.json | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)))"

# Copiar output y agregar como variable GMAIL_TOKEN_JSON en Railway
```

### Configurar Cloudinary

1. Crear cuenta en: https://cloudinary.com
2. Obtener credenciales del Dashboard
3. Agregar en `.env`:

```env
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz
```

---

## 🎯 Uso

### Desarrollo Local

#### 1. Aplicar Migraciones

```bash
python manage.py migrate
```

#### 2. Cargar Datos Iniciales (Departamentos y Municipios de Colombia)

```bash
python manage.py import_csv_data
```

#### 3. Crear Superusuario

```bash
python manage.py createsuperuser
```

#### 4. Recopilar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

#### 5. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

Accede a: http://localhost:8000

### Acceso al Sistema

- **Login**: http://localhost:8000/login/
- **Admin**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/dashboard/dashboard/
- **Proveedores**: http://localhost:8000/proveedores/
- **Separador de Recibos**: http://localhost:8000/separador/

### Flujos de Trabajo

#### Registrar un Proveedor

1. Login al sistema
2. Ir a: **Proveedores → Nuevo Proveedor**
3. Llenar formulario:
   - **Sección 1**: Información General
   - **Sección 2**: Contactos (mínimo 1)
   - **Sección 3**: Impuestos y Retenciones
   - **Sección 4**: Documentos Requeridos
   - **Sección 5**: Firma Digital
4. Click en **"Completar Registro"**
5. ✅ Se envía notificación por correo automáticamente

#### Procesar Recibos PDF

1. Login al sistema
2. Ir a: **Separador de Recibos → Subir PDF**
3. Seleccionar archivo PDF con múltiples recibos
4. Configurar opciones:
   - Calidad de imagen (Baja/Media/Alta)
   - Tamaño de imagen (Pequeña/Mediana/Grande)
   - Formato de salida (PDF Imágenes / PDF Texto / Ambos)
5. Click en **"Procesar PDF"**
6. Esperar procesamiento (~30 seg por 10 recibos)
7. Ver resultados:
   - Lista de recibos detectados
   - Información extraída (beneficiario, valor, banco)
   - Descargar PDFs individuales
   - Descargar imágenes de cada recibo

---

## 🌐 Despliegue

### Railway (Recomendado)

#### 1. Conectar Repositorio

1. Ve a: https://railway.app
2. **New Project → Deploy from GitHub repo**
3. Selecciona tu repositorio

#### 2. Agregar PostgreSQL

1. **New → Database → Add PostgreSQL**
2. Railway crea automáticamente la variable `DATABASE_URL`

#### 3. Configurar Variables de Entorno

En **Settings → Variables**, agrega:

```env
SECRET_KEY=<genera-una-nueva>
DEBUG=False
ALLOWED_HOSTS=<tu-dominio>.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Gmail API
GMAIL_TOKEN_JSON=<tu-token-en-una-linea>

# Cloudinary
CLOUDINARY_CLOUD_NAME=<tu-cloud-name>
CLOUDINARY_API_KEY=<tu-api-key>
CLOUDINARY_API_SECRET=<tu-api-secret>

# Email
NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com

# Seguridad
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### 4. Deploy Automático

Railway desplegará automáticamente cuando hagas push a `main`.

#### 5. Ejecutar Migraciones

```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py import_csv_data
```

### Heroku

Ver guía completa en: [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Render

Ver guía completa en: [`DEPLOYMENT.md`](DEPLOYMENT.md)

---

## 📚 API Reference

### Endpoints de Diagnóstico

#### Test de Email (Gmail API)

```http
GET /test-email/?send=true
```

**Respuesta exitosa:**
```json
{
  "exito": true,
  "mensaje": "✅ Correo enviado exitosamente vía Gmail API",
  "destinatario": "recepcionfacturaschvs@gmail.com",
  "tiempo_estimado": "2-3 segundos"
}
```

#### Test de Gmail API

```http
GET /test-gmail-api/?send=true
```

**Respuesta exitosa:**
```json
{
  "exito": true,
  "mensaje": "✅ Correo enviado con Gmail API exitosamente",
  "metodo": "Gmail API"
}
```

### Endpoints Principales

#### Proveedores

```http
GET  /proveedores/                    # Lista de proveedores
GET  /proveedores/nuevo/              # Formulario nuevo proveedor
POST /proveedores/nuevo/              # Crear proveedor
GET  /proveedores/<pk>/               # Detalle de proveedor
GET  /proveedores/<pk>/editar/        # Formulario editar
POST /proveedores/<pk>/editar/        # Actualizar proveedor
POST /proveedores/<pk>/eliminar/      # Eliminar proveedor
```

#### Separador de Recibos

```http
GET  /separador/                      # Dashboard
GET  /separador/subir/                # Formulario upload
POST /separador/subir/                # Procesar PDF
GET  /separador/procesamiento/<id>/   # Detalle procesamiento
GET  /separador/historial/            # Historial de procesamientos
GET  /separador/recibo/<id>/          # Detalle de recibo
```

---

## 🔧 Comandos de Gestión

### Importar Datos Geográficos

```bash
python manage.py import_csv_data
```

Carga departamentos y municipios de Colombia desde CSV.

### Autorizar Gmail API

```bash
python manage.py authorize_gmail
```

Genera archivo `token.json` para Gmail API.

### Crear Superusuario

```bash
python manage.py createsuperuser
```

### Ejecutar Tests

```bash
python manage.py test
```

### Verificar Configuración para Producción

```bash
python manage.py check --deploy
```

---

## 🐛 Troubleshooting

### Problema: WORKER TIMEOUT en Railway

**Síntoma**: El worker se reinicia cada 30 segundos

**Causa**: Imports pesados al inicio de Django (Google API)

**Solución**: Ya implementado con lazy imports en `core/utils.py`

---

### Problema: Token de Gmail expirado

**Síntoma**: Errores de `invalid_grant` al enviar correos

**Solución**:
```bash
python manage.py authorize_gmail
cat token.json | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)))"
# Actualizar GMAIL_TOKEN_JSON en Railway
```

---

### Problema: value too long for type character varying

**Síntoma**: Error al guardar proveedor

**Solución**: Aumentar límite del campo en el modelo y crear migración:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Problema: No se detectan recibos en PDF

**Posibles causas**:
- PDF es imagen escaneada (necesita OCR)
- Formato no estándar
- Resolución muy baja

**Solución**: Verificar que el PDF tenga texto seleccionable

---

## 📖 Documentación Adicional

- **[QUICKSTART.md](QUICKSTART.md)** - Guía rápida de inicio
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guía completa de despliegue
- **[CONFIGURAR_GMAIL_API_RAILWAY.md](CONFIGURAR_GMAIL_API_RAILWAY.md)** - Configurar Gmail API
- **[SOLUCION_TIMEOUT_PROVEEDORES.md](SOLUCION_TIMEOUT_PROVEEDORES.md)** - Solución de timeouts

---

## 🤝 Contribución

Este es un proyecto privado de **CHVS**. Para contribuir:

1. Solicitar acceso al repositorio
2. Crear una rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Convención de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: formato, punto y coma faltante, etc
refactor: refactorización de código
test: agregar tests
chore: tareas de mantenimiento
```

---

## 📄 Licencia

**Propietario**: Cooperativa de Ahorro y Crédito Valle Solidario (CHVS)

Este software es propiedad privada. Todos los derechos reservados.

**Restricciones**:
- ❌ No se permite el uso comercial sin autorización
- ❌ No se permite la redistribución
- ❌ No se permite la modificación sin autorización

**Contacto**: ERP Planeación - erp.planeacion@vallesolidario.com

---

## 👥 Equipo

**Desarrollo**: ERP Planeación - Valle Solidario

**Mantenimiento**: Departamento de TI - CHVS

---

## 📊 Estadísticas del Proyecto

- **Lenguaje**: Python
- **Framework**: Django 5.2
- **Apps**: 3 (core, proveedores, separador_recibos)
- **Modelos**: 8 principales
- **Líneas de código**: ~15,000
- **Archivos**: ~80

---

## 🔄 Changelog

### [1.0.0] - 2025-11-10

#### Agregado
- ✅ Sistema completo de gestión de proveedores
- ✅ Procesamiento automático de recibos PDF
- ✅ Integración con Gmail API para notificaciones
- ✅ Almacenamiento en Cloudinary
- ✅ Sistema de roles y permisos
- ✅ Dashboard con estadísticas
- ✅ Despliegue en Railway

#### Corregido
- 🐛 WORKER TIMEOUT en Railway (lazy imports)
- 🐛 Límite de caracteres en código de actividad económica
- 🐛 Timeout en envío de correos (Gmail API)

---

## 📞 Soporte

Para soporte técnico:

- **Email**: erp.planeacion@vallesolidario.com
- **Issues**: [GitHub Issues](https://github.com/erpplaneacion-eng/contabilidad/issues)

---

<div align="center">

**Desarrollado con ❤️ por ERP Planeación - Valle Solidario**

[🏠 Sitio Web](https://vallesolidario.com) • [📧 Email](mailto:erp.planeacion@vallesolidario.com)

</div>
