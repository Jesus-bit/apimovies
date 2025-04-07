from pydantic import BaseModel

class VideoCategoryBase(BaseModel):
    video_id: int
    category_id: int

class VideoCategoryCreate(VideoCategoryBase):
    pass

class VideoCategoryResponse(VideoCategoryBase):
    id: int
    name: str

    class Config:
        orm_mode = True