# app/api/v1/endpoints/actor.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.actor import Actor, ActorCreate, ActorUpdate
from app.models.actor import Actor as ActorModel
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=Actor)
def create_actor(actor: ActorCreate, db: Session = Depends(get_db)):
    # Convertir profile_url a str si no es None
    actor_data = actor.dict()  # Convertir el ActorCreate a un diccionario
    if actor_data.get("profile_url"):
        actor_data["profile_url"] = str(actor_data["profile_url"])  # Asegurarse de que sea un str
    
    new_actor = ActorModel(**actor_data)  # Crear el objeto de SQLAlchemy
    db.add(new_actor)
    db.commit()
    db.refresh(new_actor)
    return new_actor

@router.get("/{actor_id}", response_model=Actor)
def read_actor(actor_id: int, db: Session = Depends(get_db)):
    actor = db.query(ActorModel).filter(ActorModel.id == actor_id).first()  # Cambiado de actor_id a id
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")
    return actor


@router.get("/", response_model=List[Actor])
def read_actors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    actors = db.query(ActorModel).offset(skip).limit(limit).all()
    return actors

@router.put("/{actor_id}", response_model=Actor)
def update_actor(actor_id: int, actor: ActorUpdate, db: Session = Depends(get_db)):
    db_actor = db.query(ActorModel).filter(ActorModel.id == actor_id).first()  # Cambiado de actor_id a id
    if db_actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")
    
    for key, value in actor.model_dump(exclude_unset=True).items():
        # Convierte a string si el campo es 'profile_url'
        if key == "profile_url":
            value = str(value)  # Asegúrate de que value sea una cadena
        setattr(db_actor, key, value)
    
    db.commit()
    db.refresh(db_actor)
    return db_actor

@router.delete("/{actor_id}", response_model=Actor)
def delete_actor(actor_id: int, db: Session = Depends(get_db)):
    actor = db.query(ActorModel).filter(ActorModel.id == actor_id).first()  # Cambiado de actor_id a id
    if actor is None:
        raise HTTPException(status_code=404, detail="Actor not found")
    db.delete(actor)
    db.commit()
    return actor