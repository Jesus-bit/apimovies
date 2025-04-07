from typing import Optional
from pydantic import BaseModel, Field

class LevelBase(BaseModel):
    name: str = Field(..., description="Name of the level")
    required_points: int = Field(..., ge=0, description="Points required to achieve this level")
    medal_url: str = Field(..., description="URL of the medal image for this level")

class LevelCreate(LevelBase):
    pass

class LevelUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the level")
    required_points: Optional[int] = Field(None, ge=0, description="Points required to achieve this level")
    medal_url: Optional[str] = Field(None, description="URL of the medal image for this level")

class LevelOut(LevelBase):
    level_id: int = Field(..., description="Unique identifier for the level")

    class Config:
        from_attributes = True  # New name for orm_mode in Pydantic v2
        json_schema_extra = {
            "example": {
                "level_id": 1,
                "name": "Beginner",
                "required_points": 100,
                "medal_url": "https://example.com/medals/beginner.png"
            }
        }