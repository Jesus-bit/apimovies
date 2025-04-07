from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class OrientationType(str, Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"

class VideoBase(BaseModel):
    title: str
    description: str
    category_name: str
    duration: int
    thumbnail_url: str
    video_url: str
    elo: int = 1500  # Agregamos el nuevo campo con valor predeterminado

class VideoCreate(VideoBase):
    pass  # No hay campos adicionales necesarios para crear un video

class Video(VideoBase):
    id: int
    upload_date: datetime
    views: int
    likes: int
    dislikes: int
    orientation: OrientationType

    model_config = ConfigDict(from_attributes=True)

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    orientation: Optional[OrientationType] = None
    elo: Optional[int] = 1500  # Nuevo campo para actualización

    model_config = ConfigDict(from_attributes=True)
