from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NistDataRequest(BaseModel):
    """
    Modelo para la solicitud de datos al NIST.
    """
    start_date: datetime = Field(..., description="Fecha de inicio para la búsqueda")
    end_date: datetime = Field(..., description="Fecha de fin para la búsqueda")
    search_term: Optional[str] = Field(None, description="Término de búsqueda opcional")
    format: str = Field("json", description="Formato de salida (json o csv)")

class NistDataResponse(BaseModel):
    """
    Modelo para la respuesta de datos del NIST.
    """
    data: List[Dict[str, Any]] = Field(..., description="Datos obtenidos del NIST")
    metadata: Dict[str, Any] = Field(..., description="Metadatos de la respuesta")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")

class ErrorResponse(BaseModel):
    """
    Modelo para respuestas de error.
    """
    error: str = Field(..., description="Mensaje de error")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error")
    status_code: int = Field(..., description="Código de estado HTTP")

class ConversionHistory(BaseModel):
    """
    Modelo para el historial de conversiones.
    """
    id: str = Field(..., description="Identificador único de la conversión")
    request: NistDataRequest = Field(..., description="Solicitud original")
    response: NistDataResponse = Field(..., description="Respuesta del NIST")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha y hora de la conversión")
    status: str = Field(..., description="Estado de la conversión (success/error)")
    error: Optional[ErrorResponse] = Field(None, description="Error si la conversión falló")
    file_path: Optional[str] = Field(None, description="Ruta al archivo generado") 