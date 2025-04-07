from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class Level(Base):
    __tablename__ = 'levels'

    level_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    required_points = Column(Integer, nullable=False)
    medal_url = Column(String(255), nullable=False)

    # Relación uno a muchos con User
    users = relationship("User", back_populates="level")