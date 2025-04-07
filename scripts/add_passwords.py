import os
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import hash_password
from app.db.database import get_db

def add_passwords_to_users():
    db: Session = next(get_db())  # Obtener la sesión de la base de datos

    # Obtén todos los usuarios
    users = db.query(User).filter(User.hashed_password == None).all()

    for user in users:
        # Asignar una contraseña hash a cada usuario
        password = "password"  # Cambia esto por una lógica de generación segura
        user.hashed_password = hash_password(password)
        print(f"Contraseña asignada al usuario {user.username}: {password}")  # Opcional, para depuración

    db.commit()
    print("Contraseñas añadidas a todos los usuarios.")
    
if __name__ == "__main__":
    add_passwords_to_users()
