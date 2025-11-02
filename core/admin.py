"""
Configuración del admin de Django para la app core.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline para mostrar el perfil de usuario dentro del admin de User.
    """
    model = UserProfile
    can_delete = False
    verbose_name = 'Perfil'
    verbose_name_plural = 'Perfil'
    fields = ('rol', 'area', 'telefono', 'departamento')


class UserAdmin(BaseUserAdmin):
    """
    Extiende el admin de User para incluir el perfil.
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'get_area', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__rol', 'profile__area')

    def get_rol(self, obj):
        """Muestra el rol del usuario."""
        if hasattr(obj, 'profile'):
            return obj.profile.get_rol_display()
        return '-'
    get_rol.short_description = 'Rol'

    def get_area(self, obj):
        """Muestra el área del usuario."""
        if hasattr(obj, 'profile'):
            return obj.profile.get_area_display()
        return '-'
    get_area.short_description = 'Área'


# Desregistrar el User admin original y registrar el nuevo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin para gestionar perfiles de usuario directamente.
    """
    list_display = ('user', 'rol', 'area', 'telefono', 'fecha_creacion')
    list_filter = ('rol', 'area', 'fecha_creacion')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'telefono')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Permisos y Accesos', {
            'fields': ('rol', 'area')
        }),
        ('Información Adicional', {
            'fields': ('telefono', 'departamento')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
