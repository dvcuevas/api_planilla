# 📋 FUNCIONAMIENTO DE LA API REST PLANILLA (VERSIÓN SIMPLE)

## **🔄 FLUJO SIMPLE DE LA API (1 SOLO PASO)**

### **ÚNICO PASO: Subir y Procesar Imagen**
```
POST /api/planillas/
Content-Type: multipart/form-data
Body (form-data):
- imagen: [archivo de imagen]
- nombre_archivo: "planilla.jpg"

RESPUESTA DESPUÉS DEL PROCESAMIENTO (201 Created):
{
  "id": 1,
  "imagen": "/media/planillas/planilla.jpg",
  "status": "completed",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:35:00Z",
  "nombre_archivo": "planilla.jpg",
  "tamaño_archivo": 245760,
  "datos_extraidos": {
    "tarifas": [
      {
        "concepto": "Tarifa 1",
        "precio": 2000.0,
        "cantidad": 1,
        "subtotal": 0
      },
      {
        "concepto": "Tarifa 2",
        "precio": 3000.0,
        "cantidad": 1,
        "subtotal": 0
      }
    ],
    "ingresos": [
      {
        "concepto": "Total Ingreso Ruta",
        "monto": 58000.0,
        "observaciones": "Ingreso en ruta"
      },
      {
        "concepto": "Total Ingreso Oficina",
        "monto": 900000.0,
        "observaciones": "Ingreso en oficina"
      }
    ],
    "egresos": [
      {
        "concepto": "Losa",
        "monto": 5900.0,
        "observaciones": "Egreso: Losa"
      },
      {
        "concepto": "Cena",
        "monto": 10000.0,
        "observaciones": "Egreso: Cena"
      },
      {
        "concepto": "Viáticos",
        "monto": 10000.0,
        "observaciones": "Egreso: Viáticos"
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

**¿Qué hace la API automáticamente?**
1. Recibe la imagen
2. La guarda en `/media/planillas/`
3. Crea un registro en la base de datos
4. **INMEDIATAMENTE** envía la imagen a Azure Form Recognizer
5. Azure procesa con el modelo `rendibus.v1`
6. Azure devuelve datos extraídos
7. La API mapea los datos a la estructura interna
8. Responde con **TODO** (imagen guardada + datos extraídos)

**Tiempo de respuesta:** 10-30 segundos (depende del procesamiento de Azure)

---

## **🔍 ENDPOINTS ADICIONALES**

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

### **Listar Todas las Planillas**
```
GET /api/planillas/

RESPUESTA (200 OK):
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "imagen": "/media/planillas/planilla.jpg",
      "status": "completed",
      "fecha_creacion": "2024-01-15T10:30:00Z",
      "nombre_archivo": "planilla.jpg"
    }
  ]
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
POST /api/planillas/
Body: imagen válida pero Azure falla

RESPUESTA (500 Internal Server Error):
{
  "id": 1,
  "imagen": "/media/planillas/planilla.jpg",
  "status": "error",
  "error_procesamiento": "Error procesando planilla: [detalle del error]",
  "datos_extraidos": null
}
```

### **Azure No Configurado**
```
POST /api/planillas/
Body: imagen válida pero Azure no configurado

RESPUESTA (503 Service Unavailable):
{
  "error": "Azure Form Recognizer no está configurado"
}
```

---

## **📊 ESTADOS DE PLANILLA**

| **Estado** | **Descripción** | **Cuándo Ocurre** |
|------------|-----------------|-------------------|
| `completed` | Procesada exitosamente | Azure procesó correctamente |
| `error` | Error en procesamiento | Azure falló o imagen corrupta |

**Nota:** No hay estados `pending` ni `processing` porque todo es automático.

---

## **🎯 VENTAJAS DEL FLUJO SIMPLE**

### **✅ Ventajas:**
- **Simplicidad máxima**: Un solo request desde la app
- **Experiencia de usuario**: Sube imagen → obtiene datos (automático)
- **Menos código**: La app no necesita manejar 2 pasos
- **Menos errores**: No hay que coordinar 2 requests
- **Estándar**: Es como funcionan la mayoría de APIs de procesamiento
- **Intuitivo**: El usuario hace una acción y obtiene el resultado

### **❌ Desventajas:**
- **Tiempo de espera**: 10-30 segundos de respuesta
- **Timeout**: Posibles problemas con timeouts de red
- **Bloqueo**: La app queda esperando
- **Experiencia**: Si falla, el usuario debe reintentar todo
- **Recursos**: No se puede subir múltiples imágenes simultáneamente

---

## **🔧 IMPLEMENTACIÓN TÉCNICA**

### **Cambios Necesarios:**
1. **Modificar `PlanillaViewSet.create()`**:
   - Después de guardar la imagen
   - Llamar automáticamente a `azure_service.analyze_document()`
   - Actualizar el status a `completed` o `error`
   - Incluir `datos_extraidos` en la respuesta

2. **Eliminar endpoint `procesar_con_azure`**:
   - Ya no es necesario
   - Simplifica la API

3. **Modificar serializadores**:
   - `PlanillaCreateSerializer` debe incluir `datos_extraidos`
   - Manejar errores de procesamiento

### **Código de Ejemplo:**
```python
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
        planilla = serializer.save()
        
        # PROCESAMIENTO AUTOMÁTICO
        try:
            if azure_service.is_configured():
                image_path = os.path.join(settings.MEDIA_ROOT, planilla.imagen.name)
                datos_extraidos = azure_service.analyze_document(image_path)
                
                planilla.datos_extraidos = datos_extraidos
                planilla.status = 'completed'
                planilla.save()
            else:
                planilla.status = 'error'
                planilla.error_procesamiento = 'Azure Form Recognizer no configurado'
                planilla.save()
        except Exception as e:
            planilla.status = 'error'
            planilla.error_procesamiento = str(e)
            planilla.save()
        
        return Response(
            PlanillaDetailSerializer(planilla).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

## **📝 COMPARACIÓN: ACTUAL vs SIMPLE**

| **Aspecto** | **Actual (2 pasos)** | **Simple (1 paso)** |
|-------------|---------------------|---------------------|
| **Requests desde app** | 2 | 1 |
| **Tiempo de respuesta** | Inmediato + 10-30s | 10-30s |
| **Complejidad app** | Media | Baja |
| **Experiencia usuario** | 2 acciones | 1 acción |
| **Manejo errores** | Por paso | Todo junto |
| **Flexibilidad** | Alta | Baja |
| **Estándar industria** | Menos común | Más común |

---

## **🎯 RECOMENDACIÓN**

**La versión simple es mejor porque:**
1. **Es más simple** para el desarrollador de la app
2. **Es más intuitiva** para el usuario final
3. **Es el estándar** en APIs de procesamiento de documentos
4. **Menos complejidad** en el frontend
5. **Menos puntos de fallo**

**¿Quieres que implemente la versión simple?**
