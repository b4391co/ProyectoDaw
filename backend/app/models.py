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