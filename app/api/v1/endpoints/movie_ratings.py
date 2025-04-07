# app/api/v1/endpoints/movie_rating.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.core import deps
from app.models.user import User as UserModel
from app.services.coins_service import CoinsService
from app.models.movie_ratings import MovieRating as MovieRatingModel
from app.schemas.movie_ratings import MovieRating, MovieRatingCreate, MovieRatingUpdate


router = APIRouter()

@router.post("/", response_model=MovieRating)
def create_movie_rating(movie_rating: MovieRatingCreate, user_id: int, db: Session = Depends(deps.get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="user Not found")
    coins_extra = 50

    if coins_extra:
        user_update = CoinsService.add_coins(
            user_id=user_id,
            coins=coins_extra,
            db=db,
            transaction_type="rating video"
            )

    return MovieRatingModel.create(db=db, obj_in=movie_rating)

@router.get("/", response_model=List[MovieRating])
def read_movie_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return MovieRatingModel.get_multi(db, skip=skip, limit=limit)

@router.get("/{rating_id}", response_model=MovieRating)
def read_movie_rating(rating_id: int, db: Session = Depends(deps.get_db)):
    movie_rating = MovieRatingModel.get(db, id=rating_id)
    if movie_rating is None:
        raise HTTPException(status_code=404, detail="Movie rating not found")
    return movie_rating

@router.put("/{rating_id}", response_model=MovieRating)
async def update_movie_rating(
    rating_id: int,
    movie_rating: MovieRatingUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Actualiza una calificación de película existente
    """
    try:
        db_movie_rating = MovieRatingModel.get(db, id=rating_id)
        if db_movie_rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie rating not found"
            )
        
        updated_rating = MovieRatingModel.update(
            db=db,
            db_obj=db_movie_rating,
            obj_in=movie_rating
        )
        return updated_rating
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the rating."
        )

@router.delete("/{rating_id}", response_model=MovieRating)
def delete_movie_rating(rating_id: int, db: Session = Depends(deps.get_db)):
    db_movie_rating = MovieRatingModel.get(db, id=rating_id)
    if db_movie_rating is None:
        raise HTTPException(status_code=404, detail="Movie rating not found")
    return MovieRatingModel.remove(db=db, id=rating_id)

# Nuevo endpoint para obtener la calificación más reciente basada en el video_id
@router.get("/video/{video_id}", response_model=MovieRating)
def read_latest_movie_rating_by_video_id(video_id: int, db: Session = Depends(deps.get_db)):
    movie_rating = MovieRatingModel.get_latest_by_video_id(db=db, video_id=video_id)
    if movie_rating is None:
        raise HTTPException(status_code=404, detail="Movie rating not found for the given video ID")
    return movie_rating