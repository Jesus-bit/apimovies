from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core import deps
from typing import List, Optional
from datetime import datetime
from app.services.user_video_history_service import UserVideoHistoryService
from app.models.user_video_history import UserVideoHistory as UserVideoHistoryModel
from app.schemas.user_video_history import UserVideoHistory, UserVideoHistoryCreate, UserVideoHistoryUpdate
from app.models.session import Session as SessionModel


router = APIRouter(prefix="/user_video_history", tags=["user_video_history"])

@router.post("/", response_model=UserVideoHistory)
def create_user_video_history(
    user_video_history: UserVideoHistoryCreate,
    db: Session = Depends(deps.get_db)
):
    # Validar que la sesión existe si se proporciona
    if user_video_history.session_id is not None:
        session = db.query(SessionModel).filter(
            SessionModel.id == user_video_history.session_id
        ).first()
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session with id {user_video_history.session_id} not found"
            )
    # Añadir timestamp de creación
    user_video_history_dict = user_video_history.model_dump()
    user_video_history_dict["last_update"] = datetime.now()
    return UserVideoHistoryModel.create(db=db, obj_in=user_video_history_dict)

@router.get("/{user_id}", response_model=List[UserVideoHistory])
def read_user_video_histories(
    skip: int = 0,
    limit: int = 100,
    user_id: int = 1,
    db: Session = Depends(deps.get_db)
):
    user_video_history_service = UserVideoHistoryService(UserVideoHistoryModel)
    return user_video_history_service.get_unique_latest_video_histories(
        db, 
        user_id=user_id, 
        skip=skip, 
        limit=limit
    )

@router.get("/progress/{video_id}", response_model=UserVideoHistory)
def get_video_progress(
    video_id: int,
    db: Session = Depends(deps.get_db)
):
    user_video_history_service = UserVideoHistoryService(UserVideoHistoryModel)
    # latest_history = UserVideoHistoryModel.get_latest_by_video(db=db, video_id=video_id)
    latest_history = user_video_history_service.get_latest_video_progress(db=db, video_id=video_id)
    if not latest_history:
        raise HTTPException(status_code=404, detail="No progress found")
    
    return latest_history

@router.get("/history/{video_id}", response_model=List[UserVideoHistory])
def get_all_video_history(
    video_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Obtiene todos los registros de historial de un video específico.
    
    **Parámetros**
    - `video_id`: ID del video
    
    **Retorna**
    - Lista de todos los registros de historial del video
    """
    user_video_history_service = UserVideoHistoryService(UserVideoHistoryModel)
    video_histories = user_video_history_service.get_all_video_histories(db=db, video_id=video_id)
    if not video_histories:
        raise HTTPException(status_code=404, detail="No history found for the video")
    return video_histories

@router.post("/progress/{video_id}", response_model=UserVideoHistory)
def update_or_create_video_progress(
    video_id: int,
    update_data: UserVideoHistoryUpdate,
    session_id: int = Depends(deps.get_session_id),
    db: Session = Depends(deps.get_db)
):
    """
    Actualiza o crea un registro de progreso de un video.
    
    Casos de uso:
    1. Si no existe un registro para el video, crea uno nuevo.
    2. Si existe pero pertenece a otra sesión, crea un nuevo registro para la sesión actual.
    3. Si existe y pertenece a la misma sesión, actualiza el progreso.
    
    **Parámetros**
    
    * `video_id`: ID del video a actualizar
    * `update_data`: Datos de actualización del progreso
    * `session_id`: ID de la sesión actual
    * `db`: Sesión de base de datos
    
    **Retorna**
    
    * Registro de historial de video actualizado o creado
    """
    # Import the SQLAlchemy model, not the Pydantic schema
    from app.models.user_video_history import UserVideoHistory as UserVideoHistoryModel
    
    # Initialize the service with the SQLAlchemy model
    video_history_service = UserVideoHistoryService(UserVideoHistoryModel)
    
    try:
        # Call the service method to update or create progress
        updated_progress = video_history_service.update_video_progress(
            db=db, 
            video_id=video_id, 
            update_data=update_data, 
            session_id=session_id
        )
        
        return updated_progress
    
    except HTTPException as e:
        # Manejar cualquier excepción de validación de sesión
        raise e
    except Exception as e:
        # Manejar cualquier otra excepción inesperada
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating video progress: {str(e)}"
        )

@router.get("/{history_id}", response_model=UserVideoHistory)
def read_user_video_history(history_id: int, db: Session = Depends(deps.get_db)):
    history = UserVideoHistoryModel.get(db, id=history_id)
    if history is None:
        raise HTTPException(status_code=404, detail="User video history not found")
    return history

@router.get("/{user_id}/history", response_model=List[UserVideoHistory])
def get_user_video_history(
    user_id: int,
    limit: int = Query(10, ge=1),  # Limitar a 5 por defecto, mínimo 1
    db: Session = Depends(deps.get_db),
):
    """
    Obtiene el historial de videos de un usuario, ordenado por fecha más reciente.
    
    **Parámetros**
    - `user_id`: ID del usuario
    - `limit`: Número máximo de registros a devolver (por defecto 5)
    """
    user_video_history_service = UserVideoHistoryService(UserVideoHistoryModel)
    return user_video_history_service.get_recent_video_history(
        db, user_id=user_id, limit=limit
    )
