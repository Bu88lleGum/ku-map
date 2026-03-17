from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.services.pathfinder import PathfinderService

router = APIRouter()

@router.get("/calculate-path")
def calculate_path(
    start_id: int, 
    end_id: int, 
    session: Session = Depends(get_session)
):
    # Инициализируем сервис, передавая ему сессию базы
    service = PathfinderService(session)
    
    # Ищем путь (внутри он сам загрузит граф из БД)
    result = service.find_path(start_id, end_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Путь между узлами не найден")
        
    return result