from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Session
from app.db.database import Base
from app.models.categories import Category
# Schema for video_categories table

class VideoCategory(Base):
    __tablename__ = 'video_categories'
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="videos")
    video = relationship("VideoModel", back_populates="video_categories")