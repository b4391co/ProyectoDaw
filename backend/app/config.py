from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno.
    """
    # Configuración general
    APP_NAME: str = "NistDataConverter"
    DEBUG: bool = True
    
    # Configuración de la API NIST
    NIST_API_BASE_URL: str = "https://data.nist.gov/od/ds/ark:/88434/mds2-"
    NIST_API_TIMEOUT: int = 30
    
    # Configuración de CORS
    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Usa lru_cache para cachear la configuración y evitar múltiples lecturas del archivo .env
    """
    return Settings()