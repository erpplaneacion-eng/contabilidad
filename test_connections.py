# -*- coding: utf-8 -*-
"""
Script de prueba para verificar conexiones de Gmail y Cloudinary
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
import cloudinary.uploader
from io import BytesIO

def test_gmail():
    """Prueba de conexion y envio de email con Gmail"""
    print("\n" + "="*60)
    print("PRUEBA DE GMAIL")
    print("="*60)

    # Verificar configuracion
    print(f"\n[*] Configuracion de Email:")
    print(f"   - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   - EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   - EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   - EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NO CONFIGURADO'}")
    print(f"   - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   - NOTIFICATION_EMAIL: {settings.NOTIFICATION_EMAIL}")

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n[X] ERROR: Credenciales de Gmail no configuradas en .env")
        return False

    print(f"\n[->] Enviando correo de prueba a {settings.NOTIFICATION_EMAIL}...")

    try:
        resultado = send_mail(
            subject='Prueba de Email desde Django CHVS',
            message='Este es un correo de prueba desde el sistema de contabilidad CHVS.\n\nSi recibes este mensaje, la configuracion de Gmail esta funcionando correctamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            fail_silently=False,
        )

        if resultado == 1:
            print("[OK] Email enviado exitosamente!")
            print(f"   Revisa la bandeja de {settings.NOTIFICATION_EMAIL}")
            return True
        else:
            print("[X] No se pudo enviar el email")
            return False

    except Exception as e:
        print(f"[X] ERROR al enviar email: {str(e)}")
        print("\n[i] Posibles soluciones:")
        print("   1. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD esten en .env")
        print("   2. Asegurate de usar una App Password de Gmail, no tu contrasena normal")
        print("   3. Verifica que la verificacion en dos pasos este habilitada en Gmail")
        print("   4. Genera una App Password en: https://myaccount.google.com/apppasswords")
        return False


def test_cloudinary():
    """Prueba de conexion con Cloudinary"""
    print("\n" + "="*60)
    print("PRUEBA DE CLOUDINARY")
    print("="*60)

    # Verificar configuracion
    print(f"\n[*] Configuracion de Cloudinary:")
    print(f"   - CLOUD_NAME: {settings.CLOUDINARY_CLOUD_NAME if settings.CLOUDINARY_CLOUD_NAME else 'NO CONFIGURADO'}")
    print(f"   - API_KEY: {settings.CLOUDINARY_API_KEY if settings.CLOUDINARY_API_KEY else 'NO CONFIGURADO'}")
    print(f"   - API_SECRET: {'*' * 20 if settings.CLOUDINARY_API_SECRET else 'NO CONFIGURADO'}")

    if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
        print("\n[X] ERROR: Credenciales de Cloudinary no configuradas en .env")
        print("\n[i] Pasos para configurar Cloudinary:")
        print("   1. Crea una cuenta en https://cloudinary.com")
        print("   2. Ve a tu dashboard: https://cloudinary.com/console")
        print("   3. Copia Cloud Name, API Key y API Secret")
        print("   4. Agregalos a tu archivo .env")
        return False

    print(f"\n[->] Probando subida de archivo de prueba a Cloudinary...")

    try:
        # Crear un archivo de prueba en memoria
        from PIL import Image

        # Crear una imagen simple de prueba
        img = Image.new('RGB', (100, 100), color='blue')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Subir a Cloudinary
        resultado = cloudinary.uploader.upload(
            img_byte_arr,
            folder="contabilidad",
            public_id="test_image",
            overwrite=True,
            resource_type="image"
        )

        print("[OK] Archivo subido exitosamente a Cloudinary!")
        print(f"\n[*] Detalles de la subida:")
        print(f"   - Public ID: {resultado.get('public_id')}")
        print(f"   - URL: {resultado.get('secure_url')}")
        print(f"   - Formato: {resultado.get('format')}")
        print(f"   - Tamano: {resultado.get('bytes')} bytes")
        print(f"   - Dimensiones: {resultado.get('width')}x{resultado.get('height')}")

        print(f"\n[i] Ver archivo en:")
        print(f"   {resultado.get('secure_url')}")

        # Intentar eliminar el archivo de prueba
        try:
            cloudinary.uploader.destroy(resultado.get('public_id'))
            print(f"\n[i] Archivo de prueba eliminado de Cloudinary")
        except:
            print(f"\n[!] No se pudo eliminar el archivo de prueba (no es critico)")

        return True

    except Exception as e:
        print(f"[X] ERROR al subir archivo a Cloudinary: {str(e)}")
        print("\n[i] Posibles soluciones:")
        print("   1. Verifica que las credenciales en .env sean correctas")
        print("   2. Verifica tu conexion a internet")
        print("   3. Revisa que tu cuenta de Cloudinary este activa")
        return False


def test_database():
    """Verificar conexion de base de datos"""
    print("\n" + "="*60)
    print("VERIFICACION DE BASE DE DATOS")
    print("="*60)

    db_config = settings.DATABASES['default']
    print(f"\n[*] Base de datos actual:")
    print(f"   - Engine: {db_config['ENGINE']}")

    if 'sqlite3' in db_config['ENGINE']:
        print(f"   - Archivo: {db_config['NAME']}")
        print(f"   - Modo: DESARROLLO (SQLite)")
    else:
        print(f"   - Host: {db_config.get('HOST', 'N/A')}")
        print(f"   - Puerto: {db_config.get('PORT', 'N/A')}")
        print(f"   - Nombre: {db_config.get('NAME', 'N/A')}")
        print(f"   - Modo: PRODUCCION (PostgreSQL)")

    # Intentar hacer una consulta simple
    try:
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print(f"\n[OK] Conexion exitosa a la base de datos")
        print(f"   - Usuarios registrados: {user_count}")
        return True
    except Exception as e:
        print(f"\n[X] ERROR al conectar con la base de datos: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRUEBA DE CONEXIONES - SISTEMA CHVS")
    print("=" * 60)

    # Probar base de datos
    db_ok = test_database()

    # Probar Gmail
    gmail_ok = test_gmail()

    # Probar Cloudinary
    cloudinary_ok = test_cloudinary()

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"\n{'[OK]' if db_ok else '[X]'} Base de datos: {'OK' if db_ok else 'FALLO'}")
    print(f"{'[OK]' if gmail_ok else '[X]'} Gmail: {'OK' if gmail_ok else 'FALLO'}")
    print(f"{'[OK]' if cloudinary_ok else '[X]'} Cloudinary: {'OK' if cloudinary_ok else 'FALLO'}")

    if db_ok and gmail_ok and cloudinary_ok:
        print("\n[***] Todas las pruebas pasaron exitosamente!")
        print("[OK] Tu aplicacion esta lista para funcionar en desarrollo")
        print("[OK] Puedes proceder con el deploy a Railway cuando estes listo")
    else:
        print("\n[!] Algunas pruebas fallaron. Revisa los errores arriba.")

    print("\n" + "="*60)
