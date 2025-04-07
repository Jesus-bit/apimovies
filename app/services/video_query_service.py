from sqlalchemy.orm import Session
from app.models.video import VideoModel, OrientationType
from sqlalchemy.sql.expression import func
from typing import List

class VideoQueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_random_videos(self, skip: int, limit: int, orientation: OrientationType = None) -> List[VideoModel]:
        # Construir la consulta base
        videos_query = self.db.query(VideoModel)

        # Filtrar por orientación si se proporciona
        if orientation:
            videos_query = videos_query.filter(VideoModel.orientation == orientation)

        # Obtener el número total de videos
        total_videos = videos_query.count()

        # Asegurarse de que skip no sea mayor que el número total de videos
        if skip >= total_videos:
            return []

        # Calcular cuántos videos aleatorios necesitamos
        videos_needed = min(limit, total_videos - skip)

        # Generar una consulta que seleccione videos aleatorios
        return (
            videos_query.order_by(func.random())
            .offset(skip)
            .limit(videos_needed)
            .all()
        )