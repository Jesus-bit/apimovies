from sqlalchemy.orm import Session
from app.models.level import Level
from app.schemas.level import LevelCreate, LevelUpdate
from fastapi import HTTPException

def create_level(db: Session, level: LevelCreate):
    db_level = Level(**level.dict())
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level

def get_levels(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Level).offset(skip).limit(limit).all()

def get_level(db: Session, level_id: int):
    return db.query(Level).filter(Level.level_id == level_id).first()

def update_level(db: Session, level_id: int, level: LevelUpdate):
    db_level = get_level(db, level_id)
    if not db_level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    for key, value in level.dict(exclude_unset=True).items():
        setattr(db_level, key, value)
    
    db.commit()
    db.refresh(db_level)
    return db_level

def delete_level(db: Session, level_id: int):
    db_level = get_level(db, level_id)
    if not db_level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    db.delete(db_level)
    db.commit()
    return {"message": "Level deleted successfully"}

def get_levels_by_name(db: Session, name: str):
    return db.query(Level).filter(Level.name.ilike(f"%{name}%")).all()