import logging
from typing import Dict, Any
from django.conf import settings
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class AzureFormRecognizerService:
    """
    Servicio para interactuar con Azure Form Recognizer.
    Procesa imágenes de planillas y extrae datos estructurados.
    
    Configurado para usar:
    - Endpoint: https://azure-rendibus.cognitiveservices.azure.com/
    - Modelo entrenado personalizado (pendiente de configurar)
    - Mapeo de campos a modelos Django: Planilla, Tarifa, Ingreso, Egreso, ControlBoleto
    """
    
    def __init__(self):
        self.endpoint = settings.AZURE_FORM_RECOGNIZER_ENDPOINT
        self.key = settings.AZURE_FORM_RECOGNIZER_KEY
        self.model_id = settings.AZURE_FORM_RECOGNIZER_MODEL_ID
        
        if not self.endpoint or not self.key:
            logger.warning("Azure Form Recognizer credentials not configured")
            self.client = None
        else:
            try:
                self.client = DocumentAnalysisClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.key)
                )
                logger.info("Azure Form Recognizer client initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize Azure Form Recognizer client: %s", e)
                self.client = None
    
    def is_configured(self) -> bool:
        """Verificar si el servicio está configurado correctamente"""
        return self.client is not None and bool(self.endpoint and self.key)
    
    def analyze_document(self, image_path: str) -> Dict[str, Any]:
        """
        Analizar un documento usando el modelo entrenado personalizado.
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            Dict con los datos extraídos del documento
        """
        if not self.is_configured():
            raise ValueError("Azure Form Recognizer not configured")
        
        try:
            with open(image_path, "rb") as f:
                # Usar el modelo entrenado personalizado
                poller = self.client.begin_analyze_document(
                    self.model_id, 
                    document=f
                )
                result = poller.result()
            
            # Extraer datos del resultado
            extracted_data = self._extract_data_from_result(result)
            
            logger.info("Successfully analyzed document: %s", image_path)
            return extracted_data
            
        except AzureError as e:
            logger.error("Azure Form Recognizer error: %s", e)
            raise
        except FileNotFoundError:
            logger.error("Image file not found: %s", image_path)
            raise
        except Exception as e:
            logger.error("Unexpected error analyzing document: %s", e)
            raise
    
    def _extract_data_from_result(self, result) -> Dict[str, Any]:
        """
        Extraer datos estructurados del resultado del modelo entrenado.
        
        Args:
            result: Resultado del análisis de Azure
            
        Returns:
            Dict con los datos extraídos estructurados
        """
        extracted_data = {
            'raw_result': {},
            'tarifas': [],
            'ingresos': [],
            'egresos': [],
            'control_boletos': [],
            'texto_completo': '',
            'tablas': [],
            'campos_detectados': {}
        }
        
        try:
            # Extraer texto completo
            if hasattr(result, 'content'):
                extracted_data['texto_completo'] = result.content
            
            # Extraer tablas
            if hasattr(result, 'tables'):
                for table in result.tables:
                    table_data = {
                        'row_count': table.row_count,
                        'column_count': table.column_count,
                        'cells': []
                    }
                    
                    for cell in table.cells:
                        table_data['cells'].append({
                            'text': cell.content,
                            'row_index': cell.row_index,
                            'column_index': cell.column_index,
                            'confidence': cell.confidence
                        })
                    
                    extracted_data['tablas'].append(table_data)
            
            # Extraer campos específicos (key-value pairs)
            if hasattr(result, 'key_value_pairs'):
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        extracted_data['campos_detectados'][kv_pair.key.content] = {
                            'value': kv_pair.value.content,
                            'confidence': kv_pair.confidence
                        }
            
            # Guardar resultado completo incluyendo documentos
            extracted_data['raw_result'] = {
                'pages': len(result.pages) if hasattr(result, 'pages') else 0,
                'tables_count': len(result.tables) if hasattr(result, 'tables') else 0,
                'key_value_pairs_count': len(result.key_value_pairs) if hasattr(result, 'key_value_pairs') else 0,
                'documents': result.documents if hasattr(result, 'documents') else []
            }
            
            # Procesar datos específicos de planillas usando el modelo entrenado
            extracted_data = self._process_planilla_data(extracted_data)
            
        except Exception as e:
            logger.error("Error processing Azure result: %s", e)
            extracted_data['error'] = str(e)
        
        return extracted_data
    
    def _process_planilla_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos específicos del modelo entrenado rendibus.v1.
        
        Args:
            extracted_data: Datos extraídos de Azure
            
        Returns:
            Datos procesados específicos para planillas
        """
        try:
            # Obtener campos del documento
            documents = extracted_data.get('raw_result', {}).get('documents', [])
            if not documents:
                return extracted_data
            
            fields = documents[0].get('fields', {})
            
            # Procesar tarifas (Tarifa 1-6)
            tarifas = []
            for i in range(1, 7):
                tarifa_key = f"Tarifa {i}"
                if tarifa_key in fields:
                    tarifa_data = fields[tarifa_key]
                    tarifas.append({
                        'concepto': f'Tarifa {i}',
                        'precio': float(tarifa_data.get('valueString', '0').replace('.', '').replace(',', '.')),
                        'cantidad': 1,  # Se calculará basado en tickets
                        'subtotal': 0  # Se calculará
                    })
            
            # Procesar ingresos
            ingresos = []
            if 'Total Ingreso Ruta' in fields:
                ingresos.append({
                    'concepto': 'Total Ingreso Ruta',
                    'monto': float(fields['Total Ingreso Ruta'].get('valueString', '0').replace('.', '').replace(',', '.')),
                    'observaciones': 'Ingreso en ruta'
                })
            
            if 'Total Ingreso Oficina' in fields:
                ingresos.append({
                    'concepto': 'Total Ingreso Oficina',
                    'monto': float(fields['Total Ingreso Oficina'].get('valueString', '0').replace('.', '').replace(',', '.')),
                    'observaciones': 'Ingreso en oficina'
                })
            
            # Procesar egresos
            egresos = []
            egreso_fields = ['Losa', 'Cena', 'Viáticos', 'Pensión', 'Otros']
            for field_name in egreso_fields:
                if field_name in fields:
                    field_data = fields[field_name]
                    monto = field_data.get('valueNumber', 0)
                    if monto > 0:
                        egresos.append({
                            'concepto': field_name,
                            'monto': float(monto),
                            'observaciones': f'Egreso: {field_name}'
                        })
            
            # Procesar control de boletos
            control_boletos = []
            for i in range(1, 7):
                inicial_key = f"Ticket Inicial T{i}"
                final_key = f"Ticket Final T{i}"
                if inicial_key in fields and final_key in fields:
                    inicial = int(fields[inicial_key].get('valueString', '0'))
                    final = int(fields[final_key].get('valueString', '0'))
                    if final > inicial:
                        control_boletos.append({
                            'numero_inicial': inicial,
                            'numero_final': final,
                            'cantidad_vendidos': final - inicial + 1,
                            'cantidad_devueltos': 0,
                            'cantidad_anulados': 0
                        })
            
            # Agregar datos procesados
            extracted_data['tarifas'] = tarifas
            extracted_data['ingresos'] = ingresos
            extracted_data['egresos'] = egresos
            extracted_data['control_boletos'] = control_boletos
            
            # Información general de la planilla
            extracted_data['info_general'] = {
                'ciudad_origen': fields.get('Ciudad Origen', {}).get('valueString', ''),
                'ciudad_retorno': fields.get('Ciudad Retorno', {}).get('valueString', ''),
                'fecha': fields.get('Fecha', {}).get('valueDate', ''),
                'numero_planilla': fields.get('Nro Planilla', {}).get('valueString', ''),
                'conductor': fields.get('Nom. Conductor', {}).get('valueString', ''),
                'codigo_conductor': fields.get('Cód. Conductor', {}).get('valueString', ''),
                'asistente': fields.get('Nom. Asistente', {}).get('valueString', ''),
                'codigo_asistente': fields.get('Cód. Asistente', {}).get('valueString', ''),
                'numero_bus': fields.get('Número Bus', {}).get('valueString', ''),
                'patente_bus': fields.get('Patente Bus', {}).get('valueString', ''),
                'horario_origen': fields.get('Horario Horigen', {}).get('valueString', ''),
                'horario_retorno': fields.get('Horario Retorno', {}).get('valueString', '')
            }
            
        except Exception as e:
            logger.error("Error processing planilla data: %s", e)
            extracted_data['processing_error'] = str(e)
        
        return extracted_data
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Probar la conexión con Azure Form Recognizer.
        
        Returns:
            Dict con el resultado de la prueba
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Azure Form Recognizer not configured',
                'endpoint': self.endpoint,
                'key_configured': bool(self.key)
            }

        # Validación ligera: cliente inicializado y credenciales presentes
        return {
            'success': True,
            'message': 'Azure Form Recognizer client configured',
            'endpoint': self.endpoint,
            'key_configured': True
        }


# Instancia global del servicio
azure_service = AzureFormRecognizerService()
