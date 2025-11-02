#!/usr/bin/env python
"""
Script para debuggear qué palabras extrae el PDF con los parámetros actuales
"""
import pdfplumber
import sys

def debug_palabras(pdf_path):
    """Muestra las primeras palabras extraídas con diferentes parámetros"""

    print(f"\n{'='*70}")
    print(f"DEBUG: {pdf_path}")
    print(f"{'='*70}\n")

    with pdfplumber.open(pdf_path) as pdf:
        primera_pagina = pdf.pages[0]

        # Método 1: SIN parámetros (el que funciona en el script)
        print("📌 MÉTODO 1: extract_words() SIN parámetros")
        print("-" * 70)
        palabras_sin_params = primera_pagina.extract_words()
        print(f"Total palabras: {len(palabras_sin_params)}")
        print("\nPrimeras 20 palabras:")
        for i, w in enumerate(palabras_sin_params[:20], 1):
            texto = w.get('text', '')
            if 'recibo' in texto.lower():
                print(f"  {i:3d}. '{texto}' ⭐ ENCONTRADO!")
            else:
                print(f"  {i:3d}. '{texto}'")

        # Método 2: CON parámetros (el que usa PDFProcessor)
        print(f"\n📌 MÉTODO 2: extract_words() CON x_tolerance=3, y_tolerance=3")
        print("-" * 70)
        palabras_con_params = primera_pagina.extract_words(
            x_tolerance=3,
            y_tolerance=3,
            extra_attrs=["text", "x0", "y0", "x1", "y1"]
        )
        print(f"Total palabras: {len(palabras_con_params)}")
        print("\nPrimeras 20 palabras:")
        for i, w in enumerate(palabras_con_params[:20], 1):
            texto = w.get('text', '')
            if 'recibo' in texto.lower():
                print(f"  {i:3d}. '{texto}' ⭐ ENCONTRADO!")
            else:
                print(f"  {i:3d}. '{texto}'")

        # Buscar "Recibo" en TODO el texto
        print(f"\n🔍 BUSCANDO 'Recibo' (case-insensitive) en TODAS las palabras:")
        print("-" * 70)

        encontrados_metodo1 = [w for w in palabras_sin_params if 'recibo' in w.get('text', '').lower()]
        encontrados_metodo2 = [w for w in palabras_con_params if 'recibo' in w.get('text', '').lower()]

        print(f"Método 1 (sin params): {len(encontrados_metodo1)} ocurrencias")
        print(f"Método 2 (con params): {len(encontrados_metodo2)} ocurrencias")

        if encontrados_metodo1:
            print("\n✅ Con Método 1 encontró:")
            for w in encontrados_metodo1[:10]:
                print(f"   - '{w.get('text')}' en Y={w.get('y0', w.get('top', 'N/A'))}")

        if encontrados_metodo2:
            print("\n✅ Con Método 2 encontró:")
            for w in encontrados_metodo2[:10]:
                print(f"   - '{w.get('text')}' en Y={w.get('y0', 'N/A')}")

        # Mostrar estructura esperada
        print(f"\n💡 ESTRUCTURA ESPERADA:")
        print("-" * 70)
        print(f"Cada página debería tener 4 recibos")
        print(f"Cada recibo comienza con: 'Recibo individual de pagos'")
        print(f"Total esperado en 6 páginas: 24 recibos")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nUso: python debug_palabras.py archivo.pdf\n")
    else:
        debug_palabras(sys.argv[1])
