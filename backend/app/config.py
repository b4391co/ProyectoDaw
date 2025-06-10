from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno.
    """
    # Configuración general
    APP_NAME: str = "NIST Vulnerability Scanner"
    DEBUG: bool = True
    
    # Configuración de la API NIST
    NIST_API_BASE_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    NIST_API_KEY: str = os.getenv("NIST_API_KEY", "")
    NIST_API_TIMEOUT: int = 30
    
    # Configuración de CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Usa lru_cache para cachear la configuración y evitar múltiples lecturas del archivo .env
    """
    settings = Settings()
    logger.info(f"Configuración cargada:")
    logger.info(f"- API Key presente: {bool(settings.NIST_API_KEY)}")
    logger.info(f"- URL base: {settings.NIST_API_BASE_URL}")
    logger.info(f"- Timeout: {settings.NIST_API_TIMEOUT}s")
    return settings 