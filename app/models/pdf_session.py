# app/models/pdf_session.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class PDFSession(Base):
    __tablename__ = "pdf_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pdf_id = Column(Integer, ForeignKey("pdfs.id"), nullable=False)
    pdf_url = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    page_read = Column(Integer, default=1)
    session_id = Column(Integer, ForeignKey("sessions.id"))

    user = relationship("User", back_populates="pdf_sessions")
    pdf = relationship("PDF", back_populates="pdf_sessions")
    session = relationship("Session", back_populates="pdf_sessions")

    @classmethod
    def create(cls, db, *, obj_in):
        db_obj = cls(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @classmethod
    def get(cls, db, id):
        return db.query(cls).filter(cls.id == id).first()

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