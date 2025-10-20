# 📋 FUNCIONAMIENTO DE LA API REST PLANILLA

## **🔄 FLUJO ACTUAL DE LA API (2 PASOS)**

### **PASO 1: Subir Imagen**
```
POST /api/planillas/
Content-Type: multipart/form-data
Body (form-data):
- imagen: [archivo de imagen]
- nombre_archivo: "planilla.jpg"

RESPUESTA INMEDIATA (201 Created):
{
  "id": 1,
  "imagen": "/media/planillas/planilla.jpg",
  "status": "pending",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "nombre_archivo": "planilla.jpg",
  "tamaño_archivo": 245760
}
```

**¿Qué hace la API?**
- Recibe la imagen
- La guarda en `/media/planillas/`
- Crea un registro en la base de datos
- Responde inmediatamente con el ID

---

### **PASO 2: Procesar con Azure**
```
POST /api/planillas/1/procesar_con_azure/
Content-Type: application/json
Body: {}

RESPUESTA DESPUÉS DEL PROCESAMIENTO (200 OK):
{
  "message": "Planilla procesada exitosamente",
  "planilla_id": 1,
  "status": "completed",
  "datos_extraidos": {
    "tarifas": [
      {
        "concepto": "Tarifa 1",
        "precio": 2000.0,
        "cantidad": 1,
        "subtotal": 0
      }
    ],
    "ingresos": [
      {
        "concepto": "Total Ingreso Ruta",
        "monto": 58000.0,
        "observaciones": "Ingreso en ruta"
      }
    ],
    "egresos": [
      {
        "concepto": "Losa",
        "monto": 5900.0,
        "observaciones": "Egreso: Losa"
      }
    ],
    "control_boletos": [
      {
        "numero_inicial": 2080,
        "numero_final": 2080,
        "cantidad_vendidos": 1,
        "cantidad_devueltos": 0,
        "cantidad_anulados": 0
      }
    ],
    "info_general": {
      "ciudad_origen": "Parral",
      "ciudad_retorno": "Santiago",
      "fecha": "2025-11-03",
      "numero_planilla": "00028",
      "conductor": "David Salgado",
      "codigo_conductor": "149",
      "asistente": "NICOLAS BORIC",
      "codigo_asistente": "67",
      "numero_bus": "148",
      "patente_bus": "SSKP-91",
      "horario_origen": "11:40",
      "horario_retorno": "22:50"
    }
  }
}
```

**¿Qué hace la API?**
- Toma la imagen guardada
- La envía a Azure Form Recognizer
- Azure procesa con el modelo `rendibus.v1`
- Azure devuelve datos extraídos
- La API mapea los datos a la estructura interna
- Responde con los datos estructurados

---

## **🔍 ENDPOINTS ADICIONALES**

### **Obtener Datos Extraídos**
```
GET /api/planillas/1/datos_extraidos/

RESPUESTA (200 OK):
{
  "planilla_id": 1,
  "datos_extraidos": { ... },
  "fecha_procesamiento": "2024-01-15T10:35:00Z"
}
```

### **Obtener Detalle Completo**
```
GET /api/planillas/1/

RESPUESTA (200 OK):
{
  "id": 1,
  "imagen": "/media/planillas/planilla.jpg",
  "status": "completed",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:35:00Z",
  "datos_extraidos": { ... },
  "error_procesamiento": null,
  "nombre_archivo": "planilla.jpg",
  "tamaño_archivo": 245760,
  "tarifas": [...],
  "ingresos": [...],
  "egresos": [...],
  "control_boletos": [...]
}
```

### **Probar Conexión Azure**
```
GET /api/planillas/test_azure_connection/

RESPUESTA (200 OK):
{
  "success": true,
  "message": "Azure Form Recognizer client configured"
}
```

---

## **⚠️ MANEJO DE ERRORES**

### **Error de Formato de Imagen**
```
POST /api/planillas/
Body: imagen con formato no válido

RESPUESTA (400 Bad Request):
{
  "error": "Formato de imagen no válido"
}
```

### **Error de Procesamiento Azure**
```
POST /api/planillas/1/procesar_con_azure/
Body: {}

RESPUESTA (500 Internal Server Error):
{
  "error": "Error procesando planilla: [detalle del error]"
}
```

### **Planilla Ya Procesada**
```
POST /api/planillas/1/procesar_con_azure/
Body: {}

RESPUESTA (400 Bad Request):
{
  "error": "La planilla ya ha sido procesada"
}
```

---

## **📊 ESTADOS DE PLANILLA**

| **Estado** | **Descripción** | **Acciones Permitidas** |
|------------|-----------------|-------------------------|
| `pending` | Imagen subida, sin procesar | Procesar con Azure |
| `processing` | En proceso con Azure | Ninguna |
| `completed` | Procesada exitosamente | Obtener datos |
| `error` | Error en procesamiento | Reintentar procesamiento |

---

## **🎯 VENTAJAS DEL FLUJO ACTUAL**

### **✅ Ventajas:**
- **Respuesta rápida**: El primer POST responde inmediatamente
- **Control del usuario**: Decide cuándo procesar
- **Manejo de errores**: Cada paso puede fallar independientemente
- **No bloquea**: La app no queda esperando
- **Flexibilidad**: Puede subir múltiples imágenes sin procesar

### **❌ Desventajas:**
- **Complejidad**: Requiere 2 requests desde la app
- **Coordinación**: La app debe manejar 2 pasos
- **Posibles errores**: Más puntos de fallo
- **Experiencia**: El usuario debe hacer 2 acciones

---

## **🔧 IMPLEMENTACIÓN TÉCNICA**

### **Archivos Principales:**
- `api/views.py`: ViewSets y acciones personalizadas
- `api/services.py`: Servicio Azure Form Recognizer
- `api/serializers.py`: Serializadores para cada acción
- `api/models.py`: Modelos de base de datos

### **Flujo Interno:**
1. **Subida**: `PlanillaViewSet.create()` → Guarda imagen
2. **Procesamiento**: `PlanillaViewSet.procesar_con_azure()` → Llama a Azure
3. **Mapeo**: `AzureFormRecognizerService._process_planilla_data()` → Estructura datos
4. **Respuesta**: Serializador → JSON estructurado

---

## **📝 RESUMEN**

**La API actual funciona en 2 pasos:**
1. **Subir imagen** → Respuesta inmediata con ID
2. **Procesar con Azure** → Respuesta con datos extraídos

**Es un diseño válido pero requiere coordinación desde la app.**
