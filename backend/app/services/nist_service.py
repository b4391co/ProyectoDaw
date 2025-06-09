from typing import List, Dict, Any
import aiohttp
import logging
from ..models import NistDataRequest
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NistService:
    def __init__(self):
        self.base_url = settings.NIST_API_BASE_URL
        self.api_key = settings.NIST_API_KEY

    async def fetch_data(self, request: NistDataRequest) -> List[Dict[str, Any]]:
        """
        Obtiene datos de la API de NIST basados en los parámetros de la solicitud.
        
        Args:
            request: Objeto NistDataRequest con los parámetros de búsqueda
            
        Returns:
            Lista de diccionarios con los datos obtenidos
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construir la URL con los parámetros
                params = {
                    'startDate': request.start_date,
                    'endDate': request.end_date,
                    'apiKey': self.api_key
                }
                
                if request.search_term:
                    params['keyword'] = request.search_term
                
                if request.keywords:
                    params['keywords'] = ','.join(request.keywords)
                
                if request.severity:
                    params['severity'] = request.severity

                logger.info(f"Realizando petición a NIST con parámetros: {params}")
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error en la petición a NIST: {error_text}")
                        raise Exception(f"Error en la API de NIST: {error_text}")
                    
                    data = await response.json()
                    logger.info(f"Datos obtenidos de NIST: {len(data)} registros")
                    return data

        except Exception as e:
            logger.error(f"Error al obtener datos de NIST: {str(e)}")
            raise 