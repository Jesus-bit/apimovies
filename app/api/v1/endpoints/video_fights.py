# app/api/v1/endpoints/video_fights.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.video_fight import VideoFight
from app.models.video import VideoModel
from app.schemas.video_fight import VideoFightCreate, VideoFightResponse, VideoFightUpdate
from app.services.coins_service import CoinsService
from app.utils.update_elo import update_elo
from datetime import datetime

router = APIRouter()

# Ruta para obtener estadísticas de peleas
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_fights = db.query(VideoFight).count()
    finishes = db.query(VideoFight).filter(VideoFight.winner_video != None).count()

    return {
        "Finishes": finishes,
        "Total_fights": total_fights
    }
# Crear una nueva pelea de videos
@router.post("/", response_model=VideoFightResponse)
def create_video_fight(fight: VideoFightCreate, db: Session = Depends(get_db)):
    db_fight = VideoFight(**fight.model_dump())
    db.add(db_fight)
    db.commit()
    db.refresh(db_fight)
    return db_fight

# Obtener todas las peleas de videos de un usuario específico
@router.get("/{user_id}", response_model=List[VideoFightResponse])
def get_video_fights(user_id: int, 
                     limit: int = Query(100, ge=1),  # Valor por defecto: 100, mínimo: 1
                     db: Session = Depends(get_db)):
    # Obtener peleas del usuario con un límite
    fights = db.query(VideoFight).filter(VideoFight.user_id == user_id).limit(limit).all()
    if not fights:
        raise HTTPException(status_code=404, detail="Peleas no encontradas")
    return fights

@router.get("/{user_id}/unfinished", response_model=List[VideoFightResponse])
def get_unfinished_video_fights(user_id: int, 
                                 limit: int = Query(100, ge=1),  # Valor por defecto: 100, mínimo: 1
                                 db: Session = Depends(get_db)):
    # Obtener peleas sin winner_video para el usuario específico
    unfinished_fights = (
        db.query(VideoFight)
        .filter(
            VideoFight.user_id == user_id, 
            VideoFight.winner_video == None
        )
        .limit(limit)
        .all()
    )
    
    if not unfinished_fights:
        raise HTTPException(status_code=404, detail="No hay peleas sin resolver")
    
    return unfinished_fights


@router.put("/{fight_id}", response_model=VideoFightResponse)
def update_video_fight(
    fight_id: int,
    user_id: int,
    fight_update: VideoFightUpdate,
    db: Session = Depends(get_db)
    ):
    # Buscar la pelea en la base de datos
    db_fight = db.query(VideoFight).filter(VideoFight.fight_id == fight_id).first()
    if not db_fight:
        raise HTTPException(status_code=404, detail="Pelea no encontrada")

    # Update el winner y la date
    if fight_update.winner_video:
        if fight_update.winner_video not in [db_fight.video_1_id, db_fight.video_2_id]:
            raise HTTPException(status_code=400, detail="El video ganador no pertenece a esta pelea")
        db_fight.winner_video = fight_update.winner_video
        db_fight.fight_date = datetime.now()

        # Get videos Relationships para recalculate Elo
        video_1 = db.query(VideoModel).filter(VideoModel.id == db_fight.video_1_id).first()
        video_2 = db.query(VideoModel).filter(VideoModel.id == db_fight.video_2_id).first()

        if not video_1 or not video_2:
            raise HTTPException(status_code=404, detail="Uno o ambos videos not found")

        # Determinate el result para calculate Elo
        result = 1 if db_fight.winner_video == db_fight.video_1_id else 0
        new_elo_1, new_elo_2 = update_elo(video_1.elo, video_2.elo, result)

        # Update los Values de Elo de los videos
        video_1.elo = new_elo_1
        video_2.elo = new_elo_2

    # Save changes en la base de datos
    db.commit()
    db.refresh(db_fight)

    coins_extra = 10
    transactionType = "vote"

    if coins_extra and transactionType:
        user_update = CoinsService.add_coins(
            user_id=user_id,
            coins=coins_extra,
            db=db,
            transaction_type=transactionType
        )
    return db_fight

# Delete una fight de videos
@router.delete("/{fight_id}")
def delete_video_fight(fight_id: int, db: Session = Depends(get_db)):
    db_fight = db.query(VideoFight).filter(VideoFight.fight_id == fight_id).first()
    if not db_fight:
        raise HTTPException(status_code=404, detail="fight dont found it")
    
    db.delete(db_fight)
    db.commit()
    return {"message": "fight delete successfully"}

