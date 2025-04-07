# app/models/pdf.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSONB

class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    cover_url = Column(String, nullable=True)  # Nueva propiedad para la URL de portada
    
    # Relación uno a muchos con PDFSession
    pdf_sessions = relationship("PDFSession", back_populates="pdf")
    
    # Nueva relación uno a muchos con PageURL
    page_urls = relationship("PageURL", back_populates="pdf")

class PageURL(Base):
    __tablename__ = "page_urls"

    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(Integer, ForeignKey("pdfs.id"))
    page_number = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    
    # Relación muchos a uno con PDF
    pdf = relationship("PDF", back_populates="page_urls")