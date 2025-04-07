# app/core/deps.py
from datetime import datetime
from app.db.database import SessionLocal

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.models.session import Session as SessionModel
from app.core.config import settings
from app.models.session import Session as UserSession
import traceback
from app.core.deps import get_db  # Suponiendo que ya existe esta función

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_session_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserSession:
    try:

        # Intentar decodificar el token con más información
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTClaimsError as e:
            raise HTTPException(status_code=401, detail="Invalid token claims")
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=f"JWT Error: {str(e)}")

        # Extraer session_id
        session_id = payload.get("session_id")

        if session_id is None:
            raise HTTPException(status_code=401, detail="Session ID not found in token")

        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.end_time < datetime.now():
            raise HTTPException(status_code=401, detail="Session has expired")
        
        return session_id

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")