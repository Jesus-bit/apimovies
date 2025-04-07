from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

# Esquema para representar un nivel
class Level(BaseModel):
    level_id: int
    name: str
    required_points: int
    medal_url: str

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    email: str
    birthdate: date
    gender: Optional[str] = None
    location: Optional[str] = None
    subscription: Optional[str] = "Free"
    hashed_password: Optional[str] = None
    coins: Optional[int] = 0
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    subscription: Optional[str] = None
    coins: Optional[int] = None
    avatar_url: Optional[str] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    level: Optional[Level]  # Nivel relacionado

    model_config = ConfigDict(from_attributes=True)
