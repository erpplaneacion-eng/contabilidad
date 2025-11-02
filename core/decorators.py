"""
Decoradores personalizados para control de acceso basado en roles.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles requeridos.

    Args:
        roles: Lista de roles permitidos (ej: ['ADMIN', 'CONTADOR'])

    Usage:
        @role_required(['ADMIN', 'CONTADOR'])
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Si el usuario no tiene perfil, denegar acceso
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied("No tienes un perfil asignado")

            # Verificar si el rol del usuario está en los roles permitidos
            if request.user.profile.rol not in roles:
                raise PermissionDenied("No tienes permisos para acceder a esta página")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def area_required(area):
    """
    Decorador que verifica si el usuario tiene acceso a un área específica.

    Args:
        area: Área requerida (ej: 'PROVEEDORES', 'SEPARADOR')

    Usage:
        @area_required('PROVEEDORES')
        def lista_proveedores(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Si el usuario no tiene perfil, denegar acceso
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied("No tienes un perfil asignado")

            # Si el usuario tiene acceso a AMBAS áreas, permitir acceso
            if request.user.profile.area == 'AMBAS':
                return view_func(request, *args, **kwargs)

            # Verificar si el área del usuario coincide con el área requerida
            if request.user.profile.area != area:
                raise PermissionDenied(f"No tienes acceso al área de {area}")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
