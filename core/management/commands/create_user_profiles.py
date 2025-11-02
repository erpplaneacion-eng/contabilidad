"""
Comando de management para crear perfiles de usuario para usuarios existentes.

Uso:
    python manage.py create_user_profiles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Crea perfiles de usuario para todos los usuarios que no tienen perfil'

    def handle(self, *args, **options):
        users_without_profile = []
        users_with_profile = []

        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                # Crear perfil para este usuario
                UserProfile.objects.create(
                    user=user,
                    rol=UserProfile.ROL_ADMIN if user.is_superuser else UserProfile.ROL_OPERADOR,
                    area=UserProfile.AREA_AMBAS
                )
                users_without_profile.append(user.username)
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Perfil creado para usuario: {user.username}')
                )
            else:
                users_with_profile.append(user.username)
                self.stdout.write(
                    self.style.WARNING(f'[INFO] Usuario ya tiene perfil: {user.username}')
                )

        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'\nPerfiles creados: {len(users_without_profile)}'))
        if users_without_profile:
            for username in users_without_profile:
                self.stdout.write(f'  - {username}')

        self.stdout.write(self.style.WARNING(f'\nPerfiles existentes: {len(users_with_profile)}'))
        if users_with_profile:
            for username in users_with_profile:
                self.stdout.write(f'  - {username}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('\n[OK] Comando ejecutado exitosamente\n')
        )
