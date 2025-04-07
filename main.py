# Version 3.0
import os
import paramiko
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware de CORS
from app.db.database import Base, engine
from app.api.v1.endpoints import (
    users,
    video,
    actor,
    pdf,
    reel,
    session,
    movie_ratings,
    pdf_session,
    search,
    video_actor,
    video_session,
    user_video_history,
    video_fights,
    random_video,
    login,
    level,
    categories,
    video_category,
    statistics,
    video_chunk,
    erizo,
    transactions
)
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: connect to the Raspberry Pi and mount the USB
    print("Iniciando la API y montando la unidad USB...")
    yield
    # Optionally, you can add shutdown logic here
    print("Apagando la API y desmontando la unidad USB...")

# Crear la instancia de FastAPI
app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Configuración del middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las fuentes (puedes especificar dominios)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)


# Registrar los routers
app.include_router(users.router)
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(video.router, prefix="/video", tags=["video"])
app.include_router(actor.router, prefix="/actor", tags=["actor"])
app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
app.include_router(reel.router, prefix="/reel", tags=["reel"])
app.include_router(level.router)
# app.include_router(abtest.router, prefix="/abtest", tags=["abtest"])
app.include_router(categories.router)
app.include_router(video_category.router)
app.include_router(statistics.router)
app.include_router(erizo.router)
app.include_router(transactions.router)
app.include_router(pdf_session.router, prefix="/pdf_session", tags=["pdf_session"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(video_actor.router, prefix="/video_actor", tags=["video_actor"])
app.include_router(video_session.router, prefix="/video_session", tags=["video_session"])
app.include_router(user_video_history.router)
app.include_router(video_fights.router, prefix="/video_fights", tags=["video_fights"])
app.include_router(video_chunk.router)
app.include_router(movie_ratings.router, prefix="/movie_ratings", tags=["movie_ratings"])
app.include_router(random_video.router, prefix="/random", tags=["random_video"])
app.include_router(login.router, prefix="/login", tags=["login"])

# Punto de inicio (opcional)
@app.get("/")
def read_root():
    return {"message": "API is running"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
