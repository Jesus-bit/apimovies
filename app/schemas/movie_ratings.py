# app/schemas/movie_rating.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class MovieRatingBase(BaseModel):
    user_id: int
    video_id: int
    rating: Decimal = Field(..., ge=0, le=5, decimal_places=1)

class MovieRatingCreate(MovieRatingBase):
    pass

class MovieRatingUpdate(MovieRatingBase):
    user_id: Optional[int] = None
    video_id: Optional[int] = None  # Cambiado de movie_id a video_id
    rating: Optional[Decimal] = Field(None, ge=0, le=5, decimal_places=1)

class MovieRating(MovieRatingBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)