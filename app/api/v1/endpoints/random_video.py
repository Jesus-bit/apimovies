from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import List
from app.db.database import get_db
from app.models.video import VideoModel, OrientationType
from app.schemas.video import Video
from app.models.reel import Reel as ReelModel
from app.schemas.reel import Reel
from app.services.video_query_service import VideoQueryService

router = APIRouter()

@router.get("/horizontal-videos", response_model=List[Video])
async def get_random_horizontal_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    video_service = VideoQueryService(db)
    return video_service.get_random_videos(skip, limit, OrientationType.HORIZONTAL)


@router.get("/reels", response_model=List[Video])
async def get_random_reels(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    video_service = VideoQueryService(db)
    return video_service.get_random_videos(skip, limit, OrientationType.VERTICAL)


@router.get("/video", response_model=List[Video])
async def get_random_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    video_service = VideoQueryService(db)
    return video_service.get_random_videos(skip, limit)