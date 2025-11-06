# -*- coding: utf-8 -*-
"""
Script de prueba para verificar notificación de nuevo proveedor
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
django.setup()

from proveedores.models import Proveedor
from core.utils import notificar_nuevo_proveedor

def test_notificacion_proveedor():
    """Prueba de notificación de nuevo proveedor"""
    print("\n" + "="*60)
    print("PRUEBA DE NOTIFICACION DE NUEVO PROVEEDOR")
    print("="*60)

    # Buscar el último proveedor registrado
    try:
        proveedor = Proveedor.objects.latest('fecha_creacion')
        print(f"\n[*] Proveedor encontrado:")
        print(f"   - Nombre: {proveedor.nombre_razon_social}")
        print(f"   - {proveedor.get_tipo_identificacion_display()}: {proveedor.numero_identificacion}")
        print(f"   - Ciudad: {proveedor.municipio if hasattr(proveedor, 'municipio') else 'N/A'}")

        # Obtener contactos e impuestos
        contactos = proveedor.contactos.all()
        impuestos = proveedor.impuestos.all()

        print(f"\n[*] Contactos: {contactos.count()}")
        for contacto in contactos:
            print(f"   - {contacto.nombre_apellidos} ({contacto.correo_electronico})")

        print(f"\n[*] Impuestos: {impuestos.count()}")
        for impuesto in impuestos:
            if impuesto.aplica:
                print(f"   - {impuesto.get_tipo_impuesto_display()}: {impuesto.porcentaje}%")

        # Enviar notificación
        print(f"\n[->] Enviando notificación...")

        resultado = notificar_nuevo_proveedor(
            proveedor=proveedor,
            contactos=contactos,
            impuestos=impuestos,
            url_sistema=f"http://localhost:8000/proveedores/{proveedor.pk}/"
        )

        if resultado:
            print("[OK] Notificacion enviada exitosamente!")
            print(f"   Revisa la bandeja de recepcionfacturaschvs@gmail.com")
            return True
        else:
            print("[X] No se pudo enviar la notificacion")
            return False

    except Proveedor.DoesNotExist:
        print("[X] No hay proveedores registrados en el sistema")
        print("\n[i] Para probar:")
        print("   1. Registra un proveedor desde el formulario web")
        print("   2. O usa el shell de Django para crear uno manualmente")
        return False

    except Exception as e:
        print(f"[X] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCRIPT DE PRUEBA - NOTIFICACION DE PROVEEDOR")
    print("=" * 60)

    resultado = test_notificacion_proveedor()

    print("\n" + "="*60)
    if resultado:
        print("[***] Prueba completada exitosamente!")
        print("[OK] El sistema esta listo para enviar notificaciones")
        print("[OK] Cada vez que se registre un proveedor se enviara un correo")
    else:
        print("[!] La prueba fallo. Revisa los errores arriba.")

    print("="*60 + "\n")
