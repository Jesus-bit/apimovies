# app/schemas/session.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SessionBase(BaseModel):
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    # Agrega aquí otros campos relevantes para tu sesión

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    # Agrega aquí otros campos que se puedan actualizar, todos opcionales

class Session(SessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
class SessionResponse(BaseModel):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime | None