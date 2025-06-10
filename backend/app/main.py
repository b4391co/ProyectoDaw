from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .config import get_settings
from .models import NistDataRequest
from .services.nist_service import NistService
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(
    title="NIST Vulnerability Scanner",
    description="API para buscar vulnerabilidades en NIST",
    version="1.0.0"
)

# Configurar el directorio base
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend" / "templates"))

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia del servicio NIST
nist_service = NistService()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("Accediendo a la página principal")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/results", response_class=HTMLResponse)
async def read_results(request: Request):
    logger.info("Accediendo a la página de resultados")
    return templates.TemplateResponse("results.html", {"request": request})

@app.post("/api/search")
async def search_vulnerabilities(request: NistDataRequest):
    try:
        logger.info("Recibida petición de búsqueda")
        vulnerabilities = await nist_service.fetch_data(request)
        logger.info(f"Búsqueda completada: {len(vulnerabilities)} vulnerabilidades encontradas")
        return {"vulnerabilities": vulnerabilities}
    except Exception as e:
        logger.error(f"Error en la búsqueda: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error global: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    ) 