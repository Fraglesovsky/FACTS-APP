import os
from tts import generate_audio
from video import combine_clips,search_video
from image import generate_image,search_image,check_and_adjust_image
from facts_generator import get_fact

# Tworzenie folderu Final_Video jeśli nie istnieje:
output_folder = "Final_Video"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Pobierz x ciekawostek, wywołując `get_fact` wielokrotnie
facts = [get_fact() for _ in range(2)]
facts = [fact for fact in facts if fact]  # Usuń puste wartości, jeśli API zwróci błąd

# Połącz wszystkie ciekawostki w jeden tekst
combined_facts = "\n".join(f"{i+1}. {fact}" for i, fact in enumerate(facts))
print(f"Łączne ciekawostki:\n{combined_facts}")

# Generowanie jednej ścieżki audio dla wszystkich ciekawostek
audio_path = generate_audio(combined_facts)
print(f"Ścieżka do pliku audio: {audio_path}")
if not os.path.exists(audio_path):
    print("Plik audio nie istnieje!")

# Generowanie jednego obrazu dla całego filmu
first_fact = facts[0] if facts else "Ciekawostka"
image_path = search_image(first_fact)

# Pobierz oddzielne filmy dla każdego faktu
video_paths = [search_video(fact, count=1) for fact in facts]
video_paths = [item for sublist in video_paths for item in sublist]  # Flatten the list
print(f"Image path: {image_path}")
print(f"Video paths: {video_paths}")
print(f"Audio path: {audio_path}")

if not os.path.exists(image_path):
    print("Image file not found!")
if not all(os.path.exists(video_path) for video_path in video_paths):
    print("One or more video files not found!")
if not os.path.exists(audio_path):
    print("Audio file not found!")

# Tworzenie filmu z dynamicznym tekstem
if os.path.exists(image_path) and all(os.path.exists(video) for video in video_paths) and os.path.exists(audio_path):
    final_video_path = combine_clips(image_path, video_paths, audio_path, image_duration=2)
    print(f"Finalny film zapisany jako: {final_video_path}")
else:
    print("Nie można utworzyć filmu, ponieważ brakuje jednego lub więcej plików wejściowych.")

print(f"Filmik zapisany: {video_paths}")
