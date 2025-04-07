from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.categories_service import (
    create_category,
    get_all_categories,
    get_category,
    delete_category
)
from app.schemas.categories import (
    CategoryCreate,
    CategoryResponse
)

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, name=category.name)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/", response_model=list[CategoryResponse])
def get_all_categories_endpoint(db: Session = Depends(get_db)):
    return get_all_categories(db)

@router.delete("/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(db, category_id)
    return {"message": "Category deleted successfully"}