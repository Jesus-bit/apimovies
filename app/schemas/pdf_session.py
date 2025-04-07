# app/schemas/pdf_session.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PDFSessionBase(BaseModel):
    user_id: int
    pdf_id: int
    pdf_url: str
    start_time: datetime
    end_time: datetime
    page_read: int = 1
    session_id: int | None = None

class PDFSessionCreate(PDFSessionBase):
    pass

class PDFSessionUpdate(PDFSessionBase):
    pass

class PDFSession(PDFSessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
