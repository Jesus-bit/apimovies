# app/api/v1/endpoints/session.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.session import Session as SessionSchema, SessionCreate, SessionUpdate
from app.models.session import Session as SessionModel
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=SessionSchema)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    new_session = SessionModel(**session.model_dump())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/{session_id}", response_model=SessionSchema)
def read_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/", response_model=List[SessionSchema])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).offset(skip).limit(limit).all()
    return sessions

@router.put("/{session_id}", response_model=SessionSchema)
def update_session(session_id: int, session: SessionUpdate, db: Session = Depends(get_db)):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    for key, value in session.model_dump(exclude_unset=True).items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

@router.delete("/{session_id}", response_model=SessionSchema)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return session