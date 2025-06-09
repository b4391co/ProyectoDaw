from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NistDataRequest(BaseModel):
    """
    Modelo para la solicitud de datos al NIST.
    """
    start_date: datetime = Field(..., description="Fecha de inicio de la búsqueda")
    end_date: datetime = Field(..., description="Fecha de fin de la búsqueda")
    search_term: Optional[str] = Field(None, description="Término de búsqueda general")
    keywords: Optional[List[str]] = Field(default=[], description="Lista de palabras clave para filtrar")
    severity: Optional[str] = Field(None, description="Nivel de severidad para filtrar (critical, high, medium, low)")
    format: str = Field(..., description="Formato de salida (json o csv)")

class NistDataResponse(BaseModel):
    """
    Modelo para la respuesta de datos del NIST.
    """
    data: List[Dict[str, Any]] = Field(..., description="Datos obtenidos del NIST")
    metadata: Dict[str, Any] = Field(..., description="Metadatos de la respuesta")
    timestamp: datetime = Field(..., description="Fecha y hora de la respuesta")

class ErrorResponse(BaseModel):
    """
    Modelo para respuestas de error.
    """
    error: str = Field(..., description="Tipo de error")
    detail: str = Field(..., description="Detalles del error")
    status_code: int = Field(..., description="Código de estado HTTP")

class ConversionHistory(BaseModel):
    """
    Modelo para el historial de conversiones.
    """
    id: str = Field(..., description="ID único de la conversión")
    request: NistDataRequest = Field(..., description="Solicitud original")
    response: NistDataResponse = Field(..., description="Respuesta del NIST")
    status: str = Field(..., description="Estado de la conversión (success/error)")
    file_path: Optional[str] = Field(None, description="Ruta del archivo generado")
    error: Optional[ErrorResponse] = Field(None, description="Detalles del error si ocurrió alguno")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha y hora de la conversión") 