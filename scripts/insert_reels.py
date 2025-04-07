import os
import heapq
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from moviepy.editor import VideoFileClip
from app.models.video import VideoModel
from app.models.reel import Reel  # Cambiado a Reel en lugar de ReelModel
from app.db.database import Base
from app.core.config import settings
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa la conexión con la base de datos
engine = create_engine(settings.DATABASE_URL)

# Asegúrate de que las tablas están creadas
Base.metadata.create_all(bind=engine)

# Función para extraer la duración del video
def get_video_duration(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        clip.close()
        return duration
    except Exception as e:
        logger.warning(f"No se pudo obtener la duración para {os.path.basename(video_path)}. Error: {e}")
        return 0

# Carpeta de videos
video_folder = '/media/jeshu/75bc4f11-e4e5-48e1-a92a-ea0b89524415/verticales/verticales/'

# Función para insertar registros de video y reel en la base de datos
def insert_videos_and_reels_from_folder(video_folder):
    # Crea una sesión de base de datos
    with Session(engine) as session:
        # Usamos un heap para mantener los videos ordenados por duración
        video_heap = []
        
        # Primera pasada: obtener duraciones y crear el heap
        for filename in os.listdir(video_folder):
            video_path = os.path.join(video_folder, filename)
            duration = get_video_duration(video_path)
            
            # Usamos negativo de duración para ordenar de mayor a menor
            heapq.heappush(video_heap, (-duration, filename))
        
        # Segunda pasada: procesar videos ordenados e insertarlos en la base de datos
        while video_heap:
            duration, filename = heapq.heappop(video_heap)
            duration = -duration  # Convertimos de vuelta a positivo
            
            video_path = os.path.join(video_folder, filename)
            title = os.path.splitext(filename)[0]
            
            video = VideoModel(
                title=title,
                description="",
                category="",
                duration=duration,
                views=0,
                likes=0,
                dislikes=0,
                thumbnail_url=f"/thumbnails/verticales/{title}_collage.jpg",
                video_url=f"/videos/verticales/{filename}"
            )
            
            session.add(video)
            session.flush()  # Esto asigna un ID al video sin hacer commit
            
            # Crear el registro de Reel correspondiente
            reel = Reel(
                video_id=video.id,
                created_at=datetime.now()
            )
            
            session.add(reel)
            
            # Hacemos un commit cada 100 videos para no sobrecargar la memoria
            if len(video_heap) % 100 == 0:
                session.commit()
                logger.info(f"Commit parcial realizado. {len(video_heap)} videos restantes.")
        
        # Commit final
        session.commit()
        logger.info("Inserción de videos y reels completada exitosamente.")

# Ejecuta la inserción
if __name__ == "__main__":
    insert_videos_and_reels_from_folder(video_folder)