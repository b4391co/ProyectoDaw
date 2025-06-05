from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .models import NistDataRequest, NistDataResponse, ErrorResponse
from .nist_api import NistAPIClient
from .converters import DataConverter

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
converter = DataConverter()

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

@app.post("/api/nist/data")
async def get_nist_data(
    request: NistDataRequest,
    pretty: bool = Query(False, description="Formatear JSON con indentación"),
    delimiter: str = Query(',', description="Delimitador para CSV")
):
    """
    Endpoint para obtener datos del NIST y convertirlos al formato especificado.
    
    Args:
        request: Parámetros de la solicitud
        pretty: Si es True, formatea el JSON con indentación
        delimiter: Delimitador para archivos CSV
    """
    try:
        response = await nist_client.fetch_data(request)
        
        # Convertir los datos al formato especificado
        converted_data = converter.convert(
            response.data,
            request.format,
            pretty=pretty,
            delimiter=delimiter
        )
        
        if request.format.lower() == "csv":
            return Response(
                content=converted_data,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=nist_data_{converter.format_datetime(response.timestamp)}.csv"
                }
            )
        else:
            return Response(
                content=converted_data,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=nist_data_{converter.format_datetime(response.timestamp)}.json"
                }
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Error de formato", "detail": str(e)}
        )
    except ErrorResponse as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error, "detail": e.detail}
        )