from django import forms
from django.forms import inlineformset_factory
from .models import Proveedor, Contacto, Impuesto, DocumentoRequerido
from core.models import Departamento, Municipio


class ProveedorForm(forms.ModelForm):
    """Formulario para el modelo Proveedor"""
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        label="Departamento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ciudad = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),  # Se llena con JS
        label="Ciudad/Municipio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Proveedor
        fields = [
            'fecha_diligenciamiento',
            'nombre_razon_social',
            'naturaleza_juridica',
            'tipo_identificacion',
            'numero_identificacion',
            'direccion',
            'telefono',
            'celular',
            'pais',
            'departamento',
            'ciudad',
            'condicion_pago',
            'condicion_pago_otro',
            'datos_representante_legal',
            'firma_representante',
            'sello',
        ]
        widgets = {
            'fecha_diligenciamiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre_razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre o razón social'}),
            'naturaleza_juridica': forms.Select(attrs={'class': 'form-select'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-select'}),
            'numero_identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de identificación'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el celular'}),
            'pais': forms.TextInput(attrs={'class': 'form-control', 'value': 'Colombia'}),
            'condicion_pago': forms.Select(attrs={'class': 'form-select'}),
            'condicion_pago_otro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifique otra condición de pago'}),
            'datos_representante_legal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del representante legal'}),
            'firma_representante': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'sello': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }



class ContactoForm(forms.ModelForm):
    """Formulario para el modelo Contacto"""

    class Meta:
        model = Contacto
        fields = [
            'nombre_apellidos',
            'cargo',
            'direccion',
            'correo_electronico',
            'ciudad',
            'telefono',
            'celular',
        ]
        widgets = {
            'nombre_apellidos': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre y apellidos'
                }
            ),
            'cargo': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cargo'
                }
            ),
            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Dirección'
                }
            ),
            'correo_electronico': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com'
                }
            ),
            'ciudad': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ciudad'
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Teléfono'
                }
            ),
            'celular': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Celular'
                }
            ),
        }


class DocumentoRequeridoForm(forms.ModelForm):
    """Formulario para el modelo DocumentoRequerido"""

    class Meta:
        model = DocumentoRequerido
        fields = [
            'fotocopia_rut',
            'solicitud_vinculacion',
            'certificado_camara_comercio',
            'certificacion_bancaria',
            'fotocopia_cc_representante',
            'autorizacion_datos',
        ]
        widgets = {
            'fotocopia_rut': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
            'solicitud_vinculacion': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
            'certificado_camara_comercio': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
            'certificacion_bancaria': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
            'fotocopia_cc_representante': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
            'autorizacion_datos': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'application/pdf,image/*'
                }
            ),
        }


# Formsets para contactos
ContactoFormSet = inlineformset_factory(
    Proveedor,
    Contacto,
    form=ContactoForm,
    extra=2,  # Número de formularios vacíos a mostrar
    can_delete=True,
    max_num=5,  # Máximo de contactos permitidos
)


class ImpuestosProveedorForm(forms.Form):
    """Formulario para la nueva tabla de impuestos del proveedor."""

    # Campos para la resolución de exento
    resolucion_exento_numero = forms.CharField(label="Número de Resolución", required=False)
    resolucion_exento_fecha = forms.DateField(label="Fecha de Resolución", required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        proveedor = kwargs.pop('proveedor', None)
        super().__init__(*args, **kwargs)

        # Crear campos dinámicamente para cada tipo de impuesto
        for key, label in Impuesto.TIPO_IMPUESTO_CHOICES:
            self.fields[f'aplica_{key}'] = forms.BooleanField(required=False, label=label)

            if key == 'ICA':
                self.fields[f'codigo_ciiu_{key}'] = forms.CharField(required=False, label="Código CIIU")
                self.fields[f'tarifa_{key}'] = forms.DecimalField(required=False, label="Tarifa (por mil)")
                self.fields[f'municipio_{key}'] = forms.CharField(required=False, label="Municipio")
            elif key == 'OTRO':
                self.fields[f'porcentaje_{key}'] = forms.DecimalField(required=False, label="Porcentaje")
                self.fields[f'otro_concepto_{key}'] = forms.CharField(required=False, label="¿Cuál?")
            else:
                self.fields[f'porcentaje_{key}'] = forms.DecimalField(required=False, label="Porcentaje")

        # Si es una actualización, poblar el formulario con datos existentes
        if proveedor:
            impuestos_existentes = {imp.tipo_impuesto: imp for imp in proveedor.impuestos.all()}
            for key, label in Impuesto.TIPO_IMPUESTO_CHOICES:
                if key in impuestos_existentes:
                    impuesto = impuestos_existentes[key]
                    self.initial[f'aplica_{key}'] = impuesto.aplica
                    if key == 'ICA':
                        self.initial[f'codigo_ciiu_{key}'] = impuesto.codigo_actividad_economica
                        self.initial[f'tarifa_{key}'] = impuesto.tarifa
                        self.initial[f'municipio_{key}'] = impuesto.municipio
                    elif key == 'OTRO':
                        self.initial[f'porcentaje_{key}'] = impuesto.porcentaje
                        self.initial[f'otro_concepto_{key}'] = impuesto.otro_concepto
                    else:
                        self.initial[f'porcentaje_{key}'] = impuesto.porcentaje

                    # Poblar datos de resolución (asumiendo que puede estar en cualquiera)
                    if impuesto.resolucion_exento:
                        try:
                            numero, fecha = impuesto.resolucion_exento.split(' del ')
                            self.initial['resolucion_exento_numero'] = numero
                            self.initial['resolucion_exento_fecha'] = fecha
                        except (ValueError, IndexError):
                            self.initial['resolucion_exento_numero'] = impuesto.resolucion_exento

    def save(self, proveedor):
        """Guarda los datos de impuestos para un proveedor."""
        resolucion_str = ""
        if self.cleaned_data.get('resolucion_exento_numero') and self.cleaned_data.get('resolucion_exento_fecha'):
            numero = self.cleaned_data['resolucion_exento_numero']
            fecha = self.cleaned_data['resolucion_exento_fecha'].strftime('%Y-%m-%d')
            resolucion_str = f"{numero} del {fecha}"

        for key, label in Impuesto.TIPO_IMPUESTO_CHOICES:
            aplica = self.cleaned_data.get(f'aplica_{key}')

            if aplica:
                defaults = {
                    'aplica': True,
                    'resolucion_exento': resolucion_str
                }
                if key == 'ICA':
                    defaults['codigo_actividad_economica'] = self.cleaned_data.get(f'codigo_ciiu_{key}')
                    defaults['tarifa'] = self.cleaned_data.get(f'tarifa_{key}')
                    defaults['municipio'] = self.cleaned_data.get(f'municipio_{key}')
                    defaults['porcentaje'] = None # ICA no usa porcentaje
                elif key == 'OTRO':
                    defaults['porcentaje'] = self.cleaned_data.get(f'porcentaje_{key}')
                    defaults['otro_concepto'] = self.cleaned_data.get(f'otro_concepto_{key}')
                else:
                    defaults['porcentaje'] = self.cleaned_data.get(f'porcentaje_{key}')

                Impuesto.objects.update_or_create(
                    proveedor=proveedor,
                    tipo_impuesto=key,
                    defaults=defaults
                )
            else:
                # Si no aplica, borrar el registro existente
                Impuesto.objects.filter(proveedor=proveedor, tipo_impuesto=key).delete()
