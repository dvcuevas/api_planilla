#!/usr/bin/env python
"""
Script para probar la conexión con Azure Form Recognizer.
Este script puede ejecutarse independientemente para verificar las credenciales.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planilla_api.settings')
django.setup()

from api.services import AzureFormRecognizerService
from django.conf import settings


def test_azure_connection():
    """Probar la conexión con Azure Form Recognizer"""
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN AZURE FORM RECOGNIZER")
    print("=" * 50)
    
    # Verificar configuración
    print(f"Endpoint configurado: {settings.AZURE_FORM_RECOGNIZER_ENDPOINT}")
    print(f"Key configurada: {'Sí' if settings.AZURE_FORM_RECOGNIZER_KEY else 'No'}")
    print()
    
    # Crear servicio
    service = AzureFormRecognizerService()
    
    if not service.is_configured():
        print("❌ ERROR: Azure Form Recognizer no está configurado")
        print("Configura las siguientes variables en tu archivo .env:")
        print("AZURE_FORM_RECOGNIZER_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/")
        print("AZURE_FORM_RECOGNIZER_KEY=tu-clave-api")
        return False
    
    # Probar conexión
    print("🔄 Probando conexión...")
    result = service.test_connection()
    
    if result['success']:
        print("✅ CONEXIÓN EXITOSA")
        print(f"   Endpoint: {result['endpoint']}")
        print(f"   Páginas detectadas: {result.get('pages_detected', 0)}")
    else:
        print("❌ ERROR DE CONEXIÓN")
        print(f"   Error: {result['error']}")
        print(f"   Endpoint: {result['endpoint']}")
        print(f"   Key configurada: {result['key_configured']}")
    
    return result['success']


def test_document_analysis(image_path: str):
    """
    Probar análisis de documento con una imagen específica.
    
    Args:
        image_path: Ruta a la imagen a analizar
    """
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Archivo no encontrado: {image_path}")
        return False
    
    print("=" * 50)
    print("ANÁLISIS DE DOCUMENTO")
    print("=" * 50)
    print(f"Archivo: {image_path}")
    print()
    
    service = AzureFormRecognizerService()
    
    if not service.is_configured():
        print("❌ ERROR: Azure Form Recognizer no está configurado")
        return False
    
    try:
        print("🔄 Analizando documento...")
        result = service.analyze_document(image_path)
        
        print("✅ ANÁLISIS COMPLETADO")
        print(f"   Texto extraído: {len(result.get('texto_completo', ''))} caracteres")
        print(f"   Tablas detectadas: {len(result.get('tablas', []))}")
        print(f"   Campos detectados: {len(result.get('campos_detectados', {}))}")
        
        # Mostrar campos detectados
        if result.get('campos_detectados'):
            print("\n📋 CAMPOS DETECTADOS:")
            for key, value in result['campos_detectados'].items():
                print(f"   {key}: {value['value']} (confianza: {value['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Función principal"""
    print("Azure Form Recognizer - Script de Prueba")
    print("=========================================")
    
    # Probar conexión
    connection_ok = test_azure_connection()
    
    if not connection_ok:
        print("\n💡 CONSEJOS:")
        print("1. Crea una cuenta en Azure Portal")
        print("2. Crea un recurso 'Form Recognizer'")
        print("3. Obtén el endpoint y la clave API")
        print("4. Configura las variables en tu archivo .env")
        return
    
    # Si hay argumentos, probar análisis de documento
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_document_analysis(image_path)
    else:
        print("\n💡 Para probar análisis de documento:")
        print("python azure_test.py ruta/a/tu/imagen.jpg")


if __name__ == "__main__":
    main()
