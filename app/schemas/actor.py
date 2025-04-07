from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional

class ActorBase(BaseModel):
    name: str
    age: int
    nationality: Optional[str] = None  # Nacionalidad como campo opcional
    profile_url: Optional[HttpUrl] = None  # URL del perfil como campo opcional

class ActorCreate(ActorBase):
    pass

class ActorUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    nationality: Optional[str] = None
    profile_url: Optional[HttpUrl] = None

class Actor(ActorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
