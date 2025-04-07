import os
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import heapq
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from moviepy.editor import VideoFileClip
from app.models.video import VideoModel, OrientationType
from app.db.database import Base
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa la conexión con la base de datos
engine = create_engine(settings.DATABASE_URL)

# Asegúrate de que las tablas están creadas
Base.metadata.create_all(bind=engine)

def get_video_metadata(video_path):
    """
    Extrae la duración y determina la orientación del video basado en sus dimensiones
    """
    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        width, height = clip.size
        
        # Determina la orientación basada en las dimensiones
        orientation = (
            OrientationType.VERTICAL 
            if height > width 
            else OrientationType.HORIZONTAL
        )
        
        clip.close()
        return duration, orientation
    except Exception as e:
        logger.warning(f"No se pudo obtener los metadatos para {os.path.basename(video_path)}. Error: {e}")
        return 0, OrientationType.HORIZONTAL

def insert_videos_from_folder(video_folder):
    # Crea una sesión de base de datos
    with Session(engine) as session:
        # Usamos un heap para mantener los videos ordenados por duración
        video_heap = []
        
        # Primera pasada: obtener metadatos y crear el heap
        for filename in os.listdir(video_folder):
            if os.path.isfile(os.path.join(video_folder, filename)):
                video_path = os.path.join(video_folder, filename)
                duration, orientation = get_video_metadata(video_path)
                
                # Usamos negativo de duración para ordenar de mayor a menor
                heapq.heappush(video_heap, (-duration, filename, orientation))
        
        # Segunda pasada: procesar videos ordenados e insertarlos en la base de datos
        count = 0
        total_videos = len(video_heap)
        
        while video_heap:
            duration, filename, orientation = heapq.heappop(video_heap)
            duration = -duration  # Convertimos de vuelta a positivo
            
            title = os.path.splitext(filename)[0]
            
            video = VideoModel(
                title=title,
                description="",
                category="",
                duration=duration,
                views=0,
                likes=0,
                dislikes=0,
                thumbnail_url=f"/thumbnails/v2/{title}_collage.jpg",
                video_url=f"/videos/v2/{filename}",  # Incluye la extensión original
                orientation=orientation,
                elo=1500  # Valor por defecto
            )
            
            session.add(video)
            count += 1
            
            # Hacemos un commit cada 100 videos para no sobrecargar la memoria
            if count % 100 == 0:
                session.commit()
                logger.info(f"Progreso: {count}/{total_videos} videos procesados.")
        
        # Commit final
        session.commit()
        logger.info(f"Inserción completada exitosamente. Total de videos procesados: {count}")

# Ejecuta la inserción
if __name__ == "__main__":
    video_folder = '/media/jeshu/048266e9-8c9f-4a16-9f79-0e5eaa986185/'
    insert_videos_from_folder(video_folder)