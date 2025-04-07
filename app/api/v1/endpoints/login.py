from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.schemas.user import UserLogin
from app.services.coins_service import CoinsService
from app.models.user import User
from app.models.level import Level
from app.models.session import Session as UserSession
from app.utils.auth import authenticate_user
from app.db.database import get_db  # Asume que tienes un método para obtener la sesión de la base de datos
from jose import jwt, JWTError  # Necesitarás instalar python-jose
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core import deps
import traceback



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(user_id: int, username: str, session_id: int) -> str:
    try:
        # Calcular tiempo de expiración
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Preparar payload
        to_encode = {
            "sub": str(user_id),
            "username": username,
            "session_id": session_id,
            "exp": int(expire.timestamp())  # Convertir a timestamp Unix
        }
        
        # Codificar token
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        
        return token
    
    except Exception as e:
        raise

def update_user_level(user: User, db: Session):
    current_level = db.query(Level).filter(Level.level_id == user.level_id).first()
    if not current_level:
        return

    # Check for level up
    while True:
        next_level = db.query(Level).filter(Level.required_points > current_level.required_points).order_by(Level.required_points.asc()).first()
        if next_level and user.coins >= next_level.required_points:
            user.level_id = next_level.level_id
            current_level = next_level
            db.commit()
            db.refresh(user)
        else:
            break

    # Check for level down
    while True:
        previous_level = db.query(Level).filter(Level.required_points < current_level.required_points).order_by(Level.required_points.desc()).first()
        if previous_level and user.coins < current_level.required_points:
            user.level_id = previous_level.level_id
            current_level = previous_level
            db.commit()
            db.refresh(user)
        else:
            break

@router.post("/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Autenticar al usuario
    authenticated_user = authenticate_user(user.username, user.password, db)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Crear una nueva sesión
    new_session = UserSession(
        user_id=authenticated_user.id,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Generar token JWT con el session_id incluido
    token = create_access_token(
        user_id=authenticated_user.id,
        username=authenticated_user.username,
        session_id=new_session.id
    )
    coins_extra = 30

    if coins_extra:
        user_update = CoinsService.add_coins(
            user_id=authenticated_user.id,
            coins=coins_extra, db=db,
            transaction_type="login"
        )
    update_user_level(authenticated_user, db)
    return {
        "ok": True,
        "token": token,
        "session_id": new_session.id,  # Añadir ID de sesión
        "user": {
            "id": authenticated_user.id,
            "username": authenticated_user.username,
            "email": authenticated_user.email
        }
    }

@router.post("/logout")
def logout_user(
    session_id: int = Depends(deps.get_session_id),  # get_session_id debe retornar solo el ID
    db: Session = Depends(get_db)
):

    # Buscar la sesión en la base de datos
    current_session = db.query(UserSession).filter(UserSession.id == session_id).first()

    if not current_session:
        return {"error": "Sesión no encontrada"}, 404

    # Invalidar la sesión actual
    current_session.is_active = False
    db.commit()

    return {"message": "Logged out successfully"}
