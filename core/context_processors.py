"""
Context processors para agregar variables globales a todos los templates.
"""


def user_info(request):
    """
    Agrega información del usuario autenticado a todos los templates.

    Variables disponibles:
        - user_profile: Perfil del usuario (si existe)
        - user_rol: Rol del usuario (si tiene perfil)
        - user_area: Área del usuario (si tiene perfil)
        - tiene_acceso_proveedores: Boolean
        - tiene_acceso_separador: Boolean
    """
    context = {
        'user_profile': None,
        'user_rol': None,
        'user_area': None,
        'tiene_acceso_proveedores': False,
        'tiene_acceso_separador': False,
    }

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            context['user_profile'] = profile
            context['user_rol'] = profile.rol
            context['user_area'] = profile.area

            # Determinar accesos según el área
            if profile.area == 'AMBAS':
                context['tiene_acceso_proveedores'] = True
                context['tiene_acceso_separador'] = True
            elif profile.area == 'PROVEEDORES':
                context['tiene_acceso_proveedores'] = True
            elif profile.area == 'SEPARADOR':
                context['tiene_acceso_separador'] = True

    return context
