# app/api/v1/endpoints/statistics.py
from sqlalchemy.sql import func
from app.models.actor import Actor
from app.models.video_actor import VideoActor
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user_video_history import UserVideoHistory
from app.models.video_fight import VideoFight
from app.models.video import VideoModel
from app.models.transaction import UserTransaction
from app.models.video_category import VideoCategory
from app.models.categories import Category
from datetime import datetime, timedelta

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/videos_by_category")
def get_videos_by_category(db: Session = Depends(get_db)):
    """
    Obtiene el número total de videos clasificados y una lista de cada categoría con el número de videos en esa categoría.
    """
    total_classified_videos = (
        db.query(VideoModel)
        .join(VideoCategory, VideoModel.id == VideoCategory.video_id)
        .filter(VideoCategory.category_id != None)
        .count()
    )

    videos_by_category = (
        db.query(
            VideoCategory.category_id,
            Category.name,
            func.count(VideoModel.id).label("total_videos")
        )
        .join(Category, Category.id == VideoCategory.category_id)
        .join(VideoModel, VideoModel.id == VideoCategory.video_id)
        .group_by(VideoCategory.category_id, Category.name)
        .all()
    )

    return {
        "total_classified_videos": total_classified_videos,
        "videos_by_category": [
            {"category_id": category.category_id, "category_name": category.name, "total_videos": category.total_videos}
            for category in videos_by_category
        ]
    }

@router.get("/videos_classification")
def get_videos_classification(db: Session = Depends(get_db)):
    """
    Obtiene el número de videos clasificados y no clasificados.
    """
    classified_videos = (
        db.query(VideoModel)
        .join(VideoCategory, VideoModel.id == VideoCategory.video_id)
        .filter(VideoCategory.category_id != None)
        .count()
    )
    unclassified_videos = (
        db.query(VideoModel)
        .outerjoin(VideoCategory, VideoModel.id == VideoCategory.video_id)
        .filter(VideoCategory.category_id == None)
        .count()
    )

    return {
        "classified_videos": classified_videos,
        "unclassified_videos": unclassified_videos
    }
@router.get("/fights")
def get_stats_fights(db: Session = Depends(get_db)):
    total_fights = db.query(VideoFight).count()
    finishes = db.query(VideoFight).filter(VideoFight.winner_video != None).count()

    return {
        "Finishes": finishes,
        "Total_fights": total_fights
    }

@router.get("/user_visualization_time")
def get_user_visualization_time(user: int, db: Session = Depends(get_db)):
    """
    Calculates the total visualization time for each day of the last week.
    """
    if not user:
        raise HTTPException(status_code=400, detail="El parámetro 'user' es obligatorio.")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    visualization_time = (
        db.query(
            func.extract('dow', UserVideoHistory.view_date).label("day_of_week"),
            func.sum(UserVideoHistory.progress).label("total_time")
        )
        .filter(UserVideoHistory.user_id == user)
        .filter(UserVideoHistory.view_date >= start_date)
        .filter(UserVideoHistory.view_date <= end_date)
        .group_by(func.extract('dow', UserVideoHistory.view_date))
        .order_by(func.extract('dow', UserVideoHistory.view_date))
        .all()
    )

    if not visualization_time:
        return {"message": f"No se encontraron datos de visualización para el usuario con ID {user} en la última semana"}

    # Mapping day numbers to names
    days_mapping = {
        0: "Domingo",
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado"
    }

    return {
        "user_id": user,
        "visualization_time_per_day": [
            {"day": days_mapping[int(day.day_of_week)], "total_time_minutes": day.total_time / 60}
            for day in visualization_time
        ]
    }


@router.get("/videos")
def get_stats_videos(db: Session = Depends(get_db)):
    total_videos = db.query(VideoModel).count()
    no_views_videos = db.query(VideoModel).filter(VideoModel.views == 0).count()
    
    return {
        "Total": total_videos,
        "video_no_views": no_views_videos
    }

@router.get("/top_actors")
def get_top_actors_with_most_views(limit: int = 5, db: Session = Depends(get_db)):
    """
    Obtiene el top N actores cuyos videos tienen más vistas.
    """
    top_actors = (
        db.query(
            Actor.id,
            Actor.name,
            Actor.profile_url,  # Agregar el profile_url
            func.sum(VideoModel.views).label("total_views")
        )
        .join(VideoActor, VideoActor.actor_id == Actor.id)
        .join(VideoModel, VideoModel.id == VideoActor.video_id)
        .group_by(Actor.id, Actor.name, Actor.profile_url)  # Incluir profile_url en group_by
        .order_by(func.sum(VideoModel.views).desc())
        .limit(limit)
        .all()
    )

    return {
        "top_actors": [
            {
                "id": actor.id,
                "name": actor.name,
                "profile_url": actor.profile_url,
                "total_views": actor.total_views,
            }
            for actor in top_actors
        ]
    }

@router.get("/user_top_days")
def get_user_top_days(user: int, db: Session = Depends(get_db)):
    """
    Obtiene los días de la semana donde un usuario ve más videos.
    """
    if not user:
        raise HTTPException(status_code=400, detail="El parámetro 'user' es obligatorio.")

    top_days = (
        db.query(
            func.extract('dow', UserVideoHistory.view_date).label("day_of_week"),  # Extrae el día de la semana (0-6)
            func.count(UserVideoHistory.history_id).label("total_views")
        )
        .filter(UserVideoHistory.user_id == user)
        .group_by(func.extract('dow', UserVideoHistory.view_date))  # Agrupa por día de la semana
        .order_by(func.count(UserVideoHistory.history_id).desc())  # Ordena por vistas
        .all()
    )

    if not top_days:
        return {"message": f"No se encontraron datos para el usuario con ID {user}"}

    # Mapeo de números de días de la semana a nombres
    days_mapping = {
        0: "Domingo",
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado"
    }

    return {
        "user_id": user,
        "top_days": [
            {"day": days_mapping[int(day.day_of_week)], "total_views": day.total_views}
            for day in top_days
        ]
    }
@router.get("/user_last_7_days_coins")
def get_user_last_7_days_coins(user: int, db: Session = Depends(get_db)):
    """
    Obtiene el total de coins ganadas por el usuario en los últimos 7 días.
    """
    if not user:
        raise HTTPException(status_code=400, detail="El parámetro 'user' es obligatorio.")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)

    coins_last_7_days = (
        db.query(
            func.date(UserTransaction.date).label("date"),
            func.sum(UserTransaction.coins_amount).label("total_coins")
        )
        .filter(UserTransaction.user_id == user)
        .filter(UserTransaction.date >= start_date)
        .filter(UserTransaction.date <= end_date)
        .group_by(func.date(UserTransaction.date))
        .order_by(func.date(UserTransaction.date))
        .all()
    )

    if not coins_last_7_days:
        return {"message": f"No se encontraron transacciones para el usuario con ID {user} en los últimos 7 días"}

    return {
        "user_id": user,
        "coins_last_7_days": [
            {"date": str(day.date), "total_coins": day.total_coins}
            for day in coins_last_7_days
        ]
    }