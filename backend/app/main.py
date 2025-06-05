from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .models import NistDataRequest, NistDataResponse, ErrorResponse
from .nist_api import NistAPIClient

settings = get_settings()
app = FastAPI(
    title="NistDataConverter API",
    description="API para convertir y exportar datos del NIST a formatos JSON y CSV",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del cliente NIST
nist_client = NistAPIClient()

@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {
        "mensaje": "Bienvenido a NistDataConverter API",
        "estado": "activo"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de salud de la API.
    """
    return {
        "estado": "saludable",
        "version": "1.0.0"
    }

@app.post("/api/nist/data", response_model=NistDataResponse)
async def get_nist_data(request: NistDataRequest):
    """
    Endpoint para obtener datos del NIST.
    """
    try:
        response = await nist_client.fetch_data(request)
        return response
    except ErrorResponse as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error, "detail": e.detail}
        )