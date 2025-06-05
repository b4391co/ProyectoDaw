import csv
import io
import json
from typing import List, Dict, Any, Union
from datetime import datetime

class DataConverter:
    """
    Clase para convertir datos entre diferentes formatos.
    """
    @staticmethod
    def to_csv(data: List[Dict[str, Any]], delimiter: str = ',') -> str:
        """
        Convierte una lista de diccionarios a formato CSV.
        
        Args:
            data: Lista de diccionarios con los datos a convertir
            delimiter: Carácter delimitador para el CSV (por defecto ',')
            
        Returns:
            str: Datos en formato CSV
        """
        if not data:
            return ""
            
        # Crear un buffer en memoria para el CSV
        output = io.StringIO()
        
        # Obtener las cabeceras del primer elemento
        fieldnames = data[0].keys()
        
        # Crear el escritor CSV
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def to_json(data: List[Dict[str, Any]], pretty: bool = False) -> str:
        """
        Convierte una lista de diccionarios a formato JSON.
        
        Args:
            data: Lista de diccionarios con los datos a convertir
            pretty: Si es True, formatea el JSON con indentación
            
        Returns:
            str: Datos en formato JSON
        """
        if not data:
            return "[]"
            
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)
        
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Formatea una fecha y hora a string ISO.
        
        Args:
            dt: Objeto datetime a formatear
            
        Returns:
            str: Fecha y hora formateada
        """
        return dt.isoformat()
        
    @staticmethod
    def convert(data: List[Dict[str, Any]], format: str, **kwargs) -> str:
        """
        Convierte los datos al formato especificado.
        
        Args:
            data: Lista de diccionarios con los datos a convertir
            format: Formato de salida ('csv' o 'json')
            **kwargs: Argumentos adicionales para la conversión
            
        Returns:
            str: Datos en el formato especificado
            
        Raises:
            ValueError: Si el formato no es soportado
        """
        format = format.lower()
        if format == 'csv':
            return DataConverter.to_csv(data, **kwargs)
        elif format == 'json':
            return DataConverter.to_json(data, **kwargs)
        else:
            raise ValueError(f"Formato no soportado: {format}") 