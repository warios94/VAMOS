import requests
import os
from dotenv import load_dotenv
import database_manager
import time
import random
from thefuzz import fuzz

# V58: Il "Dizionario d'Oro" (Hard-Mapping) per i Top Player
TOP_PLAYERS_IDS = {
    'Jannik Sinner': 206570,
    'Novak Djokovic': 14882,
    'Carlos Alcaraz': 275923,
    'Alexander Zverev': 57163,
    'Aryna Sabalenka': 157754,
    'Coco Gauff': 264983,
    'Iga Swiatek': 228272,
    'Elena Rybakina': 186312,
    'Jessica Pegula': 44834,
    'Amanda Anisimova': 230628
}

def get_player_id(session, player_name):
    """
    V58: Trova l'ID di un giocatore in modo robusto, usando una gerarchia:
    1. Dizionario d'Oro (Hardcoded)
    2. Cache del Database Locale
    3. API di Ricerca RapidAPI
    """
    # 1. Dizionario d'Oro
    if player_name in TOP_PLAYERS_IDS:
        return TOP_PLAYERS_IDS[player_name]
    
    # 2. Cache del Database
    cached_id = database_manager.get_player_id_from_map(player_name)
    if cached_id:
        return cached_id

    # 3. API di Ricerca
    print(f"↳ ID non trovato per {player_name}. Eseguo ricerca su RapidAPI...")
    load_dotenv()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or api_key == 'tua_chiave_qui':
        return None

    url = "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    params = {"search": player_name}
    
    try:
        time.sleep(random.uniform(1, 2)) # Delay per non sovraccaricare l'API
        response = session.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        for result in data.get('results', []):
            entity = result.get('entity', {})
            if entity.get('sport', {}).get('name') == 'Tennis' and result.get('type') == 'player':
                api_name = entity.get('name')
                # Usa un ratio alto per assicurarsi che sia il giocatore giusto
                if fuzz.ratio(player_name, api_name) > 85:
                    player_id = entity.get('id')
                    print(f"✅ ID Verificato per {player_name}: {player_id}")
                    # Salva il mapping nel DB per le ricerche future
                    database_manager.save_player_id_to_map(player_id, api_name, player_name)
                    return player_id
        
        print(f"❌ Nessun match di alta qualità trovato per {player_name} nella ricerca API.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore API durante la ricerca di {player_name}: {e}")
        return None
