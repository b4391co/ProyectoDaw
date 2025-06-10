from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class NistDataRequest(BaseModel):
    """
    Modelo para la solicitud de datos al NIST.
    """
    start_date: str = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    end_date: str = Field(..., description="Fecha de fin en formato YYYY-MM-DD")
    severity: Optional[str] = Field(None, description="Severidad (LOW, MEDIUM, HIGH, CRITICAL)")
    search_term: Optional[str] = Field(None, description="Término de búsqueda")
    keywords: List[str] = Field(default_factory=list, description="Lista de palabras clave")

class NistDataResponse(BaseModel):
    """
    Modelo para la respuesta de la API de NIST.
    """
    vulnerabilities: List[dict] = Field(..., description="Lista de vulnerabilidades")
    total_results: int = Field(..., description="Número total de resultados")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta") 