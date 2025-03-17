import requests
import os
import psycopg2
import re
from dotenv import load_dotenv
from DB import save_fact, fact_exists



# Wczytaj zmienne środowiskowe z pliku .env
load_dotenv()

API_KEY = os.getenv("API_NINJAS_KEY")

if not API_KEY:
    raise ValueError("Nie znaleziono klucza API! Upewnij się, że plik .env zawiera poprawny klucz API.")

def get_fact():
    """
    Pobiera jedną ciekawostkę z API-Ninjas.
    
    :return: Ciekawostka jako string.
    """
    api_url = 'https://api.api-ninjas.com/v1/facts'
    headers = {'X-Api-Key': API_KEY}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        fact = response.json()[0]["fact"]
    if not fact_exists(fact):
                save_fact(fact)
                return fact
                
    print("Znaleziono duplikat, próbuję ponownie...")
    
    return None

def extract_keywords(text):
    """
    Wyodrębnia kluczowe słowa z tekstu, usuwając stopwords i znaki specjalne.
    
    :param text: Tekst wejściowy (np. ciekawostka).
    :return: Lista kluczowych słów.
    """
    # Usuń znaki specjalne
    text = re.sub(r'[^\w\s]', '', text)
    
    # Zamień tekst na małe litery
    text = text.lower()
    
    # Lista stopwords (możesz ją rozszerzyć)
    stopwords = {"the", "is", "in", "of", "and", "to", "as", "we", "our", "it", "by", "know","a","an","on","for","with","that","this","these","those","there","here","where","when","why","how","who","whom","whose","which","what","but","or","and","if","unless","until","while","since","because","so","then","than","whether","either","neither","both","each","every","any","all","some","most","more","less","few","many","much","such","other","another","own","same","different","such","so","too","enough","very","really","quite","rather","almost","even","ever","never","always","sometimes","often","rarely","seldom","hard"}
    
    # Wyodrębnij słowa, które nie są stopwords
    keywords = [word for word in text.split() if word not in stopwords]
    
    return keywords



