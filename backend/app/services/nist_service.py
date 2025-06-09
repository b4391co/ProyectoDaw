from typing import List, Dict, Any
import aiohttp
import logging
from ..models import NistDataRequest
from ..config import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()

class NistService:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = settings.NIST_API_KEY

    async def fetch_data(self, request: NistDataRequest):
        try:
            logger.info(f"Iniciando búsqueda en NIST con parámetros: {request}")
            
            # Construir la URL de la API
            url = f"{self.base_url}/cves"
            
            # Preparar los parámetros de la búsqueda
            params = {
                "pubStartDate": f"{request.start_date}T00:00:00.000",
                "pubEndDate": f"{request.end_date}T23:59:59.999",
                "apiKey": self.api_key,
                "resultsPerPage": 20
            }
            
            if request.search_term:
                params["keywordSearch"] = request.search_term
                
            if request.keywords:
                params["keyword"] = ",".join(request.keywords)
                
            if request.severity:
                params["cvssV3Severity"] = request.severity

            logger.info(f"Realizando petición a NIST API: {url}")
            logger.info(f"Parámetros de la petición: {params}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Error en la respuesta de NIST API: {error_text}")
                        raise Exception(f"Error en la API de NIST: {error_text}")
                    
                    data = await response.json()
                    logger.info(f"Respuesta recibida de NIST API: {len(data.get('vulnerabilities', []))} vulnerabilidades")
                    
                    return data.get("vulnerabilities", [])
                    
        except Exception as e:
            logger.error(f"Error al obtener datos de NIST: {str(e)}")
            raise Exception(f"Error al obtener datos de NIST: {str(e)}") 