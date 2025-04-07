# app/models/actor.py
from sqlalchemy import Column, Integer, String
from app.db.database import Base

class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    nationality = Column(String, nullable=True)  # Nuevo campo nacionalidad
    profile_url = Column(String, nullable=True)  # Nuevo campo profile_url (URL del perfil)
