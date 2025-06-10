from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class NistDataRequest(BaseModel):
    """
    Modelo para la solicitud de datos al NIST.
    """
    start_date: str = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    end_date: str = Field(..., description="Fecha de fin en formato YYYY-MM-DD")
    search_term: Optional[str] = Field(None, description="Término de búsqueda")
    severity: Optional[str] = Field(None, description="Severidad de la vulnerabilidad (CRITICAL, HIGH, MEDIUM, LOW)")
    output_format: str = Field("json", description="Formato de salida")
    pretty_json: bool = Field(True, description="Formatear JSON de salida")

class NistDataResponse(BaseModel):
    """
    Modelo para la respuesta de la API de NIST.
    """
    vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    total_results: int = Field(0)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    detail: str 