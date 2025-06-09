from sqlalchemy import create_engine, Column, String, DateTime, JSON, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from typing import List, Optional
from .models import ConversionHistory, NistDataRequest, NistDataResponse, ErrorResponse

# Crear la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./nist_converter.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ConversionHistoryDB(Base):
    __tablename__ = "conversion_history"

    id = Column(String, primary_key=True)
    request = Column(JSON)
    response = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String)
    error = Column(JSON, nullable=True)
    file_path = Column(String, nullable=True)

# Crear las tablas
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_conversion_history(history: ConversionHistory) -> None:
    """Guarda una entrada en el historial de conversiones."""
    db = SessionLocal()
    try:
        db_history = ConversionHistoryDB(
            id=history.id,
            request=history.request.dict(),
            response=history.response.dict(),
            created_at=history.created_at,
            status=history.status,
            error=history.error.dict() if history.error else None,
            file_path=history.file_path
        )
        db.add(db_history)
        db.commit()
    finally:
        db.close()

def get_conversion_history(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[ConversionHistory]:
    """Obtiene el historial de conversiones con paginación y filtrado opcional."""
    db = SessionLocal()
    try:
        query = db.query(ConversionHistoryDB)
        
        # Aplicar filtros
        if status:
            query = query.filter(ConversionHistoryDB.status == status)
        
        if search:
            # Buscar en ID o fecha
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    ConversionHistoryDB.id.ilike(search_term),
                    ConversionHistoryDB.created_at.cast(String).ilike(search_term)
                )
            )
        
        db_histories = query.order_by(ConversionHistoryDB.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [
            ConversionHistory(
                id=h.id,
                request=NistDataRequest(**h.request),
                response=NistDataResponse(**h.response),
                created_at=h.created_at,
                status=h.status,
                error=ErrorResponse(**h.error) if h.error else None,
                file_path=h.file_path
            )
            for h in db_histories
        ]
    finally:
        db.close()

def get_conversion_by_id(conversion_id: str) -> Optional[ConversionHistory]:
    """Obtiene una conversión específica por su ID."""
    db = SessionLocal()
    try:
        db_history = db.query(ConversionHistoryDB)\
            .filter(ConversionHistoryDB.id == conversion_id)\
            .first()
        
        if not db_history:
            return None
            
        return ConversionHistory(
            id=db_history.id,
            request=NistDataRequest(**db_history.request),
            response=NistDataResponse(**db_history.response),
            created_at=db_history.created_at,
            status=db_history.status,
            error=ErrorResponse(**db_history.error) if db_history.error else None,
            file_path=db_history.file_path
        )
    finally:
        db.close() 