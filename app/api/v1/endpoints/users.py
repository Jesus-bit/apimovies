# app/api/v1/endpoints/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.models.user import User
from app.utils.auth import hash_password
from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

# 1. Crear usuario (Create)
@router.post("/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe por correo electrónico
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Cifrar la contraseña antes de guardarla
    hashed_password = hash_password(user.hashed_password)

    # Crear el nuevo usuario con la contraseña cifrada
    db_user = User(
        username=user.username,
        email=user.email,
        birthdate=user.birthdate,
        gender=user.gender,
        location=user.location,
        subscription=user.subscription,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 2. Leer usuario por ID (Read)
@router.get("/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 3. Actualizar usuario (Update)
@router.put("/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):

    # Obtén el usuario de la base de datos
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Excluir campos no enviados y aplicar actualizaciones
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # Guardar cambios en la base de datos
    db.commit()
    db.refresh(db_user)

    return db_user

# 4. Eliminar usuario (Delete)
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}

# 5. Leer todos los usuarios
@router.get("/", response_model=List[UserInDB])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
# 6. Leer número de coins de un usuario por ID
@router.get("/coins/{user_id}", response_model=int)
def read_user_coins(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.coins