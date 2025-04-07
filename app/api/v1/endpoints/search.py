# app/api/v1/endpoints/search.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core import deps
from app.models.search import Search as SearchModel
from app.schemas.search import Search, SearchCreate, SearchUpdate

router = APIRouter()

@router.post("/", response_model=Search)
def create_search(search: SearchCreate, db: Session = Depends(deps.get_db)):
    return SearchModel.create(db=db, obj_in=search)

@router.get("/", response_model=List[Search])
def read_searches(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return SearchModel.get_multi(db, skip=skip, limit=limit)

@router.get("/{search_id}", response_model=Search)
def read_search(search_id: int, db: Session = Depends(deps.get_db)):
    search = SearchModel.get(db, id=search_id)
    if search is None:
        raise HTTPException(status_code=404, detail="Search not found")
    return search

@router.put("/{search_id}", response_model=Search)
def update_search(search_id: int, search: SearchUpdate, db: Session = Depends(deps.get_db)):
    db_search = SearchModel.get(db, id=search_id)
    if db_search is None:
        raise HTTPException(status_code=404, detail="Search not found")
    return SearchModel.update(db=db, db_obj=db_search, obj_in=search)

@router.delete("/{search_id}", response_model=Search)
def delete_search(search_id: int, db: Session = Depends(deps.get_db)):
    db_search = SearchModel.get(db, id=search_id)
    if db_search is None:
        raise HTTPException(status_code=404, detail="Search not found")
    return SearchModel.remove(db=db, id=search_id)