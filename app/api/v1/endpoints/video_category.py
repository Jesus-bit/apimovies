from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.services.video_category_service import (
    create_video_category,
    get_video_categories,
    delete_video_category
)
from app.schemas.video_category import (
    VideoCategoryCreate,
    VideoCategoryResponse
)
from app.models.video_category import VideoCategory

router = APIRouter(prefix="/video_category", tags=["video_category"])

@router.post("/", response_model=VideoCategoryResponse)
def create_video_category_endpoint(video_category: VideoCategoryCreate, db: Session = Depends(get_db)):
    return create_video_category(db, video_id=video_category.video_id, category_id=video_category.category_id)

@router.get("/{video_id}", response_model=list[VideoCategoryResponse])
def get_video_categories_endpoint(video_id: int, db: Session = Depends(get_db)):
    return get_video_categories(db, video_id)

@router.delete("/{video_category_id}")
def delete_video_category_endpoint(video_category_id: int, db: Session = Depends(get_db)):
    video_category = db.query(VideoCategory).filter(VideoCategory.id == video_category_id).first()
    if not video_category:
        raise HTTPException(status_code=404, detail="VideoCategory not found")
    delete_video_category(db, video_category_id)
    return {"message": "VideoCategory deleted successfully"}
