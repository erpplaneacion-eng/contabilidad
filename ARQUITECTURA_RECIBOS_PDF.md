# Arquitectura Aplicación de Separación de Recibos PDF

## Análisis del Proyecto Existente

**Proyecto**: Sistema de Contabilidad Django
**Ubicación**: `c:/Users/User/OneDrive/Desktop/CHVS/contabilidad`
**Estructura**: Django 4.2.7 con app `proveedores`
**Base de datos**: SQLite3
**Idioma**: Español (es-co)

## Aplicación Nueva: `separador_recibos`

### 1. Librerías Requeridas

```txt
# requirements.txt additions
PyPDF2==3.0.1
pdfplumber==0.10.3
reportlab==4.0.7
Pillow==10.1.0
opencv-python==4.8.1.78
django-storages==1.14.2
celery==5.3.4
redis==5.0.1
```

### 2. Arquitectura de la Aplicación

```
separador_recibos/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── views.py
├── urls.py
├── forms.py
├── tasks.py
├── utils/
│   ├── __init__.py
│   ├── pdf_processor.py
│   ├── coordinate_detector.py
│   ├── pdf_generator.py
│   └── file_manager.py
├── templates/
│   └── separador_recibos/
│       ├── base.html
│       ├── upload.html
│       ├── process.html
│       ├── results.html
│       └── download.html
└── migrations/
    └── __init__.py
```

### 3. Modelos de Base de Datos

```python
# separador_recibos/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class ProcesamientoRecibo(models.Model):
    """Modelo para almacenar información de procesamiento"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    archivo_original = models.FileField(upload_to='pdfs_originales/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('PROCESANDO', 'Procesando'),
            ('COMPLETADO', 'Completado'),
            ('ERROR', 'Error')
        ],
        default='PENDIENTE'
    )
    total_recibos = models.PositiveIntegerField(default=0)
    archivo_resultado = models.FileField(upload_to='pdfs_procesados/', null=True, blank=True)
    
    def __str__(self):
        return f"Procesamiento {self.id} - {self.usuario.username}"

class ReciboDetectado(models.Model):
    """Modelo para almacenar información de cada recibo detectado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    procesamiento = models.ForeignKey(ProcesamientoRecibo, on_delete=models.CASCADE)
    numero_secuencial = models.PositiveIntegerField()
    coordenada_x = models.FloatField()
    coordenada_y = models.FloatField()
    ancho = models.FloatField()
    alto = models.FloatField()
    texto_extraido = models.TextField(blank=True)
    beneficiario = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['numero_secuencial']
    
    def __str__(self):
        return f"Recibo {self.numero_secuencial} - {self.procesamiento.id}"
```

### 4. Algoritmo de Detección de Recibos

#### Estrategia de Detección por Coordenadas:
1. **Análisis de Texto**: Buscar patrón "Recibo individual de pagos"
2. **Detección de Coordenadas**: Extraer posición exacta del texto
3. **Cálculo de Área**: Determinar área de cada recibo
4. **Validación**: Verificar estructura completa del recibo

#### Algoritmo Principal:
```python
def detectar_recibos_coordenadas(pdf_path):
    """
    Algoritmo principal de detección:
    1. Extraer texto con coordenadas usando pdfplumber
    2. Identificar patrones "Recibo individual de pagos"
    3. Calcular áreas de cada recibo
    4. Extraer información específica (beneficiario, valor)
    5. Validar estructura completa
    """
    recibos_detectados = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for pagina_num, pagina in enumerate(pdf.pages):
            texto_coordenadas = pagina.extract_words(x_tolerance=3, y_tolerance=3)
            
            for word in texto_coordenadas:
                if "Recibo individual de pagos" in word['text']:
                    # Calcular área del recibo
                    recibo_info = calcular_area_recibo(word, texto_coordenadas)
                    recibo_info['pagina'] = pagina_num + 1
                    recibos_detectados.append(recibo_info)
    
    return recibos_detectados
```

### 5. Generación de PDF por Página

```python
def generar_pdf_individual(recibo_data, output_path):
    """
    Generar PDF individual usando reportlab:
    1. Crear nuevo PDF
    2. Extraer imagen/área específica del PDF original
    3. Insertar en nueva página
    4. Agregar metadatos
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    
    # Configuración de página
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Extraer y colocar contenido del recibo
    # [Implementación específica de extracción e inserción]
    
    c.save()
```

### 6. Flujo de Procesamiento Asíncrono

```python
# separador_recibos/tasks.py
from celery import shared_task
from .models import ProcesamientoRecibo, ReciboDetectado
from .utils.pdf_processor import detectar_recibos_coordenadas
from .utils.pdf_generator import generar_pdf_separado

@shared_task
def procesar_recibo_pdf(procesamiento_id):
    """Tarea asíncrona para procesar PDF"""
    procesamiento = ProcesamientoRecibo.objects.get(id=procesamiento_id)
    
    try:
        procesamiento.estado = 'PROCESANDO'
        procesamiento.save()
        
        # Detectar recibos
        recibos = detectar_recibos_coordenadas(procesamiento.archivo_original.path)
        
        # Guardar información de recibos detectados
        for i, recibo in enumerate(recibos):
            ReciboDetectado.objects.create(
                procesamiento=procesamiento,
                numero_secuencial=i + 1,
                coordenada_x=recibo['x'],
                coordenada_y=recibo['y'],
                ancho=recibo['width'],
                alto=recibo['height'],
                texto_extraido=recibo['text'],
                beneficiario=recibo.get('beneficiario', ''),
                valor=recibo.get('valor')
            )
        
        # Generar PDF separado
        output_path = generar_pdf_separado(procesamiento.archivo_original.path, recibos)
        
        procesamiento.archivo_resultado.name = output_path
        procesamiento.total_recibos = len(recibos)
        procesamiento.estado = 'COMPLETADO'
        procesamiento.save()
        
    except Exception as e:
        procesamiento.estado = 'ERROR'
        procesamiento.save()
        raise e
```

### 7. Interfaz de Usuario

#### URLs Principales:
```python
# separador_recibos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('procesando/<uuid:procesamiento_id>/', views.process_status, name='process_status'),
    path('resultados/<uuid:procesamiento_id>/', views.results, name='results'),
    path('descargar/<uuid:procesamiento_id>/', views.download_result, name='download_result'),
]
```

#### Vistas Principales:
```python
# separador_recibos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from .forms import PDFUploadForm
from .models import ProcesamientoRecibo
from .tasks import procesar_recibo_pdf

@login_required
def upload_pdf(request):
    """Vista para subir archivo PDF"""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            procesamiento = form.save(commit=False)
            procesamiento.usuario = request.user
            procesamiento.save()
            
            # Iniciar procesamiento asíncrono
            procesar_recibo_pdf.delay(procesamiento.id)
            
            return redirect('process_status', procesamiento_id=procesamiento.id)
    else:
        form = PDFUploadForm()
    
    return render(request, 'separador_recibos/upload.html', {'form': form})
```

### 8. Configuración Adicional

#### Settings.py Additions:
```python
# Configuración para Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Configuración para archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración para archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 9. Testing Strategy

```python
# separador_recibos/tests/test_pdf_processor.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .utils.pdf_processor import detectar_recibos_coordenadas

class PDFProcessorTest(TestCase):
    def test_detect_single_receipt(self):
        """Test para detectar un solo recibo"""
        # [Implementación de test]
        
    def test_detect_multiple_receipts(self):
        """Test para detectar múltiples recibos"""
        # [Implementación de test]
        
    def test_invalid_pdf(self):
        """Test para PDF inválido"""
        # [Implementación de test]
```

### 10. Buenas Prácticas Implementadas

1. **Separación de Responsabilidades**: Modelos, vistas, utilidades separadas
2. **Procesamiento Asíncrono**: Celery para tareas largas
3. **Validación de Archivos**: Verificación de tipo y tamaño
4. **Logs y Monitoreo**: Tracking de estado y errores
5. **Seguridad**: Autenticación requerida
6. **Performance**: Procesamiento en background
7. **Escalabilidad**: Arquitectura modular
8. **Testing**: Suite completa de tests

### 11. Flujo de Usuario

```
1. Usuario sube PDF → 2. Sistema detecta recibos → 3. Usuario revisa resultados → 4. Descarga PDF separado
```

### 12. Consideraciones de Rendimiento

- **Archivos grandes**: Procesamiento chunk por chunk
- **Memoria**: Liberation explícita de recursos
- **Concurrencia**: Queue de tareas para evitar bloqueos
- **Almacenamiento**: Limpieza automática de archivos temporales

Esta arquitectura garantiza una aplicación robusta, escalable y mantenible para la separación automática de recibos PDF.
### 13. Funcionalidad de Captura Visual de Recibos

#### Extracción de Pantallazo por Recibo:
```python
# separador_recibos/utils/image_extractor.py
import fitz  # PyMuPDF
from PIL import Image
import io
from django.core.files.base import ContentFile

def extraer_imagen_recibo(pdf_path, coordenadas, output_size=(600, 800)):
    """
    Extrae el pantallazo visual de cada recibo usando coordenadas
    """
    doc = fitz.open(pdf_path)
    page = doc[coordenadas['pagina'] - 1]  # página (0-indexed)
    
    # Definir rectángulo basado en coordenadas detectadas
    rect = fitz.Rect(
        coordenadas['x'], 
        coordenadas['y'], 
        coordenadas['x'] + coordenadas['width'], 
        coordenadas['y'] + coordenadas['height']
    )
    
    # Extraer como imagen
    mat = fitz.Matrix(2, 2)  # Factor de escala para mejor calidad
    pix = page.get_pixmap(matrix=mat, clip=rect)
    
    # Convertir a PIL Image
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    
    # Redimensionar si es necesario
    img = img.resize(output_size, Image.Resampling.LANCZOS)
    
    return img

def procesar_y_guardar_imagenes(recibos_detectados, procesamiento_id):
    """
    Procesa todos los recibos y guarda sus imágenes
    """
    for recibo in recibos_detectados:
        img = extraer_imagen_recibo(
            recibo['pdf_path'], 
            recibo['coordenadas']
        )
        
        # Guardar imagen
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Actualizar modelo con imagen
        recibo_instance = ReciboDetectado.objects.get(
            procesamiento_id=procesamiento_id,
            numero_secuencial=recibo['numero']
        )
        recibo_instance.imagen_recibo.save(
            f'recibo_{recibo["numero"]}.png',
            ContentFile(img_buffer.read()),
            save=True
        )
```

#### Generación de PDF con Imágenes:
```python
# separador_recibos/utils/pdf_generator.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image
import io

def generar_pdf_con_imagenes(procesamiento_id):
    """
    Genera PDF con cada recibo como página individual
    usando las imágenes extraídas
    """
    recibos = ReciboDetectado.objects.filter(
        procesamiento_id=procesamiento_id
    ).order_by('numero_secuencial')
    
    output_path = f'media/pdfs_procesados/recibo_{procesamiento_id}.pdf'
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    for i, recibo in enumerate(recibos):
        # Nueva página
        if i > 0:
            c.showPage()
        
        # Agregar título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Recibo #{recibo.numero_secuencial}")
        
        # Agregar información del recibo
        y_position = height - 100
        c.setFont("Helvetica", 10)
        
        info_fields = [
            f"Beneficiario: {recibo.nombre_beneficiario or 'N/A'}",
            f"Valor: ${recibo.valor or 'N/A'}",
            f"Entidad: {recibo.entidad_bancaria or 'N/A'}",
            f"Cuenta: {recibo.numero_cuenta or 'N/A'}",
            f"Referencia: {recibo.referencia or 'N/A'}",
            f"Fecha: {recibo.fecha_aplicacion or 'N/A'}",
            f"Estado: {recibo.estado_pago or 'N/A'}"
        ]
        
        for field in info_fields:
            c.drawString(50, y_position, field)
            y_position -= 20
        
        # Insertar imagen del recibo
        if recibo.imagen_recibo:
            try:
                # Cargar imagen
                img = Image.open(recibo.imagen_recibo.path)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Calcular posición y tamaño
                img_width, img_height = img.size
                max_width = width - 100
                max_height = height - 300
                
                # Escalar imagen manteniendo proporción
                scale = min(max_width / img_width, max_height / img_height)
                final_width = img_width * scale
                final_height = img_height * scale
                
                x_position = (width - final_width) / 2
                y_image_position = 50
                
                c.drawInlineImage(
                    img_buffer, 
                    x_position, 
                    y_image_position, 
                    width=final_width, 
                    height=final_height
                )
                
            except Exception as e:
                # Si falla la imagen, mostrar mensaje de error
                c.setFont("Helvetica-Oblique", 12)
                c.drawString(50, 50, f"Error cargando imagen: {str(e)}")
    
    c.save()
    return output_path
```

### 14. Interfaz de Tabla de Seguimiento

#### Vista de Tabla Completa:
```python
# separador_recibos/views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class TablaRecibosView(LoginRequiredMixin, ListView):
    """Vista para mostrar tabla completa de todos los recibos"""
    model = ReciboDetectado
    template_name = 'separador_recibos/tabla_recibos.html'
    context_object_name = 'recibos'
    paginate_by = 50
    
    def get_queryset(self):
        """Filtrar recibos por usuario"""
        return ReciboDetectado.objects.filter(
            procesamiento__usuario=self.request.user
        ).select_related('procesamiento')
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional"""
        context = super().get_context_data(**kwargs)
        context['total_recibos'] = self.get_queryset().count()
        context['valor_total'] = self.get_queryset().aggregate(
            total=models.Sum('valor')
        )['total'] or 0
        return context
```

#### Template de Tabla (tabla_recibos.html):
```html
<!-- separador_recibos/templates/separador_recibos/tabla_recibos.html -->
{% extends 'separador_recibos/base.html' %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h2>Tabla de Seguimiento de Recibos</h2>
            
            <!-- Estadísticas -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5>Total Recibos</h5>
                            <h3>{{ total_recibos }}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5>Valor Total</h5>
                            <h3>${{ valor_total|floatformat:0 }}</h3>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tabla de recibos -->
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>#</th>
                            <th>Imagen</th>
                            <th>Beneficiario</th>
                            <th>Valor</th>
                            <th>Entidad</th>
                            <th>Cuenta</th>
                            <th>Referencia</th>
                            <th>Fecha</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for recibo in recibos %}
                        <tr>
                            <td>{{ recibo.numero_secuencial }}</td>
                            <td>
                                {% if recibo.imagen_recibo %}
                                <img src="{{ recibo.imagen_recibo.url }}" 
                                     alt="Recibo {{ recibo.numero_secuencial }}"
                                     class="img-thumbnail" 
                                     style="width: 50px; height: auto;">
                                {% else %}
                                <span class="text-muted">Sin imagen</span>
                                {% endif %}
                            </td>
                            <td>{{ recibo.nombre_beneficiario|default:"N/A" }}</td>
                            <td>${{ recibo.valor|floatformat:0|default:"N/A" }}</td>
                            <td>{{ recibo.entidad_bancaria|default:"N/A" }}</td>
                            <td>{{ recibo.numero_cuenta|default:"N/A" }}</td>
                            <td>{{ recibo.referencia|default:"N/A" }}</td>
                            <td>{{ recibo.fecha_aplicacion|default:"N/A" }}</td>
                            <td>
                                <span class="badge bg-success">{{ recibo.estado_pago|default:"N/A" }}</span>
                            </td>
                            <td>
                                <a href="{% url 'ver_recibo' recibo.id %}" 
                                   class="btn btn-sm btn-info">Ver</a>
                                <a href="{% url 'descargar_imagen' recibo.id %}" 
                                   class="btn btn-sm btn-secondary">Imagen</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Paginación -->
            {% if is_paginated %}
            <nav aria-label="Navegación de páginas">
                <ul class="pagination justify-content-center">
                    {% if page_obj.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page=1">Primera</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Anterior</a>
                    </li>
                    {% endif %}
                    
                    <li class="page-item active">
                        <span class="page-link">
                            Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}
                        </span>
                    </li>
                    
                    {% if page_obj.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">Siguiente</a>
                    </li>
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">Última</a>
                    </li>
                    {% endif %}
                </ul>
            </nav>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

#### URLs para la Tabla:
```python
# separador_recibos/urls.py (actualizado)
urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('tabla/', views.TablaRecibosView.as_view(), name='tabla_recibos'),
    path('procesando/<uuid:procesamiento_id>/', views.process_status, name='process_status'),
    path('resultados/<uuid:procesamiento_id>/', views.results, name='results'),
    path('descargar/<uuid:procesamiento_id>/', views.download_result, name='download_result'),
    path('recibo/<uuid:recibo_id>/', views.ver_recibo, name='ver_recibo'),
    path('imagen/<uuid:recibo_id>/', views.descargar_imagen, name='descargar_imagen'),
]
```

#### Funcionalidades Adicionales de la Tabla:
1. **Filtros avanzados** por fecha, entidad, valor
2. **Exportación a Excel/CSV** de todos los datos
3. **Búsqueda por beneficiario** o referencia
4. **Validación manual** de recibos incorrectos
5. **Edición de datos** extraídos incorrectamente
6. **Dashboard con gráficos** de distribución por entidad
7. **Alertas** para valores elevados o patrones inusuales

Esta arquitectura actualizada proporciona:
- ✅ **Captura visual** de cada recibo como imagen
- ✅ **PDF separado** con cada recibo en su propia página  
- ✅ **Tabla completa** con todos los datos para seguimiento
- ✅ **Funcionalidades avanzadas** de gestión y análisis