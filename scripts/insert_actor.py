import csv
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from app.db.database import engine
from app.models.actor import Actor

def add_missing_columns():
    inspector = inspect(engine)
    existing_columns = [column['name'] for column in inspector.get_columns('actors')]
    
    with engine.connect() as connection:
        if 'nationality' not in existing_columns:
            connection.execute(text("ALTER TABLE actors ADD COLUMN nationality VARCHAR;"))
            print("Columna 'nationality' añadida a la tabla 'actors'.")
        else:
            print("La columna 'nationality' ya existe en la tabla 'actors'.")
        
        if 'profile_url' not in existing_columns:
            connection.execute(text("ALTER TABLE actors ADD COLUMN profile_url VARCHAR;"))
            print("Columna 'profile_url' añadida a la tabla 'actors'.")
        else:
            print("La columna 'profile_url' ya existe en la tabla 'actors'.")
        
        connection.commit()

def insert_actors_from_csv(file_path: str):
    # Crear una sesión de base de datos
    db = Session(engine)

    try:
        # Abrir y leer el archivo CSV
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            # Iterar sobre cada fila en el CSV
            for row in csv_reader:
                # Crear un nuevo objeto Actor
                new_actor = Actor(
                    name=row['name'],
                    age=int(row['age']) if row['age'] else None,
                    nationality=row['nationality']
                )
                
                # Añadir el nuevo actor a la sesión
                db.add(new_actor)
            
            # Commit de todos los cambios a la base de datos
            db.commit()
            print("Datos insertados exitosamente.")
    
    except Exception as e:
        print(f"Error al insertar datos: {str(e)}")
        db.rollback()
    
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    add_missing_columns()
    csv_file_path = "./Actrizes.csv"  # Reemplaza esto con la ruta real de tu archivo CSV
    insert_actors_from_csv(csv_file_path)