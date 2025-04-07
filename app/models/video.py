# app/models/video.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.db.database import Base
from app.models.video_category import VideoCategory
from app.models.video_chunk import VideoChunk

class OrientationType(str, PyEnum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"

class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category_name = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Integer, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    thumbnail_url = Column(String, nullable=False)
    video_url = Column(String, nullable=False)
    orientation = Column(
        Enum(OrientationType),
        nullable=False,
        default=OrientationType.HORIZONTAL,
        server_default=OrientationType.HORIZONTAL.value
    )
    elo = Column(Integer, default=1500)
    
    ratings = relationship("MovieRating", back_populates="video")
    reels = relationship("Reel", back_populates="video")
    video_sessions = relationship("VideoSession", back_populates="video")
    view_histories = relationship("UserVideoHistory", back_populates="video")
    video_categories = relationship("VideoCategory", back_populates="video")
    chunks = relationship("VideoChunk", back_populates="video", cascade="all, delete-orphan")