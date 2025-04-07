from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.level import LevelCreate, LevelUpdate, LevelOut

from app.services.level_service import (
    create_level,
    get_levels,
    get_level,
    update_level,
    delete_level,
    get_levels_by_name
)

router = APIRouter(prefix="/levels", tags=["levels"])

@router.post("/", response_model=LevelOut)
def create_level_endpoint(level: LevelCreate, db: Session = Depends(get_db)):
    return create_level(db, level)

@router.get("/", response_model=List[LevelOut])
def read_levels(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if name:
        return get_levels_by_name(db, name)
    return get_levels(db, skip=skip, limit=limit)

@router.get("/{level_id}", response_model=LevelOut)
def read_level(level_id: int, db: Session = Depends(get_db)):
    db_level = get_level(db, level_id)
    if not db_level:
        raise HTTPException(status_code=404, detail="Level not found")
    return db_level

@router.put("/{level_id}", response_model=LevelOut)
def update_level_endpoint(
    level_id: int,
    level: LevelUpdate,
    db: Session = Depends(get_db)
):
    return update_level(db, level_id, level)

@router.delete("/{level_id}")
def delete_level_endpoint(level_id: int, db: Session = Depends(get_db)):
    return delete_level(db, level_id)