#!/usr/bin/env python
"""
Script de diagnóstico para verificar configuración de email.
Ejecutar: python test_email_config.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

def test_email_config():
    """Verifica la configuración de email"""
    print("\n" + "="*60)
    print("DIAGNÓSTICO DE CONFIGURACIÓN DE EMAIL")
    print("="*60 + "\n")

    # 1. Verificar variables de entorno
    print("1. Variables de entorno configuradas:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {'✓ Configurado' if settings.EMAIL_HOST_USER else '✗ NO CONFIGURADO'}")
    if settings.EMAIL_HOST_USER:
        print(f"                     ({settings.EMAIL_HOST_USER})")
    print(f"   EMAIL_HOST_PASSWORD: {'✓ Configurado' if settings.EMAIL_HOST_PASSWORD else '✗ NO CONFIGURADO'}")
    if settings.EMAIL_HOST_PASSWORD:
        print(f"                         (***{settings.EMAIL_HOST_PASSWORD[-4:]})")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   NOTIFICATION_EMAIL: {settings.NOTIFICATION_EMAIL}")
    print()

    # 2. Verificar si la configuración es válida
    print("2. Estado de la configuración:")
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("   ✗ CONFIGURACIÓN INCOMPLETA")
        print("   ERROR: Faltan credenciales de Gmail")
        print()
        print("   SOLUCIÓN:")
        print("   En Railway, agrega estas variables de entorno:")
        print(f"   - EMAIL_HOST_USER=erp.planeacion@vallesolidario.com")
        print(f"   - EMAIL_HOST_PASSWORD=nyczispxalvsymco")
        print(f"   - DEFAULT_FROM_EMAIL=erp.planeacion@vallesolidario.com")
        print(f"   - NOTIFICATION_EMAIL=recepcionfacturaschvs@gmail.com")
        return False
    else:
        print("   ✓ Configuración completa")
        print()

    # 3. Intentar enviar correo de prueba
    print("3. Prueba de envío de correo:")
    respuesta = input("   ¿Deseas enviar un correo de prueba? (s/n): ").lower()

    if respuesta == 's':
        print("   Enviando correo de prueba...")
        try:
            resultado = send_mail(
                subject='🧪 Prueba de Configuración de Email - Sistema Contabilidad CHVS',
                message='Este es un correo de prueba para verificar que la configuración de Gmail funciona correctamente.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFICATION_EMAIL],
                fail_silently=False,
            )

            if resultado > 0:
                print("   ✓ CORREO ENVIADO EXITOSAMENTE")
                print(f"   Se envió a: {settings.NOTIFICATION_EMAIL}")
                return True
            else:
                print("   ✗ No se pudo enviar el correo")
                print("   send_mail() retornó 0")
                return False

        except Exception as e:
            print(f"   ✗ ERROR al enviar correo:")
            print(f"   {type(e).__name__}: {str(e)}")
            print()
            print("   POSIBLES CAUSAS:")
            print("   1. Password de aplicación de Gmail incorrecto")
            print("   2. Verificación en dos pasos no activada en Gmail")
            print("   3. El email remitente no tiene permisos")
            print("   4. Firewall bloqueando el puerto 587")
            return False
    else:
        print("   Prueba cancelada por el usuario")
        return None

    print("\n" + "="*60)


if __name__ == '__main__':
    test_email_config()
