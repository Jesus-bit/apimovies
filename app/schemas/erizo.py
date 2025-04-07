from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ErizoState(str, Enum):
    active = "active"
    used = "used"

class ErizoBase(BaseModel):
    user_id: int
    state: ErizoState
    date_acquisition: Optional[datetime] = None

class ErizoCreate(ErizoBase):
    pass

class ErizoUpdate(BaseModel):
    state: Optional[ErizoState] = None

class ErizoResponse(ErizoBase):
    id: int

    class Config:
        orm_mode = True
