from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.models.video import VideoModel
from app.models.video_category import VideoCategory as VideoCategoryModel
from app.schemas.video import VideoCreate, Video, VideoUpdate
from app.models.reel import Reel as ReelModel
from app.models.video_fight import VideoFight
from app.models.user import User as UserModel
from app.services.coins_service import CoinsService
from app.db.database import get_db
from typing import List
from app.models.video_actor import VideoActor as VideoActorModel
from app.models.movie_ratings import MovieRating as MovieRatingModel
from sqlalchemy.exc import SQLAlchemyError
from app.models.video_category import VideoCategory  # From your model
from app.models.video_chunk import VideoChunk  # From your model

import paramiko
import os
from sqlalchemy.sql import func

# Detalles del servidor NGINX
NGINX_HOST = os.getenv("RPI_HOST", "192.168.100.20")
NGINX_USER = "jesus-bit"
PRIVATE_KEY_PATH = os.getenv("RPI_KEY_PATH", "/home/jeshu/.ssh/id_rsa")
BASE_PATH_VERTICAL = "/mnt/my_usb/verticales/verticales"
PRIVATE_KEY_PASSPHRASE = "la-seguridad-de-este-sistema"  # Contraseña de la clave privada
BASE_PATH_HORIZONTAL = "/mnt/my_usb/horizontales"
BASE_PATH="/media/jesus-bit/"


def ssh_delete_video(video_url: str) -> bool:
    """Delete a video file from the server storage via SSH.

    Args:
        video_url: The URL of the video to delete (can be either format)

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    print(f"🔍 Debug: Starting ssh_delete_video for URL: {video_url}")

    try:
        # Step 1: Create SSH client
        print("🔍 Debug: Creating SSH client...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(NGINX_HOST, username=NGINX_USER, key_filename=PRIVATE_KEY_PATH)
        print("✅ Debug: SSH connection established")

        # Step 4: Extract filename and determine the base path
        print(f"🔍 Debug: Extracting filename from {video_url}")
        filename = os.path.basename(video_url)
        print(f"✅ Debug: Extracted filename: {filename}")

        if "horizontal" in video_url:
            base_path = BASE_PATH_HORIZONTAL
            print("✅ Debug: Identified as horizontal video")
        elif "vertical" in video_url:
            base_path = BASE_PATH_VERTICAL
            print("✅ Debug: Identified as vertical video")
        elif "v2" in video_url:
            base_path = BASE_PATH
            print("✅ Debug: Identified as v2 format video")
        else:
            raise ValueError("⚠️ Error: Formato de URL no reconocido")

        # Step 5: Construct full path
        video_full_path = os.path.join(base_path, filename)
        print(f"✅ Debug: Full video path resolved to: {video_full_path}")

        # Step 6: Build delete command
        command = f"rm -f {video_full_path}"
        print(f"🔍 Debug: Executing SSH command: {command}")

        # Step 7: Execute delete command
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        print(f"🔍 Debug: Command exit status: {exit_status}")

        # Step 8: Check for errors
        error = stderr.read().decode().strip()
        if exit_status != 0:
            raise Exception(f"SSH command failed: {error}")

        print("✅ Debug: Video file deleted successfully")

        # Step 9: Close SSH connection
        ssh.close()
        return True

    except Exception as e:
        print(f"❌ Error deleting video file: {str(e)}")
        if 'ssh' in locals():
            ssh.close()
        return False

router = APIRouter()

@router.get("/no_views", response_model=List[Video])
def get_videos_with_no_views(limit: int = 20, db: Session = Depends(get_db)):
    """
    Endpoint para obtener la lista de videos con cero vistas.

    Parámetros:
    - limit (int): Número máximo de videos a retornar. Por defecto es 20.

    Respuesta:
    - Una lista de objetos Video que tienen 0 vistas.

    Funcionamiento:
    1. Consulta todos los videos en la base de datos donde el campo `views` es igual a 0.
    2. Limita el número de resultados al valor proporcionado en el parámetro `limit`.
    3. Retorna la lista de videos encontrados.

    Ejemplo de URL:
    - `/no_views?limit=20`
    """
    videos = db.query(VideoModel).filter(VideoModel.views == 0).limit(limit).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found with zero views")
    return videos

@router.get("/no_views/random", response_model=List[Video])
def get_random_videos_with_no_views(limit: int = 5, db: Session = Depends(get_db)):
    """
    Endpoint para obtener una lista aleatoria de videos con cero vistas.

    Parámetros:
    - limit (int): Número máximo de videos a retornar. Por defecto es 5.

    Respuesta:
    - Una lista de objetos Video que tienen 0 vistas en orden aleatorio.

    Funcionamiento:
    1. Consulta todos los videos en la base de datos donde el campo `views` es igual a 0.
    2. Ordena los resultados de manera aleatoria.
    3. Limita el número de resultados al valor proporcionado en el parámetro `limit`.
    4. Retorna la lista de videos encontrados.

    Ejemplo de URL:
    - `/no_views/random?limit=20`
    """
    videos = db.query(VideoModel).filter(VideoModel.views == 0).order_by(func.random()).limit(limit).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found with zero views")
    return videos

@router.get("/no_category", response_model=List[Video])
def get_videos_with_no_category(limit: int = 20, db: Session = Depends(get_db)):
    """
    Endpoint para obtener la lista de videos sin categoría asignada.

    Parámetros:
    - limit (int): Número máximo de videos a retornar. Por defecto es 20.

    Respuesta:
    - Una lista de objetos Video que no tienen categoría asignada.

    Ejemplo de URL:
    - `/no_category?limit=20`
    """
    videos = db.query(VideoModel).outerjoin(VideoCategoryModel, VideoModel.id == VideoCategoryModel.video_id).filter(VideoCategoryModel.category_id == None).limit(limit).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found with no category")
    return videos

@router.get("/no_category/random", response_model=List[Video])
def get_random_videos_with_no_category(limit: int = 15, db: Session = Depends(get_db)):
    """
    Endpoint para obtener una lista aleatoria de videos sin categoría asignada.

    Parámetros:
    - limit (int): Número máximo de videos a retornar. Por defecto es 15.

    Respuesta:
    - Una lista de objetos Video que no tienen categoría asignada en orden aleatorio.

    Ejemplo de URL:
    - `/no_category/random?limit=5`
    """
    videos = db.query(VideoModel).outerjoin(VideoCategoryModel, VideoModel.id == VideoCategoryModel.video_id).filter(VideoCategoryModel.category_id == None).order_by(func.random()).limit(limit).all()

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found with no category")
    return videos


# Cargar Video Top el Top 10, limit puede cambiar el top

@router.get("/top_videos", response_model=List[Video])
def get_top_videos(limit: int = 10, db: Session = Depends(get_db)):
    """
    Endpoint mejorado para obtener los videos top basados en un ranking ponderado.

    Criterios de ranking:
    - Rating: 40%
    - Likes: 30%
    - Elo: 20%
    - Views: 10%
    - Dislikes: Penalización del 10%

    Parámetros:
    - limit (int): Número máximo de videos a retornar. Por defecto es 10.

    Respuesta:
    - Una lista de objetos VideoSchema que contienen los datos de los videos top.
    """
    from sqlalchemy.sql import func, select

    # Subconsulta para calcular el rating promedio de cada video
    avg_rating_subquery = (
        db.query(
            MovieRatingModel.video_id,
            func.avg(MovieRatingModel.rating).label("avg_rating")
        )
        .group_by(MovieRatingModel.video_id)
        .subquery()
    )

    # Subconsulta para calcular el ranking ponderado
    ranking_subquery = (
        db.query(
            VideoModel.id,
            (
                (func.coalesce(avg_rating_subquery.c.avg_rating, 0) * 0.4) +  # Rating: 40%
                (func.coalesce(VideoModel.likes, 0) * 0.3) +                  # Likes: 30%
                (func.coalesce(VideoModel.elo, 0) * 0.2) +                    # Elo: 20%
                (func.coalesce(VideoModel.views, 0) * 0.1) -                  # Views: 10%
                (func.coalesce(VideoModel.dislikes, 0) * 0.1)                 # Dislikes: Penalización del 10%
            ).label("ranking_score")
        )
        .outerjoin(avg_rating_subquery, VideoModel.id == avg_rating_subquery.c.video_id)
        .subquery()
    )

    # Consulta principal para obtener los videos ordenados por ranking_score
    top_videos = (
        db.query(VideoModel)
        .join(ranking_subquery, VideoModel.id == ranking_subquery.c.id)
        .order_by(ranking_subquery.c.ranking_score.desc(), VideoModel.upload_date.desc())
        .limit(limit)
        .all()
    )

    return top_videos

# Crear un video
@router.post("/", response_model=Video)
async def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    db_video = VideoModel(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.get("/videos", response_model=List[Video])
def get_videos_by_actor(
    actor_id: int = Query(..., description="ID del actor para filtrar videos"), 
    db: Session = Depends(get_db)
):
    """
    Endpoint para obtener videos asociados a un actor específico.

    Este endpoint permite a los usuarios recuperar una lista de videos relacionados
    con un actor dado, utilizando el `actor_id` proporcionado como parámetro de consulta.

    Parámetros:
    - actor_id (int): ID del actor cuyos videos se desean obtener.

    Respuesta:
    - Una lista de objetos VideoSchema que contienen los datos de los videos relacionados.

    Funcionamiento:
    1. Realiza una consulta a la base de datos uniendo las tablas `videos` y `video_actors`.
    2. Filtra los registros que coinciden con el `actor_id` proporcionado.
    3. Si no se encuentran videos, retorna un error 404.
    4. Si se encuentran videos, retorna una lista con la información solicitada.

    Ejemplo de URL:
    - `/videos?actorId=123`
    """
    # Consulta que une las tablas videos y video_actors
    videos = db.query(VideoModel).join(VideoActorModel, VideoModel.id == VideoActorModel.video_id).filter(
        VideoActorModel.actor_id == actor_id
    ).all()

    # Validar si se encontraron resultados
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found for the given actor")

    # Retornar los videos encontrados
    return videos

# Leer un video por ID
@router.get("/{video_id}", response_model=Video)
async def read_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    return video

# Leer todos los videos
@router.get("/", response_model=list[Video])
async def read_videos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    videos = db.query(VideoModel).offset(skip).limit(limit).all()
    return videos

# Actualizar un video
@router.put("/{video_id}", response_model=Video)
async def update_video(video_id: int, video: VideoUpdate, user_id: int, db: Session = Depends(get_db)):
    db_video = db.query(VideoModel).filter(VideoModel.id == video_id).first()

    if db_video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="user Not found")
    
    # Actualizar cada campo de manera personalizada si se proporciona en la solicitud
    video_data = video.model_dump(exclude_unset=True)
    coins_extra = 0
    if "title" in video_data:
        coins_extra = 100
        transactionType = "change title"
        db_video.title = video_data["title"]
    
    if "description" in video_data:
        db_video.description = video_data["description"]
    
    if "category" in video_data:
        db_video.category = video_data["category"]
    
    if "duration" in video_data:
        db_video.duration = video_data["duration"]
    
    if "thumbnail_url" in video_data:
        db_video.thumbnail_url = video_data["thumbnail_url"]
    
    if "video_url" in video_data:
        db_video.video_url = video_data["video_url"]
    
    new_views = db_video.views  # Initialize new_views with the current views

    if "views" in video_data:
        # Recalcular coins_extra basado en el nuevo valor de vistas
        coins_extra = 80 if db_video.views == 0 else 25
        transactionType = "watch video no views" if db_video.views == 0 else "watch video views"
        # Incrementar las vistas en lugar de reemplazarlas
        new_views += video_data["views"]
        db_video.views = new_views
    
    if "likes" in video_data:
        coins_extra = 10
        transactionType = "give like"
        db_video.likes += video_data["likes"]
    
    if "dislikes" in video_data:
        coins_extra = 10
        transactionType = "give like"
        db_video.dislikes += video_data["dislikes"]

    db.commit()
    db.refresh(db_video)

    # Verificar que las vistas se actualizaron correctamente
    updated_video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if updated_video.views < new_views:
        updated_video.views = new_views
        db.commit()
        db.refresh(updated_video)
    
    if coins_extra and transactionType:
        user_update = CoinsService.add_coins(
            user_id=user_id,
            coins=coins_extra,
            db=db,
            transaction_type=transactionType
        )
    return updated_video
# Eliminar un video
@router.delete("/{video_id}", response_model=bool)
async def delete_video_completely(video_id: int, db: Session = Depends(get_db)):
    """Completely delete a video and all its related entities from both database and storage.
    
    Args:
        db: SQLAlchemy database session
        video_id: ID of the video to delete
        
    Returns:
        bool: True if both operations succeeded, False otherwise
    """
    try:
        # Get the video from database with all relationships loaded if needed
        video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if not video:
            print(f"Video with ID {video_id} not found in database")
            return False

        # First delete the file from server
        # file_deleted = ssh_delete_video(video.video_url)
        # if not file_deleted:
        #     print(f"Failed to delete video file for video ID {video_id}")
        #     return False

        # Optionally delete thumbnail if stored separately
        # ssh_delete_thumbnail(video.thumbnail_url)

        # Manually delete relationships that might not be covered by cascade
        # (even though your model has cascade="all, delete-orphan" for chunks,
        # it's good practice to be explicit for important operations)

        # Delete video chunks (should be handled by cascade)
        db.query(VideoChunk).filter(VideoChunk.video_id == video_id).delete()

        # Delete video categories (should be handled by cascade)
        db.query(VideoCategory).filter(VideoCategory.video_id == video_id).delete()

        # Delete video fights (assuming this is a separate relationship)
        db.query(VideoFight).filter(
            (VideoFight.video_1_id == video_id) |
            (VideoFight.video_2_id == video_id)
        ).delete()

        # Delete video actors (assuming this is a separate relationship)
        db.query(VideoActorModel).filter(
            VideoActorModel.video_id == video_id
        ).delete()

        # Delete reels (from your model's relationship)
        db.query(ReelModel).filter(ReelModel.video_id == video_id).delete()

        # Delete ratings (from your model's relationship)
        db.query(MovieRatingModel).filter(MovieRatingModel.video_id == video_id).delete()


        # Finally delete the video itself
        db.delete(video)
        db.commit()
        
        return True

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error deleting video ID {video_id}: {str(e)}")
        return False
    except Exception as e:
        db.rollback()
        print(f"Unexpected error deleting video ID {video_id}: {str(e)}")
        return False