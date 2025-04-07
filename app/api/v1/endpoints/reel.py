# app/api/v1/endpoints/reel.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core import deps
from app.models.reel import Reel as ReelModel
from app.schemas.reel import Reel, ReelCreate, ReelUpdate

router = APIRouter()

@router.post("/", response_model=Reel)
def create_reel(reel: ReelCreate, db: Session = Depends(deps.get_db)):
    return ReelModel.create(db=db, obj_in=reel)

@router.get("/", response_model=List[Reel])
def read_reels(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return ReelModel.get_multi(db, skip=skip, limit=limit)

@router.get("/{reel_id}", response_model=Reel)
def read_reel(reel_id: int, db: Session = Depends(deps.get_db)):
    reel = ReelModel.get(db, id=reel_id)
    if reel is None:
        raise HTTPException(status_code=404, detail="Reel not found")
    return reel

@router.put("/{reel_id}", response_model=Reel)
def update_reel(reel_id: int, reel: ReelUpdate, db: Session = Depends(deps.get_db)):
    db_reel = ReelModel.get(db, id=reel_id)
    if db_reel is None:
        raise HTTPException(status_code=404, detail="Reel not found")
    return ReelModel.update(db=db, db_obj=db_reel, obj_in=reel)
