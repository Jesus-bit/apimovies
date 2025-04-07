# app/models/transaction.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class UserTransaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(Enum("buy erizo", "login", "watch video views", "watch video no views",
                                 "rating video", "give like", "add actor video", "vote", "change title",
                                 name="transaction_types"))
    coins_amount = Column(Integer)
    movement_type = Column(Enum("in", "out", name="movement_types"))
    date = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="transactions")