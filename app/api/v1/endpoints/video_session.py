from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core import deps
from app.models.video_session import VideoSession as VideoSessionModel
from app.schemas.video_session import VideoSession, VideoSessionCreate, VideoSessionUpdate

router = APIRouter()

@router.post("/", response_model=VideoSession)
def create_video_session(video_session: VideoSessionCreate, db: Session = Depends(deps.get_db)):
    return VideoSessionModel.create(db=db, obj_in=video_session)

@router.get("/", response_model=List[VideoSession])
def read_video_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return VideoSessionModel.get_multi(db, skip=skip, limit=limit)

@router.get("/{video_session_id}", response_model=VideoSession)
def read_video_session(video_session_id: int, db: Session = Depends(deps.get_db)):
    video_session = VideoSessionModel.get(db, id=video_session_id)
    if video_session is None:
        raise HTTPException(status_code=404, detail="Video session not found")
    return video_session

@router.put("/{video_session_id}", response_model=VideoSession)
def update_video_session(video_session_id: int, video_session: VideoSessionUpdate, db: Session = Depends(deps.get_db)):
    db_video_session = VideoSessionModel.get(db, id=video_session_id)
    if db_video_session is None:
        raise HTTPException(status_code=404, detail="Video session not found")
    return VideoSessionModel.update(db=db, db_obj=db_video_session, obj_in=video_session)

@router.delete("/{video_session_id}", response_model=VideoSession)
def delete_video_session(video_session_id: int, db: Session = Depends(deps.get_db)):
    db_video_session = VideoSessionModel.get(db, id=video_session_id)
    if db_video_session is None:
        raise HTTPException(status_code=404, detail="Video session not found")
    return VideoSessionModel.remove(db=db, id=video_session_id)