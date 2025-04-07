import os
import re

def clean_filename(filename):
    # Separa el nombre del archivo y la extensión
    name, ext = os.path.splitext(filename)
    
    # Reemplaza espacios por guiones bajos y elimina caracteres no permitidos (excepto punto para la extensión)
    name = name.replace(" ", "_")
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)  # Elimina todo excepto letras, números, guion y guion bajo
    
    # Se reconstruye el nombre con la extensión
    clean_name = name + ext
    return clean_name

def rename_videos(directory_path):
    try:
        # Recorre todos los archivos en el directorio especificado
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            # Verifica si el archivo es un video (por extensión común)
            if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                # Genera el nuevo nombre y renombra el archivo
                clean_name = clean_filename(filename)
                new_path = os.path.join(directory_path, clean_name)
                os.rename(file_path, new_path)
                print(f'Renamed: {filename} -> {clean_name}')
    except Exception as e:
        print(f'Error: {e}')

# Ruta a la carpeta que contiene los videos
directory_path = '/ruta/a/tu/carpeta/de/videos'  # Cambia esta ruta a la de tu carpeta
rename_videos(directory_path)

# Ruta a la carpeta que contiene los videos
directory_path = '/media/jeshu/048266e9-8c9f-4a16-9f79-0e5eaa986185'  # Cambia esta ruta a la de tu carpeta
rename_videos(directory_path)
