import os
import sys
from pathlib import Path
from datetime import datetime
import random
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from app.models.video import VideoModel
from app.models.video_fight import VideoFight
from app.db.database import Base
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa la conexión con la base de datos
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)

def update_elo(player_a_elo, player_b_elo, result):
    k = 32  # Factor de ajuste ELO
    new_elo_a = player_a_elo + k * (result - 1 / (1 + 10 ** ((player_b_elo - player_a_elo) / 400)))
    new_elo_b = player_b_elo + k * ((1 - result) - 1 / (1 + 10 ** ((player_a_elo - player_b_elo) / 400)))
    return int(new_elo_a), int(new_elo_b)

def create_swiss_style_video_fights(max_fights_per_video=10, existing_fights_count=2082):
    with Session(engine) as db:
        try:
            videos = db.query(VideoModel.id, VideoModel.duration, VideoModel.elo).all()
            if len(videos) < 2:
                logger.error("No hay suficientes videos para crear peleas.")
                return
            
            # Calcular la calidad promedio de los videos
            avg_duration = sum(v.duration for v in videos) / len(videos)
            videos = [(v.id, v.duration, abs(v.duration - avg_duration), v.elo) for v in videos]
            
            # Ordenar por diferencia con la media (para balancear enfrentamientos)
            videos.sort(key=lambda v: (v[2], v[1]))
            
            existing_fights = set()
            db_fights = db.query(VideoFight.video_1_id, VideoFight.video_2_id).all()
            for fight in db_fights:
                existing_fights.add((min(fight.video_1_id, fight.video_2_id), max(fight.video_1_id, fight.video_2_id)))
            
            fights_created = 0
            video_fight_counts = {video[0]: 0 for video in videos}
            
            for i in range(len(videos)):
                for j in range(i + 1, len(videos)):
                    video_1, video_2 = videos[i], videos[j]
                    fight_pair = (min(video_1[0], video_2[0]), max(video_1[0], video_2[0]))
                    
                    if fight_pair not in existing_fights and \
                       video_fight_counts[video_1[0]] < max_fights_per_video and \
                       video_fight_counts[video_2[0]] < max_fights_per_video:
                        
                        new_fight = VideoFight(
                            user_id=1,
                            video_1_id=fight_pair[0],
                            video_2_id=fight_pair[1],
                            winner_video=None,
                            fight_date=datetime.now()
                        )
                        db.add(new_fight)
                        existing_fights.add(fight_pair)
                        
                        video_fight_counts[video_1[0]] += 1
                        video_fight_counts[video_2[0]] += 1
                        fights_created += 1
                    
                    if fights_created + existing_fights_count >= len(videos) * max_fights_per_video // 2:
                        break
            
            db.commit()
            logger.info(f"Se han creado {fights_created} peleas de videos adicionales optimizadas.")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Ocurrió un error: {str(e)}")

if __name__ == "__main__":
    create_swiss_style_video_fights(max_fights_per_video=10, existing_fights_count=2082)
