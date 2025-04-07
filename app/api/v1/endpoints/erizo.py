from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.erizo import Erizo as ErizoModel
from app.schemas.erizo import ErizoCreate, ErizoUpdate, ErizoResponse
from app.models.user import User
from app.services.coins_service import CoinsService
from datetime import datetime

router = APIRouter(prefix="/erizos", tags=["erizos"])

# Obtener todos los erizos
@router.get("/", response_model=list[ErizoResponse])
def get_erizos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    erizos = db.query(ErizoModel).offset(skip).limit(limit).all()
    return erizos

# Crear un erizo
@router.post("/", response_model=ErizoResponse)
def create_erizo(erizo: ErizoCreate, db: Session = Depends(get_db)):
    COST_ERIZO = 2500  # Costo fijo por erizo

    # Verificar si el usuario existe
    user = db.query(User).filter(User.id == erizo.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar si el usuario tiene suficientes coins
    if user.coins < COST_ERIZO:
        raise HTTPException(status_code=400, detail="Insufficient coins to buy an erizo")

    # Verificar si el usuario ya tiene 3 erizos
    if user.count_erizos() >= 3:
        raise HTTPException(status_code=400, detail="User already has maximum number of erizos (3)")

    # Restar coins del usuario
    CoinsService.make_purchase(
        user_id=erizo.user_id,
        cost=COST_ERIZO,
        db=db,
        transaction_type="buy erizo"
    )

    # Crear el erizo con la fecha y hora actual del servidor
    db_erizo = ErizoModel(
        **erizo.dict(exclude={"date_acquisition"}),
        date_acquisition=datetime.utcnow()
    )
    db.add(db_erizo)
    db.commit()
    db.refresh(db_erizo)

    return db_erizo

# Obtener un erizo por ID
@router.get("/{erizo_id}", response_model=ErizoResponse)
def get_erizo(erizo_id: int, db: Session = Depends(get_db)):
    erizo = db.query(ErizoModel).filter(ErizoModel.id == erizo_id).first()
    if not erizo:
        raise HTTPException(status_code=404, detail="Erizo no encontrado")
    return erizo

# Actualizar un erizo
@router.patch("/{erizo_id}", response_model=ErizoResponse)
def update_erizo(erizo_id: int, erizo_update: ErizoUpdate, db: Session = Depends(get_db)):
    erizo = db.query(ErizoModel).filter(ErizoModel.id == erizo_id).first()
    if not erizo:
        raise HTTPException(status_code=404, detail="Erizo no encontrado")
    
    for key, value in erizo_update.dict(exclude_unset=True).items():
        setattr(erizo, key, value)
    
    db.commit()
    db.refresh(erizo)
    return erizo

# Eliminar un erizo
@router.delete("/{erizo_id}", response_model=dict)
def delete_erizo(erizo_id: int, db: Session = Depends(get_db)):
    erizo = db.query(ErizoModel).filter(ErizoModel.id == erizo_id).first()
    if not erizo:
        raise HTTPException(status_code=404, detail="Erizo no encontrado")
    
    db.delete(erizo)
    db.commit()
    return {"detail": "Erizo eliminado exitosamente"}

# Obtener erizos por user_id
@router.get("/user/{user_id}", response_model=list[ErizoResponse])
def get_erizos_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    erizos = db.query(ErizoModel).filter(ErizoModel.user_id == user_id).order_by(ErizoModel.date_acquisition.desc()).limit(3).all()
    
    if len(erizos) < 3:
        inactive_erizos = db.query(ErizoModel).filter(ErizoModel.user_id == None).order_by(ErizoModel.date_acquisition.desc()).limit(3 - len(erizos)).all()
        erizos.extend(inactive_erizos)
    
    return erizos