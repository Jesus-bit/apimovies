# app/models/reel.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Reel(Base):
    __tablename__ = "reels"

    reel_id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


    # Relación con VideoModel
    video = relationship("VideoModel", back_populates="reels", lazy='selectin')

    @classmethod
    def create(cls, db, *, obj_in):
        db_obj = cls(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get(cls, db, id):
        return db.query(cls).filter(cls.reel_id == id).first()

    @classmethod
    def get_multi(cls, db, *, skip=0, limit=100):
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def update(cls, db, *, db_obj, obj_in):
        obj_data = obj_in.dict(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def remove(cls, db, *, id):
        obj = db.query(cls).get(id)
        db.delete(obj)
        db.commit()
        return obj
