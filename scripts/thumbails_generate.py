import os
from moviepy.editor import VideoFileClip
from PIL import Image

def extract_frame(video_path, percentage):
    try:
        with VideoFileClip(video_path) as video:
            frame_time = video.duration * percentage
            frame = video.get_frame(frame_time)
            return Image.fromarray(frame)
    except Exception as e:
        print(f"Error extracting frame at {percentage*100}% for {video_path}: {e}")
        return None

def create_collage(frames, output_path, resolution):
    try:
        collage = Image.new("RGB", (resolution[0] * 2, resolution[1] * 2))

        for i, frame in enumerate(frames):
            if frame is not None:
                frame = frame.resize(resolution)
                x = (i % 2) * resolution[0]
                y = (i // 2) * resolution[1]
                collage.paste(frame, (x, y))

        collage.save(output_path)
    except Exception as e:
        print(f"Error creating collage at {output_path}: {e}")

def process_videos(directory_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            video_path = os.path.join(directory_path, filename)
            collage_name = f"{os.path.splitext(filename)[0]}_collage.jpg"
            collage_path = os.path.join(output_folder, collage_name)

            # Saltar si el collage ya existe
            if os.path.exists(collage_path):
                print(f"Collage for {filename} already exists. Skipping...")
                continue

            try:
                with VideoFileClip(video_path) as video:
                    resolution = (video.size[0] // 2, video.size[1] // 2)

                    # Extrae fotogramas de los porcentajes deseados
                    frames = [
                        extract_frame(video_path, 0.10),
                        extract_frame(video_path, 0.25),
                        extract_frame(video_path, 0.50),
                        extract_frame(video_path, 0.90)
                    ]

                    # Crea el collage
                    create_collage(frames, collage_path, resolution)
                    print(f"Collage created for {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Ruta de la carpeta que contiene los videos y donde se guardarán los collages
directory_path = '/media/jeshu/048266e9-8c9f-4a16-9f79-0e5eaa986185'  # Cambia esta ruta a la de tu carpeta de videos
output_folder = '/home/jeshu/Descargas/thumbails'   # Cambia esta ruta a la de tu carpeta de salida
process_videos(directory_path, output_folder)
