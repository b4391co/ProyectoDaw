from fastapi import FastAPI, HTTPException, Response, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .config import get_settings
from .models import NistDataRequest, NistDataResponse, ErrorResponse, ConversionHistory
from .nist_api import NistAPIClient
from .converters import DataConverter
from .database import save_conversion_history, get_conversion_history, get_conversion_by_id
import uuid
from datetime import datetime
from typing import List, Optional

settings = get_settings()
app = FastAPI(
    title="NistDataConverter API",
    description="API para convertir y exportar datos del NIST a formatos JSON y CSV",
    version="1.0.0"
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

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
async def root(request: Request):
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/history")
async def history_page(request: Request):
    """
    Página del historial de conversiones.
    """
    return templates.TemplateResponse("history.html", {"request": request})

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
    conversion_id = str(uuid.uuid4())
    try:
        response = await nist_client.fetch_data(request)
        
        # Convertir los datos al formato especificado
        converted_data = converter.convert(
            response.data,
            request.format,
            pretty=pretty,
            delimiter=delimiter
        )
        
        # Guardar en el historial
        history = ConversionHistory(
            id=conversion_id,
            request=request,
            response=response,
            status="success",
            file_path=f"nist_data_{converter.format_datetime(response.timestamp)}.{request.format.lower()}"
        )
        save_conversion_history(history)
        
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
        error = ErrorResponse(
            error="Error de formato",
            detail=str(e),
            status_code=400
        )
        history = ConversionHistory(
            id=conversion_id,
            request=request,
            response=NistDataResponse(data=[], metadata={}, timestamp=datetime.now()),
            status="error",
            error=error
        )
        save_conversion_history(history)
        raise HTTPException(
            status_code=400,
            detail={"error": "Error de formato", "detail": str(e)}
        )
    except ErrorResponse as e:
        history = ConversionHistory(
            id=conversion_id,
            request=request,
            response=NistDataResponse(data=[], metadata={}, timestamp=datetime.now()),
            status="error",
            error=e
        )
        save_conversion_history(history)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.error, "detail": e.detail}
        )

@app.get("/api/history", response_model=List[ConversionHistory])
async def list_conversion_history(
    skip: int = Query(0, description="Número de registros a saltar"),
    limit: int = Query(10, description="Número máximo de registros a devolver"),
    status: Optional[str] = Query(None, description="Filtrar por estado (success/error)")
):
    """
    Endpoint para obtener el historial de conversiones.
    
    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros a devolver
        status: Filtrar por estado (success/error)
    """
    return get_conversion_history(skip=skip, limit=limit, status=status)

@app.get("/api/history/{conversion_id}", response_model=ConversionHistory)
async def get_conversion_history_by_id(conversion_id: str):
    """
    Endpoint para obtener una conversión específica por su ID.
    
    Args:
        conversion_id: ID de la conversión
    """
    history = get_conversion_by_id(conversion_id)
    if not history:
        raise HTTPException(
            status_code=404,
            detail={"error": "Conversión no encontrada"}
        )
    return history