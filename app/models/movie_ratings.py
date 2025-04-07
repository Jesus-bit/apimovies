# app/models/movie_rating.py
from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging
# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    rating = Column(DECIMAL(3, 1), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    video = relationship("VideoModel", back_populates="ratings", lazy='selectin')
    user = relationship("User", back_populates="movie_ratings")
    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating_range'),
    )

    @classmethod
    def get_multi(cls, db, *, skip: int = 0, limit: int = 100) -> List["MovieRating"]:
        """
        Obtiene múltiples calificaciones con paginación
        """
        try:
            return db.query(cls).offset(skip).limit(limit).all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving ratings: {str(e)}"
            )

    @classmethod
    def validate_ids(cls, db, user_id: int, video_id: int):
        from app.models.video import VideoModel  # Importación local para evitar circular imports
        from app.models.user import User  # Importación local para evitar circular imports

        # Validar si existe el video
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with id {video_id} not found"
            )

        # Validar si existe el usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        # Opcional: Validar si ya existe un rating para este usuario y video
        existing_rating = db.query(cls).filter(
            cls.user_id == user_id,
            cls.video_id == video_id
        ).first()
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rating already exists for user {user_id} and video {video_id}"
            )

    @classmethod
    def create(cls, db, *, obj_in):
        try:
            data = obj_in.dict()
            # Convertir movie_id a video_id si existe en el input
            if 'movie_id' in data:
                data['video_id'] = data.pop('movie_id')

            # Validar IDs antes de crear
            cls.validate_ids(db, data['user_id'], data['video_id'])
            
            db_obj = cls(**data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided. Please check user_id and video_id exist."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @classmethod
    def validate_ids(cls, db, user_id: int, video_id: int, current_rating_id: Optional[int] = None):
        """
        Valida los IDs pero permite la actualización del rating actual
        """
        existing_rating = db.query(cls).filter(
            cls.user_id == user_id,
            cls.video_id == video_id,
            cls.id != current_rating_id  # Ignorar el rating actual en la validación
        ).first()
        
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rating already exists for user {user_id} and video {video_id}"
            )

    @classmethod
    def update(cls, db, *, db_obj, obj_in) -> "MovieRating":
        """
        Actualiza una calificación existente
        """
        try:
            obj_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in

            # Convertir movie_id a video_id si existe en el input
            if 'movie_id' in obj_data:
                obj_data['video_id'] = obj_data.pop('movie_id')

            # Validar IDs si se están actualizando, pasando el ID actual
            if 'user_id' in obj_data or 'video_id' in obj_data:
                cls.validate_ids(
                    db,
                    obj_data.get('user_id', db_obj.user_id),
                    obj_data.get('video_id', db_obj.video_id),
                    current_rating_id=db_obj.id  # Pasar el ID actual para ignorarlo en la validación
                )
            
            # Actualizar atributos
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided. Please check user_id and video_id exist."
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating rating: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating the rating."
            )

    @classmethod
    def get(cls, db, *, id: int) -> Optional["MovieRating"]:
        """
        Obtiene una calificación por su ID
        """
        try:
            return db.query(cls).filter(cls.id == id).first()
        except Exception as e:
            logger.error(f"Error retrieving rating: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving the rating."
            )
    @classmethod
    def get_latest_by_video_id(cls, db, *, video_id: int) -> Optional["MovieRating"]:
        """
        Obtiene la calificación más reciente por video_id
        """
        try:
            return db.query(cls).filter(cls.video_id == video_id).order_by(cls.timestamp.desc()).first()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving latest rating: {str(e)}"
            )