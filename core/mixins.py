"""
Mixins reutilizables para vistas basadas en clases.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin que verifica si el usuario tiene uno de los roles requeridos.

    Usage:
        class MiVista(RoleRequiredMixin, ListView):
            required_roles = ['ADMIN', 'CONTADOR']
            ...
    """
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        # Verificar login primero
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Si el usuario no tiene perfil, denegar acceso
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes un perfil asignado")

        # Verificar si el rol del usuario está en los roles requeridos
        if self.required_roles and request.user.profile.rol not in self.required_roles:
            raise PermissionDenied("No tienes permisos para acceder a esta página")

        return super().dispatch(request, *args, **kwargs)


class AreaRequiredMixin(LoginRequiredMixin):
    """
    Mixin que verifica si el usuario tiene acceso a un área específica.

    Usage:
        class ListaProveedores(AreaRequiredMixin, ListView):
            required_area = 'PROVEEDORES'
            ...
    """
    required_area = None

    def dispatch(self, request, *args, **kwargs):
        # Verificar login primero
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Si el usuario no tiene perfil, denegar acceso
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No tienes un perfil asignado")

        # Si el usuario tiene acceso a AMBAS áreas, permitir acceso
        if request.user.profile.area == 'AMBAS':
            return super().dispatch(request, *args, **kwargs)

        # Verificar si el área del usuario coincide con el área requerida
        if self.required_area and request.user.profile.area != self.required_area:
            raise PermissionDenied(f"No tienes acceso al área de {self.required_area}")

        return super().dispatch(request, *args, **kwargs)
