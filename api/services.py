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
    """
    
    def __init__(self):
        self.endpoint = settings.AZURE_FORM_RECOGNIZER_ENDPOINT
        self.key = settings.AZURE_FORM_RECOGNIZER_KEY
        
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
        Analizar un documento usando Azure Form Recognizer.
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            Dict con los datos extraídos del documento
        """
        if not self.is_configured():
            raise ValueError("Azure Form Recognizer not configured")
        
        try:
            with open(image_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-document", 
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
        Extraer datos estructurados del resultado de Azure Form Recognizer.
        
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
            
            # Procesar datos específicos de planillas
            extracted_data = self._process_planilla_data(extracted_data)
            
            # Guardar resultado completo
            extracted_data['raw_result'] = {
                'pages': len(result.pages) if hasattr(result, 'pages') else 0,
                'tables_count': len(result.tables) if hasattr(result, 'tables') else 0,
                'key_value_pairs_count': len(result.key_value_pairs) if hasattr(result, 'key_value_pairs') else 0
            }
            
        except Exception as e:
            logger.error("Error processing Azure result: %s", e)
            extracted_data['error'] = str(e)
        
        return extracted_data
    
    def _process_planilla_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesar datos específicos de planillas de recaudación.
        
        Args:
            extracted_data: Datos extraídos de Azure
            
        Returns:
            Datos procesados específicos para planillas
        """
        try:
            # Buscar patrones comunes en planillas de recaudación
            texto = extracted_data.get('texto_completo', '').lower()
            
            # Detectar tarifas (patrones comunes)
            tarifa_keywords = ['pasaje', 'tarifa', 'precio', 'boleto', 'ticket']
            for keyword in tarifa_keywords:
                if keyword in texto:
                    # Aquí podrías implementar lógica específica para extraer tarifas
                    pass
            
            # Detectar ingresos
            ingreso_keywords = ['ingreso', 'entrada', 'recaudación', 'venta']
            for keyword in ingreso_keywords:
                if keyword in texto:
                    # Lógica para extraer ingresos
                    pass
            
            # Detectar egresos
            egreso_keywords = ['egreso', 'gasto', 'salida', 'descuento']
            for keyword in egreso_keywords:
                if keyword in texto:
                    # Lógica para extraer egresos
                    pass
            
            # Detectar control de boletos
            control_keywords = ['talonario', 'control', 'inicial', 'final', 'vendido']
            for keyword in control_keywords:
                if keyword in texto:
                    # Lógica para extraer control de boletos
                    pass
            
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
        
        try:
            # Crear un documento de prueba simple
            test_data = b"Test document for Azure Form Recognizer"
            
            # Intentar analizar el documento de prueba
            poller = self.client.begin_analyze_document(
                "prebuilt-document",
                document=test_data
            )
            result = poller.result()
            
            return {
                'success': True,
                'message': 'Azure Form Recognizer connection successful',
                'endpoint': self.endpoint,
                'pages_detected': len(result.pages) if hasattr(result, 'pages') else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'endpoint': self.endpoint,
                'key_configured': bool(self.key)
            }


# Instancia global del servicio
azure_service = AzureFormRecognizerService()
