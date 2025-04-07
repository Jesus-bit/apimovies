# app/api/v1/endpoints/pdf_session.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core import deps
from app.models.pdf_session import PDFSession as PDFSessionModel
from app.schemas.pdf_session import PDFSession, PDFSessionCreate, PDFSessionUpdate

router = APIRouter()

@router.post("/", response_model=PDFSession)
def create_pdf_session(pdf_session: PDFSessionCreate, db: Session = Depends(deps.get_db)):
    return PDFSessionModel.create(db=db, obj_in=pdf_session)

@router.get("/", response_model=List[PDFSession])
def read_pdf_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return PDFSessionModel.get_multi(db, skip=skip, limit=limit)

@router.get("/{pdf_session_id}", response_model=PDFSession)
def read_pdf_session(pdf_session_id: int, db: Session = Depends(deps.get_db)):
    pdf_session = PDFSessionModel.get(db, id=pdf_session_id)
    if pdf_session is None:
        raise HTTPException(status_code=404, detail="PDF Session not found")
    return pdf_session

@router.put("/{pdf_session_id}", response_model=PDFSession)
def update_pdf_session(pdf_session_id: int, pdf_session: PDFSessionUpdate, db: Session = Depends(deps.get_db)):
    db_pdf_session = PDFSessionModel.get(db, id=pdf_session_id)
    if db_pdf_session is None:
        raise HTTPException(status_code=404, detail="PDF Session not found")
    return PDFSessionModel.update(db=db, db_obj=db_pdf_session, obj_in=pdf_session)

@router.delete("/{pdf_session_id}", response_model=PDFSession)
def delete_pdf_session(pdf_session_id: int, db: Session = Depends(deps.get_db)):
    db_pdf_session = PDFSessionModel.get(db, id=pdf_session_id)
    if db_pdf_session is None:
        raise HTTPException(status_code=404, detail="PDF Session not found")
    return PDFSessionModel.remove(db=db, id=pdf_session_id)