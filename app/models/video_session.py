# app/models/video_session.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Union
from app.schemas.video_session import VideoSessionCreate, VideoSessionUpdate

class VideoSession(Base):
    __tablename__ = "video_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))

    video = relationship("VideoModel", back_populates="video_sessions")
    session = relationship("Session", back_populates="video_sessions")
    

    @classmethod
    def create(cls, db: Session, obj_in: VideoSessionCreate) -> "VideoSession":
        db_obj = cls(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get(cls, db: Session, id: int) -> Union["VideoSession", None]:
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_multi(cls, db: Session, skip: int = 0, limit: int = 100) -> List["VideoSession"]:
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def update(cls, db: Session, db_obj: "VideoSession", obj_in: Union[VideoSessionUpdate, Dict[str, Any]]) -> "VideoSession":
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def remove(cls, db: Session, id: int) -> "VideoSession":
        obj = db.query(cls).get(id)
        db.delete(obj)
        db.commit()
        return obj