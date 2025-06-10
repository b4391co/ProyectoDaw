from typing import List, Dict, Any
import aiohttp
import logging
from ..models import NistDataRequest
from ..config import get_settings
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests

logger = logging.getLogger(__name__)
settings = get_settings()

class NistService:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = settings.NIST_API_KEY
        self.headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"Servicio NIST inicializado con URL base: {self.base_url}")
        logger.info(f"API Key presente: {bool(self.api_key)}")

    async def search_vulnerabilities(self, start_date: str, end_date: str, search_term: str = None, 
                                   severity: str = None):
        try:
            # Construir los parámetros de búsqueda
            params = {
                "pubStartDate": f"{start_date}T00:00:00.000",
                "pubEndDate": f"{end_date}T23:59:59.999",
                "resultsPerPage": 2000  # Límite de la API NIST
            }

            # Añadir término de búsqueda si existe
            if search_term:
                params["keywordSearch"] = search_term

            # Añadir severidad si existe (solo CVSS v3)
            if severity:
                params["cvssV3Severity"] = severity.upper()

            logger.info(f"Realizando búsqueda con parámetros: {params}")
            
            # Realizar la petición a la API
            response = requests.get(
                f"{self.base_url}/cves/search",
                headers=self.headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Búsqueda exitosa. Total de resultados: {data.get('totalResults', 0)}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la búsqueda: {str(e)}")
            raise Exception(f"Error al buscar vulnerabilidades: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise Exception(f"Error inesperado: {str(e)}")

    async def fetch_data(self, request: NistDataRequest) -> List[Dict[str, Any]]:
        """
        Obtiene datos de vulnerabilidades del NIST.
        
        Args:
            request: Parámetros de la solicitud
            
        Returns:
            Lista de vulnerabilidades encontradas
        """
        try:
            logger.info("Iniciando búsqueda en NIST")
            
            if not self.api_key:
                raise Exception("No se ha configurado la clave API de NIST")
            
            # Construir la URL de la API
            url = f"{self.base_url}/"
            
            # Preparar los parámetros de la búsqueda
            params = {
                "lastModStartDate": f"{request.start_date}T13:00:00.000+01:00",
                "lastModEndDate": f"{request.end_date}T13:36:00.000+01:00",
                "resultsPerPage": 2000
            }
            
            if request.severity:
                params["cvssV3Severity"] = request.severity.upper()
                
            if request.search_term:
                params["keywordSearch"] = request.search_term

            # Construir la URL completa con los parámetros
            full_url = f"{url}?{urlencode(params)}"
            logger.info(f"URL de la petición: {full_url}")
            
            headers = {
                "Accept": "application/json",
                "apiKey": self.api_key
            }
            
            timeout = aiohttp.ClientTimeout(total=settings.NIST_API_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params, headers=headers) as response:
                    logger.info(f"Status code: {response.status}")
                    
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Error en la respuesta de NIST API: {error_text}")
                        try:
                            error_data = await response.json()
                            error_message = error_data.get('message', error_text)
                        except:
                            error_message = error_text
                        raise Exception(f"Error en la API de NIST: {error_message}")
                    
                    data = await response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    total_results = data.get("totalResults", 0)
                    logger.info(f"Vulnerabilidades encontradas: {len(vulnerabilities)} de {total_results} totales")
                    return vulnerabilities
                    
        except Exception as e:
            logger.error(f"Error al obtener datos de NIST: {str(e)}")
            raise Exception(f"Error al obtener datos de NIST: {str(e)}") 