from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class VideoChunk(Base):
    __tablename__ = 'video_chunks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)
    chunk_start_time = Column(Integer)
    chunk_end_time = Column(Integer)

    video = relationship("VideoModel", back_populates="chunks")
