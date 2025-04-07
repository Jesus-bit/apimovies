# app/models/user.py

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.erizo import Erizo
from app.models.transaction import UserTransaction
from app.models.level import Level

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    birthdate = Column(Date, nullable=False)
    gender = Column(String, nullable=True)
    location = Column(String, nullable=True)
    subscription = Column(String, nullable=False, default="Free")
    hashed_password = Column(String, nullable=True)

    coins = Column(Integer, nullable=False, default=0)  # Nueva propiedad
    avatar_url = Column(String, nullable=True)  # Nueva propiedad
    erizos = relationship("Erizo", back_populates="user")
    transactions = relationship("UserTransaction", back_populates="user")

    def count_erizos(self):
        return len([erizo for erizo in self.erizos if erizo.state == "active"])

    level_id = Column(Integer, ForeignKey('levels.level_id'), nullable=False, default=1)
    level = relationship("Level", back_populates="users")

    fights = relationship("VideoFight", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    movie_ratings = relationship("MovieRating", back_populates="user", lazy='selectin')

    # Relación uno a muchos con PDFSession
    pdf_sessions = relationship("PDFSession", back_populates="user")
    # Relación uno a muchos con Search
    searches = relationship("Search", back_populates="user")
    # Relaciones con otros modelos
    video_histories = relationship("UserVideoHistory", back_populates="user")
