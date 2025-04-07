# app/schemas/pdf.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class PageURLBase(BaseModel):
    page_number: int
    url: str

class PageURLCreate(PageURLBase):
    pass

class PageURL(PageURLBase):
    id: int
    pdf_id: int

    model_config = ConfigDict(from_attributes=True)

class PDFBase(BaseModel):
    title: str
    file_path: str
    cover_url: str

class PDFCreate(PDFBase):
    page_urls: List[PageURLCreate]

class PDFUpdate(BaseModel):
    title: Optional[str] = None
    file_path: Optional[str] = None
    page_urls: Optional[List[PageURLCreate]] = None

class PDF(PDFBase):
    id: int
    page_urls: List[PageURL]

    model_config = ConfigDict(from_attributes=True)