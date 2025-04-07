# app/api/v1/endpoints/pdf.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.pdf import PDF, PDFCreate, PDFUpdate
from app.models.pdf import PDF as PDFModel, PageURL
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=PDF)
def create_pdf(pdf: PDFCreate, db: Session = Depends(get_db)):
    new_pdf = PDFModel(title=pdf.title, file_path=pdf.file_path)
    db.add(new_pdf)
    db.commit()
    db.refresh(new_pdf)
    
    # Añadir las URLs de las páginas
    for page_number, url in pdf.page_urls.urls.items():
        page_url = PageURL(pdf_id=new_pdf.id, page_number=page_number, url=url)
        db.add(page_url)
    
    db.commit()
    db.refresh(new_pdf)
    return new_pdf

@router.get("/{pdf_id}", response_model=PDF)
def read_pdf(pdf_id: int, db: Session = Depends(get_db)):
    pdf = db.query(PDFModel).filter(PDFModel.id == pdf_id).first()
    if pdf is None:
        raise HTTPException(status_code=404, detail="PDF not found")
    return pdf

@router.get("/", response_model=List[PDF])
def read_pdfs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pdfs = db.query(PDFModel).offset(skip).limit(limit).all()
    return pdfs

@router.put("/{pdf_id}", response_model=PDF)
def update_pdf(pdf_id: int, pdf: PDFUpdate, db: Session = Depends(get_db)):
    db_pdf = db.query(PDFModel).filter(PDFModel.id == pdf_id).first()
    if db_pdf is None:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Actualizar campos básicos
    for key, value in pdf.model_dump(exclude={'page_urls'}, exclude_unset=True).items():
        setattr(db_pdf, key, value)
    
    # Actualizar URLs de páginas si se proporcionan
    if pdf.page_urls:
        # Eliminar URLs existentes
        db.query(PageURL).filter(PageURL.pdf_id == pdf_id).delete()
        
        # Añadir nuevas URLs
        for page_number, url in pdf.page_urls.urls.items():
            page_url = PageURL(pdf_id=pdf_id, page_number=page_number, url=url)
            db.add(page_url)
    
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

@router.delete("/{pdf_id}", response_model=PDF)
def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    pdf = db.query(PDFModel).filter(PDFModel.id == pdf_id).first()
    if pdf is None:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Eliminar las URLs de las páginas asociadas
    db.query(PageURL).filter(PageURL.pdf_id == pdf_id).delete()
    
    db.delete(pdf)
    db.commit()
    return pdf

@router.delete("/delete/all", response_model=List[PDF])
def delete_all_pdfs(db: Session = Depends(get_db)):
    pdfs = db.query(PDFModel).all()
    if not pdfs:
        raise HTTPException(status_code=404, detail="No PDFs found")
    
    # Eliminar las URLs de las páginas asociadas a cada PDF
    for pdf in pdfs:
        db.query(PageURL).filter(PageURL.pdf_id == pdf.id).delete()
        db.delete(pdf)
    
    db.commit()
    return pdfs
