#!/usr/bin/env python
"""
Script de prueba para verificar qué detecta el programa en un PDF
Uso: python test_pdf_detection.py ruta/al/archivo.pdf
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabiliadad.settings')
django.setup()

from separador_recibos.utils.pdf_processor import PDFProcessor
import pdfplumber


def test_pdf(pdf_path):
    """Prueba la detección de recibos en un PDF"""
    print(f"\n{'='*60}")
    print(f"ANALIZANDO: {pdf_path}")
    print(f"{'='*60}\n")

    # 1. Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: El archivo no existe: {pdf_path}")
        return

    # 2. Mostrar primeras palabras del PDF
    print("📄 PRIMERAS 50 PALABRAS DEL PDF:")
    print("-" * 60)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            primera_pagina = pdf.pages[0]
            palabras = primera_pagina.extract_words()

            for i, word in enumerate(palabras[:50]):
                print(f"{i+1:3d}. '{word['text']}'")

            print(f"\n✅ Total de palabras en primera página: {len(palabras)}")
    except Exception as e:
        print(f"❌ Error leyendo PDF: {e}")
        return

    # 3. Buscar "Recibo individual de pagos"
    print(f"\n🔍 BUSCANDO: 'Recibo individual de pagos'")
    print("-" * 60)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina_num, pagina in enumerate(pdf.pages):
                palabras = pagina.extract_words(
                    x_tolerance=3,
                    y_tolerance=3,
                    extra_attrs=["text", "x0", "y0", "x1", "y1"]
                )

                # Buscar palabra "Recibo"
                for i, word in enumerate(palabras):
                    if word.get('text', '').lower() == 'recibo':
                        # Juntar siguientes palabras
                        frase = []
                        for j in range(i, min(i + 8, len(palabras))):
                            if abs(palabras[j].get('y0', 0) - word.get('y0', 0)) < 5:
                                frase.append(palabras[j].get('text', ''))

                        texto_junto = ' '.join(frase)

                        if 'individual' in texto_junto.lower() and 'pagos' in texto_junto.lower():
                            print(f"✅ ENCONTRADO en página {pagina_num + 1}:")
                            print(f"   Texto: '{texto_junto}'")
                            print(f"   Coordenadas: X={word.get('x0', 0):.1f}, Y={word.get('y0', 0):.1f}")
    except Exception as e:
        print(f"❌ Error buscando patrón: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Ejecutar detección del procesador
    print(f"\n🤖 EJECUTANDO DETECTOR DE RECIBOS:")
    print("-" * 60)
    try:
        processor = PDFProcessor(pdf_path)
        recibos = processor.detectar_recibos_coordenadas()

        print(f"✅ RECIBOS DETECTADOS: {len(recibos)}")

        for i, recibo in enumerate(recibos, 1):
            print(f"\n📋 Recibo #{i}:")
            print(f"   Página: {recibo.get('pagina')}")
            print(f"   Beneficiario: {recibo.get('beneficiario', 'No detectado')}")
            print(f"   Valor: ${recibo.get('valor', 'No detectado')}")
            print(f"   Entidad: {recibo.get('entidad', 'No detectado')}")
            print(f"   Referencia: {recibo.get('referencia', 'No detectado')}")

    except Exception as e:
        print(f"❌ Error en detección: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'='*60}")
    print("ANÁLISIS COMPLETADO")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\n❌ Uso: python test_pdf_detection.py ruta/al/archivo.pdf\n")
        print("Ejemplo:")
        print("  python test_pdf_detection.py analisis.pdf")
        print("  python test_pdf_detection.py C:\\Users\\User\\Desktop\\recibos.pdf")
        print()
    else:
        pdf_path = sys.argv[1]
        test_pdf(pdf_path)
