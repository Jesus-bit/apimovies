from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from app.db.database import Base
from typing import Dict, Any, Optional, Union
from fastapi.encoders import jsonable_encoder

class UserVideoHistory(Base):
    __tablename__ = 'user_video_history'

    history_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    view_date = Column(DateTime, default=datetime.now)
    progress = Column(Integer, nullable=False)
    watched_full = Column(Boolean, default=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    last_update = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    user = relationship("User", back_populates="video_histories")
    video = relationship("VideoModel", back_populates="view_histories")
    session = relationship("Session", back_populates="video_histories")

    @classmethod
    def get(cls, db: Session, id: int) -> Optional["UserVideoHistory"]:
        """Obtiene un registro por su ID"""
        return db.query(cls).filter(cls.history_id == id).first()

    @classmethod
    def get_multi(cls, db: Session, *, skip: int = 0, limit: int = 100) -> list["UserVideoHistory"]:
        """Obtiene múltiples registros con paginación"""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get_multi_by_filters(cls, db: Session, *, filters: dict, skip: int = 0, limit: int = 100) -> list["UserVideoHistory"]:
        """Obtiene múltiples registros aplicando filtros"""
        query = db.query(cls)
        for field, value in filters.items():
            if value is not None:
                query = query.filter(getattr(cls, field) == value)
        return query.offset(skip).limit(limit).all()

    @classmethod
    def create(cls, db: Session, *, obj_in: Dict[str, Any]) -> "UserVideoHistory":
        """Crea un nuevo registro"""
        obj_in_data = obj_in.copy()
        db_obj = cls(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def update(cls, db: Session, *, db_obj: "UserVideoHistory", obj_in: Union[Dict[str, Any], Any]) -> "UserVideoHistory":
        """Actualiza un registro existente"""
        obj_data = jsonable_encoder(db_obj)
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def remove(cls, db: Session, *, id: int) -> "UserVideoHistory":
        """Elimina un registro"""
        obj = db.query(cls).get(id)
        db.delete(obj)
        db.commit()
        return obj

    @classmethod
    def get_by_user_and_video(cls, db: Session, *, user_id: int, video_id: int) -> Optional["UserVideoHistory"]:
        """Obtiene el historial de un usuario para un video específico"""
        return db.query(cls).filter(
            cls.user_id == user_id,
            cls.video_id == video_id
        ).first()

    @classmethod
    def get_user_history(cls, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> list["UserVideoHistory"]:
        """Obtiene todo el historial de un usuario"""
        return db.query(cls).filter(
            cls.user_id == user_id
        ).offset(skip).limit(limit).all()

    @classmethod
    def get_latest_by_video(cls, db: Session, video_id: int) -> Optional["UserVideoHistory"]:
        """
        Obtiene el registro más reciente de progreso para un video específico.
        """
        return (
            db.query(cls)
            .filter(cls.video_id == video_id)
            .order_by(cls.last_update.desc())
            .first()
        )
