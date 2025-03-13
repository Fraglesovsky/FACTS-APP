from diffusers import StableDiffusionPipeline
import torch
import os
import requests
from dotenv import load_dotenv
from facts_generator import extract_keywords
from PIL import Image


load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

if not PEXELS_API_KEY:
    raise ValueError("Nie znaleziono klucza API! Upewnij się, że plik .env zawiera poprawny klucz PEXELS_API_KEY.")

def generate_image(prompt):
    """
    Generuje obraz na podstawie podanego promptu i zapisuje go z nazwą odpowiadającą tekstowi.
    
    :param prompt: Tekst używany jako prompt do generowania obrazu.
    :return: Pełna ścieżka do wygenerowanego obrazu.
    """
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id)
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    # Upewnij się, że folder 'Final_Video' istnieje
    folder_path = "Final_Video"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Generowanie obrazu
    image = pipe(prompt).images[0]

    # Stwórz nazwę pliku na podstawie tekstu (zamień spacje na podkreślenia)
    safe_filename = "_".join(prompt.split()) + ".jpg"
    image_path = os.path.join(folder_path, safe_filename)

    # Zapisz obraz
    image.save(image_path)
    print(f"Obraz wygenerowany: {image_path}")
    
    return image_path  # Zwróć pełną ścieżkę do obrazu

def search_image(query,size="portrait"):
    """
    Wyszukuje obraz w Pexels API na podstawie kluczowych słów i zapisuje go jako plik lokalny.
    
    :param query: Tekst do wyszukiwania obrazu.
    :return: Ścieżka do pobranego obrazu.
    """
    # Wyodrębnij kluczowe słowa z zapytania
    keywords = extract_keywords(query)
    
    # Użyj pierwszych 2-3 kluczowych słów jako zapytania
    search_query = " ".join(keywords[:3])
    
    url = f"https://api.pexels.com/v1/search?query={search_query}&per_page=1"
    headers = {"Authorization": PEXELS_API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data["photos"]:
            raise ValueError(f"Nie znaleziono obrazów dla zapytania: {search_query}")
        
        if size not in data["photos"][0]["src"]:
            raise ValueError(f"Rozmiar '{size}' nie jest dostępny dla tego obrazu.")

        # Pobierz URL pierwszego obrazu
        image_url = data["photos"][0]["src"]["original"]

        # Pobierz i zapisz obraz
        folder_path = "Final_Video"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = os.path.join(folder_path, f"{search_query.replace(' ', '_')}.jpg")
        img_data = requests.get(image_url).content
        with open(image_path, "wb") as handler:
            handler.write(img_data)

        print(f"Obraz pobrany i zapisany jako: {image_path}")
        return image_path
    else:
        raise ValueError(f"Błąd podczas wyszukiwania obrazu: {response.status_code}, {response.text}")
    

def check_and_adjust_image(image_path, target_resolution=(1080, 1920)):
    """
    Sprawdza proporcje obrazu i dopasowuje go do proporcji 9:16 (1080x1920) tylko jeśli jest to konieczne.
    
    :param image_path: Ścieżka do obrazu.
    :param target_resolution: Docelowa rozdzielczość (szerokość, wysokość).
    :return: Ścieżka do przetworzonego obrazu.
    """
    img = Image.open(image_path)
    width, height = img.size

    # Oblicz proporcje
    aspect_ratio = width / height
    target_aspect_ratio = target_resolution[0] / target_resolution[1]

    if abs(aspect_ratio - target_aspect_ratio) < 0.01:
        print(f"Obraz {image_path} już ma proporcje 9:16.")
        return image_path  # Nie zmieniaj obrazu

    # Przytnij lub skaluj obraz
    if aspect_ratio > target_aspect_ratio:
        # Obraz jest zbyt szeroki - przytnij
        new_width = int(height * target_aspect_ratio)
        left = (width - new_width) // 2
        right = left + new_width
        img_cropped = img.crop((left, 0, right, height))
    else:
        # Obraz jest zbyt wysoki - przytnij
        new_height = int(width / target_aspect_ratio)
        top = (height - new_height) // 2
        bottom = top + new_height
        img_cropped = img.crop((0, top, width, bottom))

    cropped_image_path = image_path.replace(".jpg", "_adjusted.jpg")
    img_cropped.save(cropped_image_path)
    print(f"Obraz {image_path} został dopasowany do proporcji 9:16 i zapisany jako {cropped_image_path}.")
    return cropped_image_path
    

# Przykładowe użycie funkcji




