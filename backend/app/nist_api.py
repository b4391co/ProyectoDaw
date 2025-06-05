import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
from .config import get_settings
from .models import NistDataRequest, NistDataResponse, ErrorResponse

settings = get_settings()

class NistAPIClient:
    """
    Cliente para interactuar con la API de NIST.
    """
    def __init__(self):
        self.base_url = settings.NIST_API_BASE_URL
        self.timeout = settings.NIST_API_TIMEOUT

    async def fetch_data(self, request: NistDataRequest) -> NistDataResponse:
        """
        Obtiene datos del NIST basados en los parámetros de la solicitud.
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construir la URL con los parámetros de búsqueda
                params = {
                    "start_date": request.start_date.isoformat(),
                    "end_date": request.end_date.isoformat()
                }
                if request.search_term:
                    params["search"] = request.search_term

                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        raise ErrorResponse(
                            error="Error en la API de NIST",
                            detail=await response.text(),
                            status_code=response.status
                        )

                    data = await response.json()
                    return NistDataResponse(
                        data=data.get("results", []),
                        metadata={
                            "total_results": data.get("total", 0),
                            "page": data.get("page", 1),
                            "per_page": data.get("per_page", 10)
                        }
                    )

        except aiohttp.ClientError as e:
            raise ErrorResponse(
                error="Error de conexión con NIST",
                detail=str(e),
                status_code=500
            )
        except Exception as e:
            raise ErrorResponse(
                error="Error inesperado",
                detail=str(e),
                status_code=500
            ) 