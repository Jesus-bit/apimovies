# app/models/video_actor.py

from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base

class VideoActor(Base):
    __tablename__ = "video_actors"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("actors.id"), nullable=False)
