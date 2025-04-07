# app/models/erizo.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Erizo(Base):
    __tablename__ = "erizos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    state = Column(Enum("active", "used", name="erizo_states"))
    date_acquisition = Column(DateTime, default=datetime.now())
    user = relationship("User", back_populates="erizos")