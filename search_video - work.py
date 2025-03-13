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