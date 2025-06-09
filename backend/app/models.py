from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class NistDataRequest(BaseModel):
    """
    Modelo para la solicitud de datos al NIST.
    """
    start_date: str = Field(..., description="Fecha de inicio en formato ISO")
    end_date: str = Field(..., description="Fecha de fin en formato ISO")
    search_term: Optional[str] = Field(None, description="Término de búsqueda")
    keywords: Optional[List[str]] = Field(default=[], description="Lista de palabras clave")
    severity: Optional[str] = Field(None, description="Nivel de severidad (critical, high, medium, low)")
    output_format: Optional[str] = Field("json", description="Formato de salida (json/csv)")
    pretty_json: Optional[bool] = Field(False, description="Formatear JSON con indentación")
    custom_delimiter: Optional[str] = Field(",", description="Delimitador personalizado para CSV")

class NistDataResponse(BaseModel):
    """
    Modelo para la respuesta de datos del NIST.
    """
    data: List[Dict[str, Any]] = Field(..., description="Datos obtenidos de la API")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadatos adicionales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")

class ErrorResponse(BaseModel):
    """
    Modelo para respuestas de error.
    """
    error: str = Field(..., description="Tipo de error")
    detail: str = Field(..., description="Descripción detallada del error")
    status_code: int = Field(..., description="Código de estado HTTP")

class ConversionHistory(BaseModel):
    """
    Modelo para el historial de conversiones.
    """
    id: str = Field(..., description="ID único de la conversión")
    start_date: str = Field(..., description="Fecha de inicio")
    end_date: str = Field(..., description="Fecha de fin")
    search_term: Optional[str] = Field(None, description="Término de búsqueda")
    output_format: str = Field(..., description="Formato de salida")
    pretty_json: bool = Field(False, description="JSON formateado")
    custom_delimiter: str = Field(",", description="Delimitador CSV")
    keywords: Optional[List[str]] = Field(default=[], description="Palabras clave")
    severity: Optional[str] = Field(None, description="Nivel de severidad")
    status: str = Field(..., description="Estado de la conversión")
    error: Optional[ErrorResponse] = Field(None, description="Error si ocurrió")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la conversión") 