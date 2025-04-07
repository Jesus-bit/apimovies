from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from sqlalchemy import func, and_
from typing import List
from app.models.user_video_history import UserVideoHistory as UserVideoHistoryModel
from app.models.session import Session as SessionModel
from app.schemas.user_video_history import UserVideoHistoryCreate, UserVideoHistoryUpdate
from app.db.crud_base import CRUDBase
from fastapi import HTTPException
import logging

class UserVideoHistoryService:
    def __init__(self, model: UserVideoHistoryModel):
        self.crud = CRUDBase(model)
    def get_all_video_histories(self, db: Session, video_id: int) -> List[UserVideoHistoryModel]:
        """
        Obtiene todos los registros de historial de un video específico.
        
        **Parámetros**
        - `db`: Sesión de base de datos
        - `video_id`: ID del video
        
        **Retorna**
        - Lista de todos los registros de historial del video
        """
        try:
            return (
                db.query(UserVideoHistoryModel)
                .filter(UserVideoHistoryModel.video_id == video_id)
                .order_by(UserVideoHistoryModel.last_update.desc())
                .all()
            )
        except Exception as e:
            logging.error(f"Error retrieving all video histories for video ID {video_id}: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error retrieving all video histories for the video"
            )
    def validate_session(self, db: Session, session_id: Optional[int]) -> bool:
        """
        Valida que la sesión exista si se proporciona un session_id.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `session_id`: ID de la sesión a validar
        
        **Retorna**
        
        * Booleano indicando si la sesión es válida
        """
        if session_id is not None:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            return session is not None
        return True

    def create_video_history(self, 
                              db: Session, 
                              user_video_history: UserVideoHistoryCreate
    ):
        """
        Crea un nuevo registro de historial de video.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `user_video_history`: Datos para crear el historial
        
        **Retorna**
        
        * Registro de historial de video creado
        """
        # Validar sesión
        if not self.validate_session(db, user_video_history.session_id):
            raise HTTPException(
                status_code=404,
                detail=f"Session with id {user_video_history.session_id} not found"
            )
        # Añadir timestamp de creación
        user_video_history_dict = user_video_history.model_dump()
        user_video_history_dict["last_update"] = datetime.now()
        return self.crud.create(db, obj_in=user_video_history_dict)

    def get_latest_video_progress(self, 
                                   db: Session, 
                                   video_id: int
    ):
        """
        Obtiene el último progreso de un video.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `video_id`: ID del video
        
        **Retorna**
        
        * Último registro de progreso si existe, sino None
        """
        existing_progress = UserVideoHistoryModel.get_latest_by_video(db=db, video_id=video_id)
        return (
            db.query(UserVideoHistoryModel)
            .filter_by(video_id=video_id)
            .order_by(UserVideoHistoryModel.last_update.desc())
            .first()
        )

    def update_video_progress(self, 
                               db: Session, 
                               video_id: int, 
                               update_data: UserVideoHistoryUpdate, 
                               session_id: int
    ):
        """
        Actualiza o crea el progreso de un video.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `video_id`: ID del video
        * `update_data`: Datos de actualización
        * `session_id`: ID de la sesión actual
        
        **Retorna**
        
        * Registro de historial de video actualizado o creado
        """
        
        logging.info(
            f"Update video progress - Video ID: {video_id}, "
            f"Session: {session_id}, Watched Full: {update_data.watched_full}"
        )
        # Buscar el último progreso del video
        existing_progress = self.get_latest_video_progress(db, video_id)
        # Si ya existe un progreso
        if existing_progress:
            # Si pertenece a otra sesión, crear uno nuevo
            if existing_progress.session_id != session_id:
                
                return self.create_new_progress(
                    db, 
                    video_id=video_id, 
                    update_data=update_data, 
                    session_id=session_id
                )
            # Si pertenece a la misma sesión, actualizar
            return self.update_existing_progress(
                db, 
                existing_progress=existing_progress, 
                update_data=update_data
            )
        
        # Si no hay progreso previo, crear uno nuevo
        return self.create_new_progress(
            db, 
            video_id=video_id, 
            update_data=update_data, 
            session_id=session_id
        )


    def create_new_progress(self, 
                         db: Session, 
                         video_id: int, 
                         update_data: UserVideoHistoryUpdate, 
                         session_id: int
        ):
        try:
            # Determine the progress value based on watched_full status
            progress = 0 if update_data.watched_full else (update_data.progress or 0)
            
            # Create the model instance with proper validation
            new_data = UserVideoHistoryCreate(
                user_id=1,  # TODO: Obtain user_id dynamically
                video_id=video_id,
                progress=progress,
                watched_full=update_data.watched_full or False,
                session_id=session_id,
                last_update=datetime.now(),
                view_date=datetime.now()
            )
            
            # Log the progress update
            logging.info(
                f"Creating new video progress - Video ID: {video_id}, "
                f"Progress: {progress}, Watched Full: {update_data.watched_full}"
            )
            
            # Create the record
            created_record = self.crud.create(db, obj_in=new_data)
            
            return created_record
        
        except Exception as e:
            logging.error(f"Error creating video progress: {str(e)}")
            raise

    def get_unique_latest_video_histories(self, 
                                        db: Session, 
                                        user_id: int, 
                                        skip: int = 0, 
                                        limit: int = 100
    ):
        """
        Obtiene el historial de video más reciente para cada video único de un usuario.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `user_id`: ID del usuario
        * `skip`: Número de registros a saltar (para paginación)
        * `limit`: Número máximo de registros a devolver
        
        **Retorna**
        
        * Lista de los registros de historial de video más recientes por video
        """
        # Subquery para obtener el último registro por video para el usuario
        latest_records_subquery = (
            db.query(
                UserVideoHistoryModel.video_id, 
                func.max(UserVideoHistoryModel.last_update).label('max_last_update')
            )
            .filter(UserVideoHistoryModel.user_id == user_id)
            .group_by(UserVideoHistoryModel.video_id)
            .subquery()
        )

        # Query principal para obtener los registros completos de esos últimos registros
        unique_video_histories = (
            db.query(UserVideoHistoryModel)
            .join(
                latest_records_subquery, 
                and_(
                    UserVideoHistoryModel.video_id == latest_records_subquery.c.video_id,
                    UserVideoHistoryModel.last_update == latest_records_subquery.c.max_last_update
                )
            )
            .filter(UserVideoHistoryModel.user_id == user_id)
            .order_by(UserVideoHistoryModel.last_update.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return unique_video_histories
    def get_recent_video_history(
        self, db: Session, user_id: int, limit: int
    ) -> List[UserVideoHistoryModel]:
        """
        Obtiene los últimos registros del historial de videos para un usuario.
        
        **Parámetros**
        - `db`: Sesión de base de datos
        - `user_id`: ID del usuario
        - `limit`: Número máximo de registros a devolver
        
        **Retorna**
        - Lista de registros de historial de videos
        """
        try:
            return (
                db.query(UserVideoHistoryModel)
                .filter(UserVideoHistoryModel.user_id == user_id)
                .order_by(UserVideoHistoryModel.last_update.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            logging.error(f"Error retrieving video history: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Error retrieving video history"
            )


    def update_existing_progress(self, 
                                  db: Session, 
                                  existing_progress: UserVideoHistoryModel, 
                                  update_data: UserVideoHistoryUpdate
    ):
        """
        Actualiza un progreso de video existente.
        
        **Parámetros**
        
        * `db`: Sesión de base de datos
        * `existing_progress`: Registro de progreso existente
        * `update_data`: Datos de actualización
        
        **Retorna**
        
        * Registro de historial de video actualizado
        """
        update_dict = {
            'last_update': datetime.now()
        }

        if update_data.progress is not None:
            update_dict['progress'] = update_data.progress
        if update_data.watched_full is not None:
            update_dict['watched_full'] = update_data.watched_full

        return self.crud.update(db, db_obj=existing_progress, obj_in=update_dict)