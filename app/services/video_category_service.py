from app.models.video_category import VideoCategory
from app.schemas.video_category import VideoCategoryResponse
from app.models.categories import Category
from sqlalchemy.orm import Session

def create_video_category(db: Session, video_id: int, category_id: int):
    video_category = VideoCategory(video_id=video_id, category_id=category_id)
    db.add(video_category)
    db.commit()
    db.refresh(video_category)
    category_name = db.query(Category.name).filter(Category.id == category_id).scalar()
    return VideoCategoryResponse(id=video_category.id, video_id=video_category.video_id, category_id=video_category.category_id, name=category_name)

def get_video_categories(db: Session, video_id: int):
    results = db.query(VideoCategory, Category.name).join(Category, VideoCategory.category_id == Category.id).filter(VideoCategory.video_id == video_id).all()
    return [{"id": vc.id, "video_id": vc.video_id, "category_id": vc.category_id, "name": name} for vc, name in results]

def delete_video_category(db: Session, video_category_id: int):
    video_category = db.query(VideoCategory).filter(VideoCategory.id == video_category_id).first()
    if video_category:
        db.delete(video_category)
        db.commit()