# app/schemas/transaction.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    buy_erizo = "buy erizo"
    login = "login"
    watch_video_views = "watch video views"
    watch_video_no_views = "watch video no views"
    rating_video = "rating video"
    give_like = "give like"
    add_actor_video = "add actor video"
    vote = "vote"
    change_title = "change title"  # Nuevo tipo de transacción

class MovementType(str, Enum):
    in_ = "in"
    out = "out"

class TransactionBase(BaseModel):
    user_id: int
    transaction_type: TransactionType
    coins_amount: int
    movement_type: MovementType
    date: Optional[datetime] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    transaction_type: Optional[TransactionType] = None
    coins_amount: Optional[float] = None
    movement_type: Optional[MovementType] = None

class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode = True
