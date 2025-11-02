from django import forms
from django.core.validators import FileExtensionValidator
from .models import ProcesamientoRecibo, ReciboDetectado


class PDFUploadForm(forms.ModelForm):
    """Formulario para subir archivos PDF"""
    
    class Meta:
        model = ProcesamientoRecibo
        fields = ['archivo_original']
        widgets = {
            'archivo_original': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf',
                'id': 'pdfFileInput'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivo_original'].label = 'Archivo PDF'
        self.fields['archivo_original'].help_text = 'Selecciona un archivo PDF que contenga múltiples recibos'
    
    def clean_archivo_original(self):
        """Validación personalizada del archivo"""
        archivo = self.cleaned_data.get('archivo_original')
        
        if not archivo:
            raise forms.ValidationError('Debe seleccionar un archivo')
        
        # Validar extensión
        if not archivo.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Solo se permiten archivos PDF')
        
        # Validar tamaño (máximo 50MB)
        if archivo.size > 50 * 1024 * 1024:  # 50MB
            raise forms.ValidationError('El archivo es demasiado grande. Máximo 50MB')
        
        # Validar tipo de contenido
        if archivo.content_type not in ['application/pdf']:
            raise forms.ValidationError('El archivo debe ser un PDF válido')
        
        return archivo


class FiltrosRecibosForm(forms.Form):
    """Formulario para filtrar recibos en la tabla"""
    
    beneficiario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por beneficiario...'
        })
    )
    
    entidad = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas las entidades'),
            ('BANCOLOMBIA', 'BANCOLOMBIA'),
            ('BANCO CAJA SOCIAL', 'BANCO CAJA SOCIAL'),
            ('NEQUI', 'NEQUI'),
            ('DAVIPLATA', 'DAVIPLATA'),
            ('BANCO DE BOGOTA', 'BANCO DE BOGOTA'),
            ('BANCO FALABELLA', 'BANCO FALABELLA'),
            ('BANCO BBVA', 'BANCO BBVA'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    valor_minimo = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Valor mínimo'
        })
    )
    
    valor_maximo = forms.DecimalField(
        required=False,
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Valor máximo'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos los estados'),
            ('validado', 'Validado'),
            ('no_validado', 'No Validado'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    orden_por = forms.ChoiceField(
        required=False,
        choices=[
            ('numero_secuencial', 'Número de recibo'),
            ('nombre_beneficiario', 'Beneficiario'),
            ('valor', 'Valor'),
            ('fecha_aplicacion', 'Fecha'),
            ('fecha_deteccion', 'Fecha de detección'),
        ],
        initial='numero_secuencial',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    direccion = forms.ChoiceField(
        required=False,
        choices=[
            ('asc', 'Ascendente'),
            ('desc', 'Descendente'),
        ],
        initial='asc',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class EditarReciboForm(forms.ModelForm):
    """Formulario para editar información de un recibo detectado"""

    class Meta:
        model = ReciboDetectado
        fields = [
            'nombre_beneficiario', 'valor', 'entidad_bancaria', 
            'numero_cuenta', 'referencia', 'fecha_aplicacion',
            'concepto', 'estado_pago', 'validado'
        ]
        widgets = {
            'nombre_beneficiario': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'entidad_bancaria': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'numero_cuenta': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fecha_aplicacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'concepto': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'estado_pago': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'validado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_valor(self):
        """Validación del valor"""
        valor = self.cleaned_data.get('valor')
        if valor and valor <= 0:
            raise forms.ValidationError('El valor debe ser mayor a cero')
        return valor


class ConfiguracionProcesamientoForm(forms.Form):
    """Formulario para configurar el procesamiento de PDF"""
    
    extraer_imagenes = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Extraer imágenes de alta calidad de cada recibo'
    )
    
    calidad_imagen = forms.ChoiceField(
        required=False,
        choices=[
            ('baja', 'Baja (rápido)'),
            ('media', 'Media'),
            ('alta', 'Alta (lento)'),
        ],
        initial='media',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tamaño_imagen = forms.ChoiceField(
        required=False,
        choices=[
            ('pequeña', 'Pequeña (300x400)'),
            ('mediana', 'Mediana (600x800)'),
            ('grande', 'Grande (900x1200)'),
        ],
        initial='mediana',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    generar_reporte = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Generar reporte con estadísticas'
    )
    
    formato_salida = forms.ChoiceField(
        required=False,
        choices=[
            ('pdf_imagenes', 'PDF con imágenes'),
            ('pdf_texto', 'PDF solo texto'),
            ('ambos', 'Ambos formatos'),
        ],
        initial='pdf_imagenes',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )