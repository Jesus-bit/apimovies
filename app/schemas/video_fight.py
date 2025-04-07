# app/schemas/video_fight.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class VideoFightBase(BaseModel):
    user_id: int
    video_1_id: int
    video_2_id: int

class VideoFightCreate(VideoFightBase):
    pass

class VideoFightUpdate(BaseModel):
    winner_video: Optional[int]

class VideoFightResponse(VideoFightBase):
    fight_id: int
    winner_video: Optional[int]
    fight_date: datetime

    model_config = ConfigDict(from_attributes=True)
