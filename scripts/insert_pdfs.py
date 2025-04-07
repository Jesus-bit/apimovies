import os
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models.pdf import PDF, PageURL
from app.db.database import Base, SessionLocal
from app.core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_pdfs_and_urls(directory_path):
    """
    Inserta PDFs y sus URLs de página en la base de datos.
    
    Args:
        directory_path (str): Ruta del directorio que contiene las subcarpetas de PDFs
    """
    # Crear motor de base de datos y sesión
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Recorrer las subcarpetas
        for subfolder in os.listdir(directory_path):
            subfolder_path = os.path.join(directory_path, subfolder)
            
            # Verificar que sea una carpeta
            if os.path.isdir(subfolder_path):
                # El nombre de la carpeta será el título del PDF
                pdf_title = subfolder
                
                # Buscar archivos .txt con URLs
                url_files = [f for f in os.listdir(subfolder_path) if f.endswith('.txt')]
                
                if url_files:
                    # Tomar el primer archivo de URLs
                    url_file_path = os.path.join(subfolder_path, url_files[0])
                    
                    # Buscar archivos PDF
                    pdf_files = [f for f in os.listdir(subfolder_path) if f.endswith('.pdf')]
                    
                    if pdf_files:
                        # Tomar el primer archivo PDF
                        pdf_file = pdf_files[0]
                        pdf_file_path = os.path.join(subfolder_path, pdf_file)
                        
                        # Crear registro de PDF
                        pdf = PDF(
                            title=pdf_title,
                            file_path=pdf_file_path
                        )
                        db.add(pdf)
                        db.commit()
                        db.refresh(pdf)
                        
                        # Leer URLs del archivo de texto
                        with open(url_file_path, 'r', encoding='utf-8') as f:
                            urls = f.readlines()
                        
                        # Insertar URLs de páginas
                        for page_number, url in enumerate(urls, 1):
                            url = url.strip()  # Eliminar espacios en blanco
                            if url:  # Ignorar líneas vacías
                                page_url = PageURL(
                                    pdf_id=pdf.id,
                                    page_number=page_number,
                                    url=url
                                )
                                db.add(page_url)
                        
                        db.commit()
                        
                        logger.info(f"Insertado PDF: {pdf_title} con {len(urls)} URLs")
                    else:
                        logger.warning(f"No se encontró archivo PDF en la carpeta {subfolder}")
                else:
                    logger.warning(f"No se encontró archivo de URLs en la carpeta {subfolder}")
        
        logger.info("Proceso de inserción completado")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error durante la inserción: {e}")
    
    finally:
        db.close()

# Ejemplo de uso
if __name__ == "__main__":
    # Reemplazar con la ruta de tu directorio
    DIRECTORY_PATH = "/ruta/a/tu/directorio/de/pdfs"
    insert_pdfs_and_urls(DIRECTORY_PATH)