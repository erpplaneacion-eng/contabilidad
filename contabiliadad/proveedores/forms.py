from django import forms
from django.forms import inlineformset_factory
from .models import Proveedor, Contacto, Impuesto, DocumentoRequerido


class ProveedorForm(forms.ModelForm):
    """Formulario para el modelo Proveedor"""

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
            'fecha_diligenciamiento': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'nombre_razon_social': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el nombre o razón social'
                }
            ),
            'naturaleza_juridica': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'tipo_identificacion': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'numero_identificacion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el número de identificación'
                }
            ),
            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la dirección'
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el teléfono'
                }
            ),
            'celular': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el celular'
                }
            ),
            'pais': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'value': 'Colombia'
                }
            ),
            'departamento': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese el departamento'
                }
            ),
            'ciudad': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la ciudad'
                }
            ),
            'condicion_pago': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'condicion_pago_otro': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Especifique otra condición de pago'
                }
            ),
            'datos_representante_legal': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nombre completo del representante legal'
                }
            ),
            'firma_representante': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
            'sello': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                }
            ),
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


class ImpuestoForm(forms.ModelForm):
    """Formulario para el modelo Impuesto"""

    class Meta:
        model = Impuesto
        fields = [
            'tipo_impuesto',
            'aplica',
            'porcentaje',
            'codigo_actividad_economica',
            'tarifa',
            'municipio',
            'resolucion_exento',
            'otro_concepto',
        ]
        widgets = {
            'tipo_impuesto': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'aplica': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
            'porcentaje': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'step': '0.01',
                    'min': '0',
                    'max': '100'
                }
            ),
            'codigo_actividad_economica': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Código CIIU'
                }
            ),
            'tarifa': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'step': '0.01',
                    'min': '0',
                    'max': '100'
                }
            ),
            'municipio': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Municipio'
                }
            ),
            'resolucion_exento': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Número y fecha de resolución (si aplica)'
                }
            ),
            'otro_concepto': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Especificar otro concepto (si aplica)'
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


# Formsets para contactos e impuestos
ContactoFormSet = inlineformset_factory(
    Proveedor,
    Contacto,
    form=ContactoForm,
    extra=2,  # Número de formularios vacíos a mostrar
    can_delete=True,
    max_num=5,  # Máximo de contactos permitidos
)

ImpuestoFormSet = inlineformset_factory(
    Proveedor,
    Impuesto,
    form=ImpuestoForm,
    extra=4,  # Uno para cada tipo de impuesto
    can_delete=True,
    max_num=10,
)
