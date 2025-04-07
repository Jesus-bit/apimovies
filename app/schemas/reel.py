# app/schemas/reel.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReelBase(BaseModel):
    video_id: int

class ReelCreate(ReelBase):
    pass

class ReelUpdate(ReelBase):
    pass

class Reel(ReelBase):
    reel_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)