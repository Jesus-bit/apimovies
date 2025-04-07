# app/api/v1/endpoints/video_actor.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.video_actor import VideoActor as VideoActorModel
from app.models.user import User as UserModel
from app.services.coins_service import CoinsService
from app.db.database import get_db
from app.schemas.video_actor import VideoActor as VideoActorSchema, VideoActorCreate, VideoActorUpdate

router = APIRouter()

@router.post("/", response_model=VideoActorSchema)
def create_video_actor(video_actor: VideoActorCreate, user_id: int ,db: Session = Depends(get_db)):
    new_video_actor = VideoActorModel(**video_actor.dict())

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="user Not found")
    coins_extra = 100

    db.add(new_video_actor)
    db.commit()
    db.refresh(new_video_actor)

    if coins_extra:
        user_update = CoinsService.add_coins(
            user_id=user_id,
            coins=coins_extra, 
            db=db,
            transaction_type="add actor video"
        )
    return new_video_actor

@router.get("/{video_actor_id}", response_model=VideoActorSchema)
def read_video_actor(video_actor_id: int, db: Session = Depends(get_db)):
    video_actor = db.query(VideoActorModel).filter(VideoActorModel.id == video_actor_id).first()
    if video_actor is None:
        raise HTTPException(status_code=404, detail="VideoActor not found")
    return video_actor

@router.get("/", response_model=List[VideoActorSchema])
def read_video_actors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    video_actors = db.query(VideoActorModel).offset(skip).limit(limit).all()
    return video_actors

@router.get("/video/{video_id}", response_model=List[VideoActorSchema])
def read_video_actors_by_video_id(video_id: int, db: Session = Depends(get_db)):
    video_actors = db.query(VideoActorModel).filter(VideoActorModel.video_id == video_id).all()
    if not video_actors:
        raise HTTPException(status_code=404, detail="No actors found for this video ID")
    return video_actors

@router.put("/{video_actor_id}", response_model=VideoActorSchema)
def update_video_actor(video_actor_id: int, video_actor: VideoActorUpdate, db: Session = Depends(get_db)):
    db_video_actor = db.query(VideoActorModel).filter(VideoActorModel.id == video_actor_id).first()
    if db_video_actor is None:
        raise HTTPException(status_code=404, detail="VideoActor not found")
    
    for key, value in video_actor.model_dump(exclude_unset=True).items():
        setattr(db_video_actor, key, value)
    
    db.commit()
    db.refresh(db_video_actor)
    return db_video_actor

@router.delete("/{video_actor_id}", response_model=VideoActorSchema)
def delete_video_actor(video_actor_id: int, db: Session = Depends(get_db)):
    video_actor = db.query(VideoActorModel).filter(VideoActorModel.id == video_actor_id).first()
    if video_actor is None:
        raise HTTPException(status_code=404, detail="VideoActor not found")
    
    db.delete(video_actor)
    db.commit()
    return video_actor