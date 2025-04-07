import os
import re
import sys
from pathlib import Path

# Añadir el directorio raíz al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models.pdf import PDF, PageURL
from app.db.database import Base
from app.core.config import settings
import logging
import traceback

# Configurar logging más detallado
def setup_logger():
    # Configuración base del logger
    logging.basicConfig(
        level=logging.DEBUG,  # Cambiado a DEBUG para obtener más detalles
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Log a consola
            logging.StreamHandler(sys.stdout),
            # Log a archivo
            logging.FileHandler('pdf_insertion.log', encoding='utf-8')
        ]
    )
    
    # Logger específico para este módulo
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    return logger

# Inicializar logger
logger = setup_logger()

# Inicializa la conexión con la base de datos
try:
    engine = create_engine(settings.DATABASE_URL)
    logger.info(f"Conexión a base de datos establecida con URL: {settings.DATABASE_URL}")
except Exception as e:
    logger.error(f"Error al establecer conexión a base de datos: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Asegúrate de que las tablas están creadas
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas o verificadas correctamente")
except Exception as e:
    logger.error(f"Error al crear tablas de base de datos: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

# Directorio raíz donde se encuentran las carpetas de PDFs
PDF_ROOT_DIR = "/home/jeshu/Imágenes/manga/Super-Melons-Archive-English-Edition/Naruto"  # Ajusta esto a tu directorio real

def custom_sort_key(filename):
    """
    Función de ordenamiento personalizada que compara caracter por caracter.
    """
    logger.debug(f"Procesando nombre de archivo para ordenamiento: {filename}")
    
    def char_type(char):
        if char.isdigit():
            return 1  # Los dígitos tienen prioridad sobre letras
        elif char.isalpha():
            return 2  # Las letras vienen después de los dígitos
        else:
            return 0  # Otros caracteres (como puntos) van primero
    
    def tokenize(s):
        tokens = []
        current_token = ""
        current_type = None
        
        for char in s:
            token_type = char_type(char)
            
            if current_type is not None and token_type != current_type:
                tokens.append((current_type, current_token))
                current_token = char
                current_type = token_type
            else:
                current_token += char
                current_type = token_type
        
        if current_token:
            tokens.append((current_type, current_token))
        
        logger.debug(f"Tokens para {filename}: {tokens}")
        return tokens
    
    tokens = tokenize(filename)
    
    sort_key = []
    for token_type, token in tokens:
        if token_type == 1:  # Es un número
            sort_key.append((token_type, int(token)))
        else:
            sort_key.append((token_type, token))
    
    logger.debug(f"Clave de ordenamiento para {filename}: {sort_key}")
    return sort_key

def insert_pdfs():
    logger.info("Iniciando proceso de inserción de PDFs")
    
    try:
        with Session(engine) as session:
            # Verificar si el directorio existe
            if not os.path.exists(PDF_ROOT_DIR):
                logger.error(f"El directorio no existe: {PDF_ROOT_DIR}")
                return
            
            logger.info(f"Procesando directorio: {PDF_ROOT_DIR}")
            
            # Listar contenidos del directorio
            try:
                folders = os.listdir(PDF_ROOT_DIR)
                logger.info(f"Carpetas encontradas: {folders}")
            except Exception as e:
                logger.error(f"Error al listar directorio: {e}")
                logger.error(traceback.format_exc())
                return
            
            for folder_name in folders:
                folder_path = os.path.join(PDF_ROOT_DIR, folder_name)
                
                # Verificar que sea un directorio
                if not os.path.isdir(folder_path):
                    logger.warning(f"No es un directorio: {folder_path}")
                    continue
                
                logger.info(f"Procesando carpeta: {folder_name}")
                
                # El nombre de la carpeta es el título del PDF
                title = folder_name
                
                # Recopilar imágenes de la carpeta
                try:
                    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))]
                    logger.info(f"Archivos de imagen encontrados en {folder_name}: {image_files}")
                    
                    # Ordenar imágenes con la función personalizada
                    image_files.sort(key=custom_sort_key)
                    logger.info(f"Archivos de imagen ordenados: {image_files}")
                except Exception as e:
                    logger.error(f"Error al procesar imágenes en {folder_name}: {e}")
                    logger.error(traceback.format_exc())
                    continue
                
                # Establecer la URL de la portada
                cover_url = f"/pdfs/{folder_name}/{image_files[0]}" if image_files else None
                logger.info(f"URL de portada: {cover_url}")
                
                # Crear objeto PDF
                try:
                    pdf = PDF(
                        title=title,
                        file_path=folder_path,
                        cover_url=cover_url
                    )
                    session.add(pdf)
                    session.flush()
                    logger.info(f"PDF creado: {title} (ID: {pdf.id})")
                except Exception as e:
                    logger.error(f"Error al crear objeto PDF: {e}")
                    logger.error(traceback.format_exc())
                    continue
                
                # Añadir URLs de páginas
                try:
                    for idx, file_name in enumerate(image_files, 1):
                        page_url = PageURL(
                            pdf_id=pdf.id,
                            page_number=idx,
                            url=f"/pdfs/{folder_name}/{file_name}"
                        )
                        session.add(page_url)
                    
                    session.commit()
                    logger.info(f"Páginas insertadas para {title}: {len(image_files)} páginas")
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error al insertar páginas para {title}: {e}")
                    logger.error(traceback.format_exc())
    
    except Exception as e:
        logger.error(f"Error general en la inserción de PDFs: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        logger.info("Script de inserción de PDFs iniciado")
        insert_pdfs()
        logger.info("Script de inserción de PDFs completado exitosamente")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        logger.error(traceback.format_exc())