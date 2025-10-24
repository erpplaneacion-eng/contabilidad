# Sistema de Registro de Proveedores

## Descripción
Sistema web Django para gestionar el registro y actualización de datos de proveedores. Permite a los proveedores diligenciar un formulario completo con su información, contactos, impuestos y documentos requeridos.

## Características
- Formulario web completo para registro de proveedores
- Gestión de contactos múltiples por proveedor
- Manejo de información de impuestos y retenciones
- Carga de documentos requeridos (RUT, certificados, etc.)
- Panel de administración Django para gestionar todos los proveedores
- Base de datos SQLite
- Interfaz responsive con Bootstrap 5

## Requisitos
- Python 3.8 o superior
- Django 5.2.0 o superior
- Pillow 12.0.0 o superior

## Instalación

### 1. Activar el entorno virtual

**En Windows:**
```bash
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear superusuario (si no existe)
```bash
python manage.py createsuperuser
```

**Credenciales por defecto ya creadas:**
- Usuario: `admin`
- Contraseña: `admin123`
- **IMPORTANTE:** Cambie esta contraseña después del primer inicio de sesión

## Ejecutar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: http://127.0.0.1:8000/

## URLs Principales

### Para Proveedores (Formularios públicos)
- **Formulario de Registro:** http://127.0.0.1:8000/proveedores/registro/
- **Actualizar Proveedor:** http://127.0.0.1:8000/proveedores/actualizar/<id>/

### Para Administradores
- **Panel de Administración:** http://127.0.0.1:8000/admin/
- **Lista de Proveedores:** http://127.0.0.1:8000/proveedores/lista/
- **Detalle de Proveedor:** http://127.0.0.1:8000/proveedores/detalle/<id>/

## Estructura del Proyecto

```
contabilidad/
├── contabiliadad/              # Proyecto Django principal
│   ├── settings.py            # Configuración del proyecto
│   ├── urls.py                # URLs principales
│   └── proveedores/           # App de proveedores
│       ├── models.py          # Modelos de datos
│       ├── forms.py           # Formularios
│       ├── views.py           # Vistas
│       ├── admin.py           # Configuración del admin
│       ├── urls.py            # URLs de la app
│       └── templates/         # Templates HTML
│           └── proveedores/
│               ├── base.html
│               ├── formulario_proveedor.html
│               └── success.html
├── static/                     # Archivos estáticos
│   └── css/
│       └── style.css
├── media/                      # Archivos subidos
│   ├── firmas/
│   ├── sellos/
│   └── documentos/
├── db.sqlite3                 # Base de datos
├── manage.py                  # Script de gestión Django
└── requirements.txt           # Dependencias

```

## Modelos de Datos

### Proveedor
Información principal del proveedor: nombre, identificación, dirección, contacto, condiciones de pago, etc.

### Contacto
Contactos adicionales del proveedor (hasta 5 por proveedor).

### Impuesto
Información de impuestos y retenciones del proveedor.

### DocumentoRequerido
Documentos legales y certificados del proveedor (RUT, Cámara de Comercio, etc.).

## Uso del Sistema

### Para Proveedores

1. Acceda a la URL de registro: http://127.0.0.1:8000/proveedores/registro/
2. Complete todos los campos requeridos (marcados con *)
3. Agregue contactos adicionales si es necesario
4. Complete la información de impuestos
5. Seleccione las condiciones de pago
6. Cargue los documentos requeridos
7. Proporcione los datos del representante legal
8. Haga clic en "Registrar Proveedor"
9. Recibirá una página de confirmación con los detalles del registro

### Para Actualizar Datos

1. Use la URL: http://127.0.0.1:8000/proveedores/actualizar/<id>/
2. El ID se proporciona en la página de confirmación después del registro
3. Modifique los campos necesarios
4. Haga clic en "Actualizar Datos"

### Para Administradores

1. Acceda al panel de administración: http://127.0.0.1:8000/admin/
2. Inicie sesión con las credenciales de superusuario
3. Podrá ver y administrar:
   - Proveedores
   - Contactos
   - Impuestos
   - Documentos requeridos

## Compartir el Formulario con Proveedores

### Opción 1: Desarrollo Local
Si el servidor está en desarrollo local, solo será accesible desde su máquina.

### Opción 2: Servidor Local en Red
Para compartir en su red local:

1. Encuentre su dirección IP local:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` o `ip addr`

2. Ejecute el servidor permitiendo conexiones externas:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. Comparta la URL con los proveedores:
   ```
   http://<su-ip-local>:8000/proveedores/registro/
   ```

### Opción 3: Despliegue en Producción
Para un uso real en producción, debe desplegar la aplicación en:
- Un servidor VPS (DigitalOcean, Linode, AWS, etc.)
- Plataformas como Heroku, PythonAnywhere, Railway, etc.

**IMPORTANTE:** Antes de desplegar en producción:
1. Cambie `DEBUG = False` en settings.py
2. Configure un `SECRET_KEY` seguro
3. Configure `ALLOWED_HOSTS` con su dominio
4. Use una base de datos más robusta (PostgreSQL, MySQL)
5. Configure un servidor web real (Nginx + Gunicorn)
6. Configure HTTPS con certificado SSL

## Archivos Media

Los archivos subidos por los proveedores se guardan en:
- `media/firmas/` - Firmas digitales
- `media/sellos/` - Sellos de empresas
- `media/documentos/` - Documentos legales

## Personalización

### Cambiar estilos
Edite el archivo: `static/css/style.css`

### Modificar campos del formulario
Edite los modelos en: `contabiliadad/proveedores/models.py`
Luego ejecute:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Agregar validaciones
Edite los formularios en: `contabiliadad/proveedores/forms.py`

## Soporte y Mantenimiento

### Ver registros
Los registros de proveedores se almacenan en la base de datos SQLite: `db.sqlite3`

### Hacer respaldo
```bash
# Respaldo de la base de datos
cp db.sqlite3 db.sqlite3.backup

# Respaldo de archivos media
cp -r media/ media.backup/
```

### Limpiar base de datos (CUIDADO)
```bash
# Esto eliminará TODOS los datos
python manage.py flush
```

## Solución de Problemas

### Error: "No module named 'django'"
Asegúrese de que el entorno virtual esté activado e instale las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "Table doesn't exist"
Ejecute las migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Los archivos estáticos no cargan
Ejecute:
```bash
python manage.py collectstatic
```

### Error de permisos en archivos media
Asegúrese de que la carpeta `media/` tenga permisos de escritura.

## Licencia
Este proyecto es para uso interno de la organización.

## Contacto
Para soporte técnico, contacte al administrador del sistema.
