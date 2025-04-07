import os
import re
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import logging
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.video import VideoModel
from app.core.config import settings
from app.models.movie_ratings import MovieRating as MovieRatingModel

# Configurar logger
def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('elo_update.log', encoding='utf-8')
        ]
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger

logger = setup_logger()

# Conectar a la base de datos
try:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Conexión a la base de datos establecida correctamente.")
except Exception as e:
    logger.error(f"Error al establecer conexión a la base de datos: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

def update_elo(player_a_elo, player_b_elo, result):
    k = 32  # Factor K
    new_elo_a = player_a_elo + k * (result - 1 / (1 + 10 ** ((player_b_elo - player_a_elo) / 400)))
    new_elo_b = player_b_elo + k * ((1 - result) - 1 / (1 + 10 ** ((player_a_elo - player_b_elo) / 400)))
    return int(new_elo_a), int(new_elo_b)

def update_all_videos_elo():
    db = SessionLocal()
    try:
        videos = db.query(VideoModel).all()
        for video in videos:
            ratings = db.query(MovieRatingModel).filter(MovieRatingModel.video_id == video.id).all()
            if not ratings:
                continue

            total_elo = video.elo
            for rating in ratings:
                # Suponiendo que el resultado es 1 si es positivo, 0.5 si es empate y 0 si es negativo
                result = 1 if rating.rating >= 3 else 0
                total_elo, _ = update_elo(total_elo, video.elo, result)

            video.elo = max(1000, total_elo)
            logger.info(f"Video ID {video.id} actualizado con ELO: {video.elo}")

        db.commit()
        logger.info("ELO de todos los videos actualizado correctamente.")
    except Exception as e:
        logger.error(f"Error al actualizar el ELO: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    update_all_videos_elo()
