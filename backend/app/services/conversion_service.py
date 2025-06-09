from typing import List, Dict, Any
import json
import csv
import io
import logging
from ..models import NistDataRequest

logger = logging.getLogger(__name__)

class ConversionService:
    def convert_data(self, data: List[Dict[str, Any]], request: NistDataRequest) -> List[Dict[str, Any]]:
        """
        Convierte los datos al formato especificado.
        
        Args:
            data: Lista de diccionarios con los datos a convertir
            request: Objeto NistDataRequest con los parámetros de conversión
            
        Returns:
            Lista de diccionarios con los datos convertidos
        """
        try:
            if request.output_format.lower() == 'csv':
                return self._convert_to_csv(data, request)
            else:
                return self._convert_to_json(data, request)
        except Exception as e:
            logger.error(f"Error en la conversión de datos: {str(e)}")
            raise

    def _convert_to_csv(self, data: List[Dict[str, Any]], request: NistDataRequest) -> List[Dict[str, Any]]:
        """Convierte los datos a formato CSV."""
        if not data:
            return []

        # Obtener todas las claves posibles de los datos
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())

        # Crear un buffer para el CSV
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=sorted(fieldnames),
            delimiter=request.custom_delimiter if request.custom_delimiter else ','
        )
        
        writer.writeheader()
        writer.writerows(data)
        
        return [{'csv_data': output.getvalue()}]

    def _convert_to_json(self, data: List[Dict[str, Any]], request: NistDataRequest) -> List[Dict[str, Any]]:
        """Convierte los datos a formato JSON."""
        if request.pretty_json:
            return [json.dumps(data, indent=2)]
        return [json.dumps(data)] 