# app/schemas/video_actor.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class VideoActorBase(BaseModel):
    video_id: int
    actor_id: int
    # Agrega aquí otros campos relevantes para tu VideoActor

class VideoActorCreate(VideoActorBase):
    pass

class VideoActorUpdate(BaseModel):
    video_id: Optional[int] = None
    actor_id: Optional[int] = None
    # Agrega aquí otros campos que se puedan actualizar, todos opcionales

class VideoActor(VideoActorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)