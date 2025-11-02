from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Proveedor, Contacto, Impuesto, DocumentoRequerido
from .forms import (
    ProveedorForm,
    ContactoFormSet,
    ImpuestoFormSet,
    DocumentoRequeridoForm
)


def proveedor_form_view(request):
    """Vista para crear un nuevo proveedor con sus contactos, impuestos y documentos"""

    if request.method == 'POST':
        proveedor_form = ProveedorForm(request.POST, request.FILES)
        documento_form = DocumentoRequeridoForm(request.POST, request.FILES)

        if proveedor_form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar el proveedor
                    proveedor = proveedor_form.save()

                    # Guardar contactos
                    contacto_formset = ContactoFormSet(request.POST, instance=proveedor)
                    if contacto_formset.is_valid():
                        contacto_formset.save()

                    # Guardar impuestos
                    impuesto_formset = ImpuestoFormSet(request.POST, instance=proveedor)
                    if impuesto_formset.is_valid():
                        impuesto_formset.save()

                    # Guardar documentos
                    if documento_form.is_valid():
                        documento = documento_form.save(commit=False)
                        documento.proveedor = proveedor
                        documento.save()

                    messages.success(
                        request,
                        f'¡Registro exitoso! El proveedor {proveedor.nombre_razon_social} ha sido registrado correctamente.'
                    )
                    return redirect('proveedores:success', pk=proveedor.pk)

            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        proveedor_form = ProveedorForm()
        contacto_formset = ContactoFormSet()
        impuesto_formset = ImpuestoFormSet()
        documento_form = DocumentoRequeridoForm()

    context = {
        'proveedor_form': proveedor_form,
        'contacto_formset': ContactoFormSet(request.POST or None),
        'impuesto_formset': ImpuestoFormSet(request.POST or None),
        'documento_form': documento_form,
    }

    return render(request, 'proveedores/formulario_proveedor.html', context)


@login_required
def proveedor_update_view(request, pk):
    """Vista para actualizar un proveedor existente (requiere autenticación)"""

    proveedor = get_object_or_404(Proveedor, pk=pk)

    if request.method == 'POST':
        proveedor_form = ProveedorForm(request.POST, request.FILES, instance=proveedor)

        if proveedor_form.is_valid():
            try:
                with transaction.atomic():
                    proveedor = proveedor_form.save()

                    # Actualizar contactos
                    contacto_formset = ContactoFormSet(request.POST, instance=proveedor)
                    if contacto_formset.is_valid():
                        contacto_formset.save()

                    # Actualizar impuestos
                    impuesto_formset = ImpuestoFormSet(request.POST, instance=proveedor)
                    if impuesto_formset.is_valid():
                        impuesto_formset.save()

                    # Actualizar documentos
                    try:
                        documento = DocumentoRequerido.objects.get(proveedor=proveedor)
                        documento_form = DocumentoRequeridoForm(
                            request.POST,
                            request.FILES,
                            instance=documento
                        )
                    except DocumentoRequerido.DoesNotExist:
                        documento_form = DocumentoRequeridoForm(request.POST, request.FILES)

                    if documento_form.is_valid():
                        documento = documento_form.save(commit=False)
                        documento.proveedor = proveedor
                        documento.save()

                    messages.success(
                        request,
                        f'¡Actualización exitosa! Los datos de {proveedor.nombre_razon_social} han sido actualizados.'
                    )
                    return redirect('proveedores:success', pk=proveedor.pk)

            except Exception as e:
                messages.error(request, f'Error al actualizar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        proveedor_form = ProveedorForm(instance=proveedor)
        contacto_formset = ContactoFormSet(instance=proveedor)
        impuesto_formset = ImpuestoFormSet(instance=proveedor)

        try:
            documento = DocumentoRequerido.objects.get(proveedor=proveedor)
            documento_form = DocumentoRequeridoForm(instance=documento)
        except DocumentoRequerido.DoesNotExist:
            documento_form = DocumentoRequeridoForm()

    context = {
        'proveedor_form': proveedor_form,
        'contacto_formset': contacto_formset,
        'impuesto_formset': impuesto_formset,
        'documento_form': documento_form,
        'proveedor': proveedor,
        'is_update': True,
    }

    return render(request, 'proveedores/formulario_proveedor.html', context)


def success_view(request, pk):
    """Vista de éxito después de registrar/actualizar un proveedor"""

    proveedor = get_object_or_404(Proveedor, pk=pk)

    context = {
        'proveedor': proveedor,
    }

    return render(request, 'proveedores/success.html', context)


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
        # Estadísticas por naturaleza jurídica
        context['total_juridica'] = Proveedor.objects.filter(naturaleza_juridica='JURIDICA').count()
        context['total_natural'] = Proveedor.objects.filter(naturaleza_juridica='NATURAL').count()
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

    # Verificar permisos
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

    # Si no es POST, redirigir a la lista
    return redirect('proveedores:lista')
