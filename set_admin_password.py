#!/usr/bin/env python
"""Script para establecer la contraseña del superusuario admin"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')  # Contraseña por defecto
    user.save()
    print("Contraseña del superusuario 'admin' actualizada exitosamente.")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("\nIMPORTANTE: Cambie esta contraseña después del primer inicio de sesión.")
except User.DoesNotExist:
    print("El usuario 'admin' no existe.")
