from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
import base64
import re
import threading
import logging

from .models import Proveedor, Contacto, Impuesto, DocumentoRequerido
from .forms import (
    ProveedorForm,
    ContactoFormSet,
    ImpuestosProveedorForm,
    DocumentoRequeridoForm
)
from core.utils import notificar_nuevo_proveedor

logger = logging.getLogger(__name__)


def enviar_notificacion_async(proveedor_id, url_proveedor):
    """
    Envía la notificación de nuevo proveedor en un hilo separado.
    Esto evita que el timeout de Gunicorn afecte la respuesta al usuario.
    """
    try:
        # Obtener el proveedor desde la BD (en el hilo separado)
        proveedor = Proveedor.objects.get(pk=proveedor_id)

        # Enviar notificación por correo
        notificar_nuevo_proveedor(
            proveedor=proveedor,
            contactos=proveedor.contactos.all(),
            impuestos=proveedor.impuestos.all(),
            url_sistema=url_proveedor
        )
        logger.info(f'Notificación enviada exitosamente para proveedor {proveedor_id}')
    except Exception as e:
        # Si falla el correo, solo registrar el error
        logger.error(f'Error al enviar notificación de nuevo proveedor {proveedor_id}: {str(e)}')


def base64_to_file(data_url):
    """Convierte una URL de datos base64 en un ContentFile de Django."""
    if not data_url or ';base64,' not in data_url:
        return None
    try:
        format, imgstr = data_url.split(';base64,')
        ext = format.split('/')[-1]
        data = base64.b64decode(imgstr)
        return ContentFile(data, name=f'signature.{ext}')
    except (ValueError, TypeError, base64.binascii.Error):
        return None

def proveedor_form_view(request):
    """Vista para crear un nuevo proveedor con sus contactos, impuestos y documentos"""
    if request.method == 'POST':
        post_data = request.POST.copy()
        files_data = request.FILES.copy()

        # Procesar firmas base64
        firma_rep_base64 = post_data.get('firma_representante_base64')
        if firma_rep_base64:
            firma_file = base64_to_file(firma_rep_base64)
            if firma_file:
                files_data['firma_representante'] = firma_file

        auth_datos_base64 = post_data.get('autorizacion_datos_base64')
        if auth_datos_base64:
            auth_file = base64_to_file(auth_datos_base64)
            if auth_file:
                files_data['autorizacion_datos'] = auth_file

        proveedor_form = ProveedorForm(post_data, files_data)
        documento_form = DocumentoRequeridoForm(post_data, files_data)
        impuestos_form = ImpuestosProveedorForm(post_data)
        contacto_formset = ContactoFormSet(post_data)

        if all([proveedor_form.is_valid(), documento_form.is_valid(), impuestos_form.is_valid(), contacto_formset.is_valid()]):
            try:
                with transaction.atomic():
                    proveedor = proveedor_form.save()
                    contacto_formset.instance = proveedor
                    contacto_formset.save()
                    impuestos_form.save(proveedor)
                    documento = documento_form.save(commit=False)
                    documento.proveedor = proveedor
                    documento.save()

                    # Enviar notificación por correo en un hilo separado (no bloqueante)
                    # Usa Gmail API (rápido, 2-3 segundos) para evitar timeouts
                    try:
                        url_proveedor = request.build_absolute_uri(
                            reverse('proveedores:detalle', args=[proveedor.pk])
                        )
                        # Iniciar thread para enviar correo sin bloquear la respuesta
                        thread = threading.Thread(
                            target=enviar_notificacion_async,
                            args=(proveedor.pk, url_proveedor),
                            daemon=True
                        )
                        thread.start()
                        logger.info(f'Thread de notificación iniciado para proveedor {proveedor.pk} (Gmail API)')
                    except Exception as e:
                        # Si falla al iniciar el thread, solo registrar el error
                        logger.error(f'Error al iniciar thread de notificación: {str(e)}')

                    messages.success(request, f'¡Registro exitoso! El proveedor {proveedor.nombre_razon_social} ha sido registrado.')
                    return redirect('proveedores:success', pk=proveedor.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        proveedor_form = ProveedorForm()
        contacto_formset = ContactoFormSet()
        impuestos_form = ImpuestosProveedorForm()
        documento_form = DocumentoRequeridoForm()

    context = {
        'proveedor_form': proveedor_form,
        'contacto_formset': contacto_formset,
        'impuestos_form': impuestos_form,
        'documento_form': documento_form,
    }
    return render(request, 'proveedores/formulario_proveedor.html', context)

@login_required
def proveedor_update_view(request, pk):
    """Vista para actualizar un proveedor existente (requiere autenticación)"""
    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        post_data = request.POST.copy()
        files_data = request.FILES.copy()

        # Procesar firmas base64
        firma_rep_base64 = post_data.get('firma_representante_base64')
        if firma_rep_base64:
            firma_file = base64_to_file(firma_rep_base64)
            if firma_file:
                files_data['firma_representante'] = firma_file

        auth_datos_base64 = post_data.get('autorizacion_datos_base64')
        if auth_datos_base64:
            auth_file = base64_to_file(auth_datos_base64)
            if auth_file:
                files_data['autorizacion_datos'] = auth_file

        proveedor_form = ProveedorForm(post_data, files_data, instance=proveedor)
        impuestos_form = ImpuestosProveedorForm(post_data, proveedor=proveedor)
        contacto_formset = ContactoFormSet(post_data, instance=proveedor)
        try:
            documento_instance = proveedor.documentos
            documento_form = DocumentoRequeridoForm(post_data, files_data, instance=documento_instance)
        except DocumentoRequerido.DoesNotExist:
            documento_form = DocumentoRequeridoForm(post_data, files_data)

        if all([proveedor_form.is_valid(), impuestos_form.is_valid(), contacto_formset.is_valid(), documento_form.is_valid()]):
            try:
                with transaction.atomic():
                    proveedor = proveedor_form.save()
                    contacto_formset.save()
                    impuestos_form.save(proveedor)
                    documento = documento_form.save(commit=False)
                    documento.proveedor = proveedor
                    documento.save()
                    messages.success(request, f'¡Actualización exitosa! Los datos de {proveedor.nombre_razon_social} han sido actualizados.')
                    return redirect('proveedores:success', pk=proveedor.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        proveedor_form = ProveedorForm(instance=proveedor)
        contacto_formset = ContactoFormSet(instance=proveedor)
        impuestos_form = ImpuestosProveedorForm(proveedor=proveedor)
        try:
            documento_form = DocumentoRequeridoForm(instance=proveedor.documentos)
        except DocumentoRequerido.DoesNotExist:
            documento_form = DocumentoRequeridoForm()

    context = {
        'proveedor_form': proveedor_form,
        'contacto_formset': contacto_formset,
        'impuestos_form': impuestos_form,
        'documento_form': documento_form,
        'proveedor': proveedor,
        'is_update': True,
    }
    return render(request, 'proveedores/formulario_proveedor.html', context)

class ProveedorListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los proveedores (solo para usuarios autenticados)"""

    model = Proveedor
    template_name = 'proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 20
    ordering = ['-fecha_creacion']
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_juridica'] = Proveedor.objects.filter(
            naturaleza_juridica__in=['PERSONA_JURIDICA', 'SOCIEDAD']
        ).count()
        context['total_natural'] = Proveedor.objects.filter(
            naturaleza_juridica='PERSONA_NATURAL'
        ).count()
        return context


class ProveedorDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver el detalle de un proveedor (solo para usuarios autenticados)"""

    model = Proveedor
    template_name = 'proveedores/proveedor_detail.html'
    context_object_name = 'proveedor'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contactos'] = self.object.contactos.all()
        context['impuestos'] = self.object.impuestos.all()
        try:
            context['documentos'] = self.object.documentos
        except DocumentoRequerido.DoesNotExist:
            context['documentos'] = None
        return context


@login_required
def proveedor_delete_view(request, pk):
    """Vista para eliminar un proveedor (requiere autenticación y permisos de admin)"""

    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.rol == 'ADMIN')):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tiene permisos para eliminar proveedores'}, status=403)
        messages.error(request, 'No tiene permisos para eliminar proveedores.')
        return redirect('proveedores:lista')

    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        try:
            nombre = proveedor.nombre_razon_social
            proveedor.delete()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Proveedor "{nombre}" eliminado correctamente'})

            messages.success(request, f'Proveedor "{nombre}" eliminado correctamente.')
            return redirect('proveedores:lista')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

            messages.error(request, f'Error al eliminar el proveedor: {str(e)}')
            return redirect('proveedores:lista')

    return redirect('proveedores:lista')

def success_view(request, pk):
    """Vista de éxito después de registrar/actualizar un proveedor"""

    proveedor = get_object_or_404(Proveedor, pk=pk)

    context = {
        'proveedor': proveedor,
    }

    return render(request, 'proveedores/success.html', context)


