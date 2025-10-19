# API Planilla de Recaudación

API REST para procesar planillas de recaudación usando Azure Form Recognizer.

## 🚀 Estado del Proyecto

✅ **COMPLETADO:**
- API REST Django funcional
- Modelos de datos completos
- Integración Azure Form Recognizer configurada
- Endpoint: https://azure-rendibus.cognitiveservices.azure.com/
- Credenciales configuradas y probadas

🔄 **PENDIENTE:**
- Integración con modelo entrenado personalizado
- Mapeo de campos específicos del modelo

- **API REST completa** con Django REST Framework
- **Subida de imágenes** de planillas
- **Procesamiento automático** con Azure Form Recognizer
- **Modelos estructurados** para tarifas, ingresos, egresos y control de boletos
- **Panel de administración** Django
- **CORS configurado** para aplicaciones móviles

## 📋 Requisitos

- Python 3.8+
- Django 4.2.7
- Azure Form Recognizer (opcional para desarrollo)

## 🛠️ Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd api_planilla
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Iniciar servidor**
```bash
python manage.py runserver
```

## 🔧 Configuración Azure Form Recognizer

1. **Crear cuenta Azure** (puede tardar 48 horas)
2. **Crear recurso Form Recognizer** en Azure Portal
3. **Obtener credenciales**:
   - Endpoint: `https://tu-recurso.cognitiveservices.azure.com/`
   - API Key: `tu-clave-api`

4. **Configurar variables** (crear archivo `.env`):
```env
AZURE_FORM_RECOGNIZER_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=tu-clave-api
```

5. **Probar conexión**:
```bash
python azure_test.py
```

## 📡 Endpoints API

### Planillas
- `GET /api/planillas/` - Listar planillas
- `POST /api/planillas/` - Crear planilla (subir imagen)
- `GET /api/planillas/{id}/` - Detalle de planilla
- `POST /api/planillas/{id}/procesar_con_azure/` - Procesar con Azure
- `GET /api/planillas/{id}/datos_extraidos/` - Obtener datos extraídos
- `GET /api/planillas/test_azure_connection/` - Probar conexión Azure

### Otros modelos
- `GET /api/tarifas/` - Listar tarifas
- `GET /api/ingresos/` - Listar ingresos
- `GET /api/egresos/` - Listar egresos
- `GET /api/control-boletos/` - Listar controles de boletos

### Admin
- `http://127.0.0.1:8000/admin/` - Panel de administración

## 🧪 Pruebas

### Probar conexión Azure
```bash
python azure_test.py
```

### Probar análisis de documento
```bash
python azure_test.py ruta/a/tu/imagen.jpg
```

### Probar API con Postman/Thunder Client

**Subir imagen:**
```http
POST http://127.0.0.1:8000/api/planillas/
Content-Type: multipart/form-data

imagen: [archivo de imagen]
```

**Procesar con Azure:**
```http
POST http://127.0.0.1:8000/api/planillas/1/procesar_con_azure/
```

**Obtener datos extraídos:**
```http
GET http://127.0.0.1:8000/api/planillas/1/datos_extraidos/
```

## 📊 Modelos de Datos

### Planilla
- `imagen` - Archivo de imagen
- `status` - Estado del procesamiento (pending, processing, completed, error)
- `datos_extraidos` - JSON con datos de Azure Form Recognizer
- `error_procesamiento` - Mensaje de error si falla

### Tarifa
- `concepto` - Concepto de la tarifa
- `precio` - Precio unitario
- `cantidad` - Cantidad vendida
- `subtotal` - Precio × cantidad

### Ingreso/Egreso
- `concepto` - Concepto del movimiento
- `monto` - Monto del movimiento
- `observaciones` - Observaciones adicionales

### ControlBoleto
- `numero_inicial` - Número inicial del talonario
- `numero_final` - Número final del talonario
- `cantidad_vendidos` - Boletos vendidos
- `cantidad_devueltos` - Boletos devueltos
- `cantidad_anulados` - Boletos anulados
- `total_boletos` - Total calculado automáticamente
- `boletos_faltantes` - Boletos faltantes calculados

## 🔍 Estados de Procesamiento

- **pending** - Imagen subida, esperando procesamiento
- **processing** - Enviada a Azure Form Recognizer
- **completed** - Procesada exitosamente
- **error** - Error en el procesamiento

## 📝 Logs

Los logs se guardan en el sistema de logging de Django. Para ver logs detallados:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🚨 Solución de Problemas

### Error: "Azure Form Recognizer not configured"
- Verificar que las variables de entorno estén configuradas
- Comprobar que el endpoint y la clave sean correctos

### Error: "Image file not found"
- Verificar que la imagen se haya subido correctamente
- Comprobar permisos de archivos en la carpeta `media/`

### Error de conexión Azure
- Verificar conectividad a internet
- Comprobar que el recurso Azure esté activo
- Verificar límites de cuota de Azure

## 📞 Soporte

Para problemas o dudas:
1. Revisar los logs del servidor
2. Probar la conexión con `python azure_test.py`
3. Verificar configuración en el panel de administración
