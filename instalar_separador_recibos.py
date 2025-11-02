#!/usr/bin/env python3
"""
Script de instalación automática para Separador de Recibos PDF
Sistema de Contabilidad CHVS

Este script automatiza la instalación y configuración inicial de la aplicación
de separación de recibos PDF.
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}:")
        print(f"Comando: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Verifica versión de Python"""
    print("🐍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def install_dependencies():
    """Instala dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    dependencies = [
        "Django>=5.2.0",
        "Pillow>=12.0.0", 
        "PyPDF2==3.0.1",
        "pdfplumber==0.10.3",
        "reportlab==4.0.7",
        "opencv-python==4.8.1.78",
        "django-storages==1.14.2",
        "celery==5.3.4",
        "redis==5.0.1",
        "PyMuPDF==1.23.14",
        "pdf2image==1.17.0",
        "matplotlib==3.7.2",
        "Wand==0.6.13",
        "python-dateutil==2.8.2"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install {dep}", 
                          f"Instalando {dep.split('>=')[0].split('==')[0]}"):
            return False
    
    return True

def create_directories():
    """Crea directorios necesarios"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        "media",
        "media/pdfs_originales", 
        "media/pdfs_procesados",
        "media/imagenes_recibos",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")
    
    return True

def setup_django():
    """Configura Django y la base de datos"""
    print("\n⚙️ Configurando Django...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
    django.setup()
    
    # Ejecutar migraciones
    print("📊 Ejecutando migraciones...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Base de datos configurada")
    return True

def create_superuser():
    """Crea superusuario para Django Admin"""
    print("\n👤 Configurando superusuario...")
    
    from django.contrib.auth.models import User
    from django.db import connection
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superusuario ya existe")
        return True
    
    # Crear superusuario por defecto
    print("📝 Creando superusuario por defecto...")
    print("   Usuario: admin")
    print("   Email: admin@contabilidad.com")
    print("   Contraseña: admin123")
    
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@contabilidad.com', 
            password='admin123'
        )
        print("✅ Superusuario creado")
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        print("⚠️  Puedes crear uno manualmente con: python manage.py createsuperuser")
        return True

def verify_installation():
    """Verifica que la instalación sea correcta"""
    print("\n🔍 Verificando instalación...")
    
    try:
        # Verificar Django
        import django
        print(f"✅ Django {django.get_version()}")
        
        # Verificar dependencias
        import PyPDF2
        print(f"✅ PyPDF2 {PyPDF2.__version__}")
        
        import pdfplumber
        print(f"✅ pdfplumber {pdfplumber.__version__}")
        
        import reportlab
        print(f"✅ reportlab {reportlab.Version}")
        
        # Verificar que la app existe
        from separador_recibos import models
        print("✅ Aplicación separador_recibos importada correctamente")
        
        print("✅ Verificación completada")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def print_success_message():
    """Muestra mensaje de éxito y siguientes pasos"""
    print("\n" + "="*60)
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("="*60)
    
    print("\n📋 INFORMACIÓN DE ACCESO:")
    print("   🌐 URL de la aplicación: http://localhost:8000/separador/")
    print("   🔧 Panel de administración: http://localhost:8000/admin/")
    print("   👤 Usuario admin: admin")
    print("   🔑 Contraseña admin: admin123")
    
    print("\n🚀 PASOS SIGUIENTES:")
    print("   1. Ejecutar el servidor:")
    print("      python manage.py runserver")
    print()
    print("   2. (Opcional) Iniciar Celery para procesamiento asíncrono:")
    print("      celery -A contabiliadad worker -l info")
    print()
    print("   3. (Opcional) Iniciar Redis para Celery:")
    print("      redis-server")
    
    print("\n📚 DOCUMENTACIÓN:")
    print("   📖 README completo: separador_recibos/README.md")
    print("   🏗️ Arquitectura: ARQUITECTURA_RECIBOS_PDF.md")
    
    print("\n🔍 FUNCIONALIDADES PRINCIPALES:")
    print("   ✅ Detección automática de recibos")
    print("   ✅ Extracción de imágenes de alta calidad")
    print("   ✅ Generación de PDF separado por recibo")
    print("   ✅ Tabla completa para seguimiento")
    print("   ✅ Dashboard con estadísticas")
    print("   ✅ Filtros avanzados de búsqueda")
    print("   ✅ Validación manual de datos")
    print("   ✅ Exportación a CSV")
    
    print("\n🎯 PARA PROBAR LA APLICACIÓN:")
    print("   1. Ve a http://localhost:8000/separador/")
    print("   2. Inicia sesión con admin/admin123")
    print("   3. Sube tu archivo PDF de recibos")
    print("   4. Espera el procesamiento")
    print("   5. Revisa los resultados en la tabla")
    
    print("\n" + "="*60)

def main():
    """Función principal de instalación"""
    print("🚀 INSTALADOR AUTOMÁTICO - SEPARADOR DE RECIBOS PDF")
    print("="*60)
    print("Sistema de Contabilidad CHVS")
    print("="*60)
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear directorios
    if not create_directories():
        print("❌ Error creando directorios")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)
    
    # Configurar Django
    if not setup_django():
        print("❌ Error configurando Django")
        sys.exit(1)
    
    # Crear superusuario
    create_superuser()
    
    # Verificar instalación
    if not verify_installation():
        print("❌ Error en verificación de instalación")
        sys.exit(1)
    
    # Mostrar mensaje de éxito
    print_success_message()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        print("💡 Por favor, revisa los requisitos e intenta de nuevo")
        sys.exit(1)