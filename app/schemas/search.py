# app/schemas/search.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SearchBase(BaseModel):
    user_id: int
    search_query: str

class SearchCreate(SearchBase):
    pass

class SearchUpdate(SearchBase):
    pass

class Search(SearchBase):
    search_id: int
    search_date: datetime

    model_config = ConfigDict(from_attributes=True)