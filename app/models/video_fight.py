# app/models/video_fight.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class VideoFight(Base):
    __tablename__ = 'video_fight'

    fight_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_1_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    video_2_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    winner_video = Column(Integer, ForeignKey("videos.id"), nullable=True)
    fight_date = Column(DateTime, default=datetime.now)

    # Relaciones opcionales si se usa SQLAlchemy ORM
    user = relationship("User", back_populates="fights")
    video_1 = relationship("VideoModel", foreign_keys=[video_1_id])
    video_2 = relationship("VideoModel", foreign_keys=[video_2_id])
    winner = relationship("VideoModel", foreign_keys=[winner_video])