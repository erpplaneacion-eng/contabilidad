"""
Modelos del núcleo del sistema - Perfiles de usuario y configuración.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Perfil extendido de usuario con roles y áreas de acceso.

    Se crea automáticamente cuando se crea un usuario.
    """

    # Opciones de roles
    ROL_ADMIN = 'ADMIN'
    ROL_CONTADOR = 'CONTADOR'
    ROL_OPERADOR = 'OPERADOR'

    ROLES_CHOICES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_CONTADOR, 'Contador'),
        (ROL_OPERADOR, 'Operador'),
    ]

    # Opciones de áreas
    AREA_PROVEEDORES = 'PROVEEDORES'
    AREA_SEPARADOR = 'SEPARADOR'
    AREA_AMBAS = 'AMBAS'

    AREA_CHOICES = [
        (AREA_PROVEEDORES, 'Gestión de Proveedores'),
        (AREA_SEPARADOR, 'Procesamiento de Recibos'),
        (AREA_AMBAS, 'Ambas Áreas'),
    ]

    # Relación uno a uno con el modelo User de Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )

    # Campos de perfil
    rol = models.CharField(
        max_length=20,
        choices=ROLES_CHOICES,
        default=ROL_OPERADOR,
        verbose_name='Rol'
    )

    area = models.CharField(
        max_length=20,
        choices=AREA_CHOICES,
        default=AREA_AMBAS,
        verbose_name='Área de acceso'
    )

    # Campos adicionales opcionales
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )

    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
    )

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()} ({self.get_area_display()})"

    def tiene_acceso_proveedores(self):
        """Verifica si el usuario tiene acceso al área de proveedores."""
        return self.area in [self.AREA_PROVEEDORES, self.AREA_AMBAS]

    def tiene_acceso_separador(self):
        """Verifica si el usuario tiene acceso al área de separador de recibos."""
        return self.area in [self.AREA_SEPARADOR, self.AREA_AMBAS]

    def es_admin(self):
        """Verifica si el usuario es administrador."""
        return self.rol == self.ROL_ADMIN


# Signals para crear automáticamente el perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un nuevo usuario.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Departamento(models.Model):
    """Modelo para los departamentos de un país."""
    codigo_departamento = models.CharField(max_length=10, primary_key=True, verbose_name='Código del Departamento')
    nombre_departamento = models.CharField(max_length=100, verbose_name='Nombre del Departamento')

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre_departamento']

    def __str__(self):
        return self.nombre_departamento


class Municipio(models.Model):
    """Modelo para los municipios de un departamento."""
    codigo_municipio = models.CharField(max_length=10, unique=True, verbose_name='Código del Municipio')
    nombre_municipio = models.CharField(max_length=100, verbose_name='Nombre del Municipio')
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.CASCADE, 
        related_name='municipios',
        verbose_name='Departamento'
    )

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['departamento', 'nombre_municipio']

    def __str__(self):
        return f"{self.nombre_municipio} ({self.departamento.nombre_departamento})"

