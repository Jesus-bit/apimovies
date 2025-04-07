# app/models/session.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime, nullable=False, default=datetime.now())
    is_active = Column(Boolean, default=True)

    video_sessions = relationship("VideoSession", back_populates="session")
    pdf_sessions = relationship("PDFSession", back_populates="session")
    # Relaciones
    user = relationship("User", back_populates="sessions")
    video_histories = relationship("UserVideoHistory", back_populates="session")