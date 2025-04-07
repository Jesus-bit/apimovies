from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.video_chunk import VideoChunk
from app.schemas.video_chunk import VideoChunkCreate, VideoChunkResponse

router = APIRouter(prefix="/video_chunks", tags=["video_chunks"])

@router.post("/", response_model=VideoChunkResponse)
def create_chunk(chunk: VideoChunkCreate, db: Session = Depends(get_db)):
    new_chunk = VideoChunk(**chunk.dict())
    db.add(new_chunk)
    db.commit()
    db.refresh(new_chunk)
    return new_chunk

@router.get("/{chunk_id}", response_model=VideoChunkResponse)
def get_chunk(chunk_id: int, db: Session = Depends(get_db)):
    chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk

@router.get("/video/{video_id}", response_model=list[VideoChunkResponse])
def get_chunks_by_video(video_id: int, db: Session = Depends(get_db)):
    chunks = db.query(VideoChunk).filter(VideoChunk.video_id == video_id).all()
    return chunks

@router.put("/{chunk_id}", response_model=VideoChunkResponse)
def update_chunk(chunk_id: int, chunk_data: VideoChunkCreate, db: Session = Depends(get_db)):
    chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    for key, value in chunk_data.dict().items():
        setattr(chunk, key, value)
    db.commit()
    db.refresh(chunk)
    return chunk

@router.delete("/{chunk_id}")
def delete_chunk(chunk_id: int, db: Session = Depends(get_db)):
    chunk = db.query(VideoChunk).filter(VideoChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    db.delete(chunk)
    db.commit()
    return {"message": "Chunk deleted successfully"}
