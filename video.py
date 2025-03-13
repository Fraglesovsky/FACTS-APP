import os
import requests
import subprocess
import shutil
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, AudioFileClip
from moviepy.video.fx.all import crop
#from custom_resize import custom_resize  # Zakomentowane, jeśli nie używasz custom_resize
from moviepy.video.fx.resize import resize
from facts_generator import extract_keywords
from image import check_and_adjust_image


load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def combine_clips(image_path, video_paths, audio_path, image_duration=2, target_resolution=(1080, 1920)):
    """
    Łączy obraz (jako klip wideo) z wieloma klipami wideo i dodaje dźwięk.
    """

    # Check if all required files exist before proceeding
    if not os.path.exists(image_path):
        print("Image file not found!")
        return None
    if not all(os.path.exists(video_path) for video_path in video_paths):
        print("One or more video files not found!")
        return None
    if not os.path.exists(audio_path):
        print("Audio file not found!")
        return None

    # Dodaj ścieżkę audio
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration

    # Dopasowanie obrazu do proporcji 6:19 (skalowanie zamiast przycinania)
    image_clip = (ImageClip(image_path)
                  .set_duration(image_duration)
                  .resize(height=target_resolution[1]))

    # Dopasowanie filmów do proporcji 6:19 (skalowanie zamiast przycinania)
    video_clips = []
    for path in video_paths:
        try:
            clip = VideoFileClip(path).resize(height=target_resolution[1])
            video_clips.append(clip)
        except Exception as e:
            print(f"Błąd podczas ładowania klipu {path}: {e}")

    if not video_clips:
        raise ValueError("Brak poprawnych klipów wideo.")

    # Podziel pozostały czas równomiernie na wszystkie filmy
    remaining_duration = audio_duration - image_duration
    num_videos = len(video_clips)
    time_per_video = remaining_duration / num_videos

    adjusted_clips = []
    for clip in video_clips:
        adjusted_clip = clip.subclip(0, min(time_per_video, clip.duration))
        adjusted_clips.append(adjusted_clip)

    # Połącz obraz i filmy
    final_clip = concatenate_videoclips([image_clip] + adjusted_clips, method="compose")
    
    # Upewnij się, że wymiary finalnego klipu są liczbami parzystymi
    final_clip = ensure_even_dimensions(final_clip)

    final_clip = final_clip.set_audio(audio_clip).set_duration(audio_clip.duration)

    # Zapisz wynikowy film z poprawnymi ustawieniami kodowania
    output_path = "Final_Video/final_combined_video.mp4"
    final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec='aac', ffmpeg_params=['-pix_fmt', 'yuv420p'])

    return output_path


def search_video(query, count=2, min_width=600, min_height=1067, size='large', default_video=None):
    """
    Wyszukuje wiele filmów w Pexels API, zapisuje je jako pliki lokalne i konwertuje do MP4.
    
    :param query: Tekst do wyszukiwania filmu.
    :param count: Liczba filmów do pobrania (domyślnie 2).
    :param min_width: Minimalna szerokość w pikselach dla zwróconych filmów.
    :param min_height: Minimalna wysokość w pikselach dla zwróconych filmów.
    :param size: Rozmiar filmu (np. 'large', 'medium', 'small').
    :param default_video: Ścieżka do domyślnego filmu w przypadku braku wyników.
    :return: Lista ścieżek do przekonwertowanych filmów.
    """
    # Wyodrębnij kluczowe słowa z zapytania
    keywords = extract_keywords(query)
    search_query = " ".join(keywords[:3])
    
    url = f"https://api.pexels.com/videos/search?query={search_query}&per_page={count}"
    headers = {"Authorization": PEXELS_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data["videos"]:
            print(f"Brak wyników dla zapytania: {search_query}")
            return [default_video] if default_video else []  # Zwróć domyślny film lub pustą listę

        folder_path = "Final_Video"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        video_paths = []
        for i, video in enumerate(data["videos"][:count]):
            # Przeglądaj wszystkie dostępne wersje plików wideo
            selected_file = None
            for file in video["video_files"]:
                if file["width"] >= min_width and file["height"] >= min_height:
                    selected_file = file
                    break  # Znaleziono odpowiedni plik, przerywamy pętlę

            if not selected_file:
                print(f"Brak filmu o wymaganej rozdzielczości dla zapytania '{search_query}'.")
                continue

            video_url = selected_file["link"]
            
            # Pobierz film
            video_path = os.path.join(folder_path, f"{search_query.replace(' ', '_')}_{i+1}.mp4")
            try:
                video_data = requests.get(video_url, stream=True)
                video_data.raise_for_status()  # Sprawdź, czy pobieranie się powiodło
                with open(video_path, "wb") as handler:
                    for chunk in video_data.iter_content(chunk_size=8192):
                        handler.write(chunk)
                print(f"Film pobrany: {video_path}")
                video_paths.append(video_path)  # Dodaj ścieżkę do listy `video_paths`
            except requests.exceptions.RequestException as e:
                print(f"Błąd podczas pobierania filmu: {e}")
                continue

            # Konwertuj film
            converted_video_path = os.path.join(folder_path, f"{search_query.replace(' ', '_')}_{i+1}_converted.mp4")
            converted_video = convert_video(video_path, converted_video_path)
            if converted_video:
                video_paths.append(converted_video)  # Dodaj przekonwertowany film do listy `video_paths`
            else:
                print(f"Nie udało się przekonwertować filmu: {video_path}")

        return video_paths if video_paths else [default_video] if default_video else []
    else:
        raise ValueError(f"Błąd podczas wyszukiwania filmu: {response.status_code}, {response.text}")

    

def convert_video(input_path, output_path):
    """Konwertuje film do formatu MP4 z kodekami H.264 i AAC."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"  # Update this path to the correct location of ffmpeg.exe

    command = [
        ffmpeg_path,
        '-y',  # Automatycznie nadpisuj istniejące pliki
        '-i', input_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-movflags', 'faststart',  # Optymalizacja dla odtwarzania online
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Film przekonwertowany: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas konwersji filmu: {e}")
        print(f"Wyjście z ffmpeg: {e.stderr.decode('utf-8')}")
        return None
    return output_path

def check_and_adjust_video(video_path, output_path, target_resolution=(1080, 1920)):
    """
    Sprawdza proporcje filmu i dopasowuje go do proporcji 9:16 (1080x1920) tylko jeśli jest to konieczne.
    
    :param video_path: Ścieżka do oryginalnego filmu.
    :param output_path: Ścieżka do zapisanego filmu.
    :param target_resolution: Docelowa rozdzielczość (szerokość, wysokość).
    """
    clip = VideoFileClip(video_path)
    width, height = clip.size

    # Oblicz proporcje
    aspect_ratio = width / height
    target_aspect_ratio = target_resolution[0] / target_resolution[1]

    if abs(aspect_ratio - target_aspect_ratio) < 0.01:
        print(f"Film {video_path} już ma proporcje 9:16.")
        clip.write_videofile(output_path, fps=clip.fps, codec="libx264", audio_codec="aac")
        return output_path  # Nie zmieniaj filmu

    # Przytnij film
    if aspect_ratio > target_aspect_ratio:
        # Film jest zbyt szeroki - przytnij
        new_width = int(height * target_aspect_ratio)
        cropped_clip = crop(clip, width=new_width, height=height, x_center=width / 2)
    else:
        # Film jest zbyt wysoki - przytnij
        new_height = int(width / target_aspect_ratio)
        cropped_clip = crop(clip, width=width, height=new_height, y_center=height / 2)

    cropped_clip.write_videofile(output_path, fps=clip.fps, codec="libx264", audio_codec="aac")
    print(f"Film {video_path} został dopasowany do proporcji 9:16 i zapisany jako {output_path}.")
    return output_path


def ensure_even_dimensions(clip):
    """
    Upewnia się, że wymiary klipu są liczbami parzystymi.
    Jeśli nie są, zmienia rozmiar klipu na najbliższe liczby parzyste.
    """
    width, height = clip.size
    new_width = width if width % 2 == 0 else width + 1
    new_height = height if height % 2 == 0 else height + 1
    if (new_width, new_height) != (width, height):
        print(f"Dostosowanie wymiarów z ({width}, {height}) do ({new_width}, {new_height}).")
        return clip.resize(newsize=(new_width, new_height))
    return clip





