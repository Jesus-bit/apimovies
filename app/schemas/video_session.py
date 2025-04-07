from pydantic import BaseModel, ConfigDict
from datetime import datetime

class VideoSessionBase(BaseModel):
    user_id: int
    video_id: int
    start_time: datetime
    end_time: datetime
    session_id: int | None = None

class VideoSessionCreate(VideoSessionBase):
    pass

class VideoSessionUpdate(VideoSessionBase):
    pass

class VideoSession(VideoSessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)