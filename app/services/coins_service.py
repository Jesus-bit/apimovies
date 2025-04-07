from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.models.transaction import UserTransaction as TransactionModel  # Asumiendo que existe este modelo
from fastapi import HTTPException
from datetime import datetime
from app.schemas.transaction import TransactionType, MovementType, TransactionCreate

class CoinsService:
    @staticmethod
    def add_coins(user_id: int, coins: int, db: Session, transaction_type: TransactionType):
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Crear la transacción
        transaction = TransactionModel(
            user_id=user_id,
            transaction_type=transaction_type,
            coins_amount=coins,
            movement_type=MovementType.in_ if coins > 0 else MovementType.out,
            date=datetime.now()
        )
        
        # Actualizar coins del usuario
        user.coins += coins
        
        # Guardar cambios
        db.add(transaction)
        db.commit()
        db.refresh(user)
        db.refresh(transaction)
        
        return {"user": user, "transaction": transaction}

    @staticmethod
    def make_purchase(user_id: int, cost: int, transaction_type: TransactionType, db: Session):
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.coins < cost:
            raise HTTPException(status_code=400, detail="Insufficient coins")
            
        # Crear la transacción
        transaction = TransactionModel(
            user_id=user_id,
            transaction_type=transaction_type,
            coins_amount=cost,
            movement_type=MovementType.out,
            date=datetime.now()
        )
        
        # Actualizar coins del usuario
        user.coins -= cost
        
        # Guardar cambios
        db.add(transaction)
        db.commit()
        db.refresh(user)
        db.refresh(transaction)
        
        return {"user": user, "transaction": transaction}

    @staticmethod
    def get_user_transactions(user_id: int, db: Session):
        transactions = db.query(TransactionModel)\
            .filter(TransactionModel.user_id == user_id)\
            .order_by(TransactionModel.date.desc())\
            .all()
        return transactions