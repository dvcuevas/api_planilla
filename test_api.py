#!/usr/bin/env python
"""
Script para probar todos los endpoints de la API.
Verifica que la API esté funcionando correctamente.
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoint(method, endpoint, data=None, files=None):
    """Probar un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        else:
            return False, f"Método {method} no soportado"
        
        return response.status_code < 400, f"{method} {endpoint}: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return False, f"Error de conexión: {method} {endpoint}"
    except Exception as e:
        return False, f"Error: {method} {endpoint} - {str(e)}"

def test_api_endpoints():
    """Probar todos los endpoints de la API"""
    print("=" * 60)
    print("PRUEBA DE ENDPOINTS DE LA API")
    print("=" * 60)
    
    # Lista de endpoints a probar
    endpoints = [
        ("GET", "/planillas/"),
        ("GET", "/planillas/test_azure_connection/"),
        ("GET", "/tarifas/"),
        ("GET", "/ingresos/"),
        ("GET", "/egresos/"),
        ("GET", "/control-boletos/"),
    ]
    
    results = []
    
    for method, endpoint in endpoints:
        success, message = test_endpoint(method, endpoint)
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        results.append(success)
    
    # Resumen
    total = len(results)
    passed = sum(results)
    
    print("\n" + "=" * 60)
    print(f"RESUMEN: {passed}/{total} endpoints funcionando")
    
    if passed == total:
        print("🎉 ¡TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
    else:
        print("⚠️  Algunos endpoints tienen problemas")
    
    return passed == total

def test_image_upload():
    """Probar subida de imagen (requiere imagen de prueba)"""
    print("\n" + "=" * 60)
    print("PRUEBA DE SUBIDA DE IMAGEN")
    print("=" * 60)
    
    # Buscar imagen de prueba
    test_images = [
        "test_image.jpg",
        "test_image.png", 
        "planilla_test.jpg",
        "planilla_test.png"
    ]
    
    image_path = None
    for img in test_images:
        if os.path.exists(img):
            image_path = img
            break
    
    if not image_path:
        print("⚠️  No se encontró imagen de prueba")
        print("Para probar subida de imágenes, coloca una imagen llamada:")
        print("- test_image.jpg")
        print("- test_image.png")
        print("- planilla_test.jpg")
        print("- planilla_test.png")
        return False
    
    print(f"📷 Probando con imagen: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'imagen': f}
            data = {'nombre_archivo': image_path}
            
            response = requests.post(f"{BASE_URL}/planillas/", data=data, files=files)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Imagen subida exitosamente")
                print(f"   ID de planilla: {result.get('id')}")
                print(f"   Status: {result.get('status')}")
                return True
            else:
                print(f"❌ Error subiendo imagen: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print("API Planilla - Script de Prueba")
    print("===============================")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/planillas/", timeout=5)
        if response.status_code >= 400:
            print("❌ El servidor no está respondiendo correctamente")
            return
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("Asegúrate de que el servidor Django esté corriendo:")
        print("python manage.py runserver")
        return
    
    print("✅ Servidor Django detectado")
    
    # Probar endpoints
    endpoints_ok = test_api_endpoints()
    
    # Probar subida de imagen
    upload_ok = test_image_upload()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    if endpoints_ok and upload_ok:
        print("🎉 ¡API COMPLETAMENTE FUNCIONAL!")
        print("\n📋 Próximos pasos:")
        print("1. Configurar credenciales de Azure Form Recognizer")
        print("2. Probar procesamiento de imágenes con Azure")
        print("3. Integrar con la aplicación móvil")
    elif endpoints_ok:
        print("✅ Endpoints funcionando correctamente")
        print("⚠️  Subida de imágenes necesita imagen de prueba")
    else:
        print("❌ Hay problemas con algunos endpoints")
        print("Revisa los logs del servidor Django")

if __name__ == "__main__":
    main()
