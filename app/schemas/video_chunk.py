from pydantic import BaseModel
from typing import Optional

class VideoChunkCreate(BaseModel):
    video_id: int
    chunk_start_time: Optional[int] = None
    chunk_end_time: Optional[int] = None

class VideoChunkResponse(VideoChunkCreate):
    id: int

    class Config:
        from_attributes = True
