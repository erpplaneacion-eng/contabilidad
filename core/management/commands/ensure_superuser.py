"""
Comando para crear superusuario automáticamente si no existe
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config


class Command(BaseCommand):
    help = 'Crea un superusuario si no existe'

    def handle(self, *args, **options):
        User = get_user_model()

        # Obtener credenciales desde variables de entorno
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@contabilidad.com')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='')

        if not password:
            self.stdout.write(
                self.style.WARNING('No se proporcionó DJANGO_SUPERUSER_PASSWORD. No se creará el superusuario.')
            )
            return

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'El superusuario "{username}" ya existe.')
            )
            return

        # Crear superusuario
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear superusuario: {str(e)}')
            )
