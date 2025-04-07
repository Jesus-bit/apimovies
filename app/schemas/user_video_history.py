from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserVideoHistoryBase(BaseModel):
    user_id: int
    video_id: int
    progress: int = 0
    watched_full: bool = False
    session_id: Optional[int] = None
    last_update: Optional[datetime] = None

class UserVideoHistoryCreate(UserVideoHistoryBase):
    pass

class UserVideoHistoryUpdate(BaseModel):
    progress: Optional[int] = None
    watched_full: Optional[bool] = None
    last_update: Optional[datetime] = None
    
    class Config:
        exclude_unset = True  # Solo incluye campos que fueron explícitamente establecidos

class UserVideoHistory(UserVideoHistoryBase):
    history_id: Optional[int] = None
    last_update: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Permite crear desde objetos ORM
        extra='ignore'  # Ignora campos adicionales durante la validación
    )
