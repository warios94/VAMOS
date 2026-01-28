import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import api_client
import database_manager
import requests

def get_scheduled_matches_from_api(session, date_str, tour_type='atp'):
    """
    V69: Correzione dell'endpoint API per i match programmati.
    """
    load_dotenv()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or "tua_chiave_qui" in api_key:
        raise ValueError("Chiave RapidAPI non trovata o non configurata nel file .env")

    # --- V69: Endpoint Corretto (rimosso /date/) ---
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/{tour_type}/fixtures/{date_str}"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }

    print(f"📡 Chiamata API V2 (Fix 500) per {tour_type.upper()} il {date_str}...")
    
    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status() # Lancia un'eccezione per codici di stato HTTP errati
        data = response.json()
        
        # Filtro per Australian Open
        filtered_events = [
            event for event in data.get('results', []) 
            if 'Australian Open' in event.get('tournament', {}).get('name', '')
        ]
        
        matches = []
        for event in filtered_events:
            p1_data = event.get('player_1', {})
            p2_data = event.get('player_2', {})
            
            p1_name = p1_data.get('name')
            p2_name = p2_data.get('name')

            p1_id = p1_data.get('id')
            p2_id = p2_data.get('id')

            if p1_id and p2_id:
                database_manager.save_player_id_to_map(p1_id, p1_name)
                database_manager.save_player_id_to_map(p2_id, p2_name)

                matches.append({
                    "p1": p1_name, "p2": p2_name,
                    "tournament": event.get('tournament', {}).get('name'),
                    "p1_rapidapi_id": p1_id,
                    "p2_rapidapi_id": p2_id,
                    "tour": tour_type
                })
        return matches

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore API {e}")
        return []

if __name__ == '__main__':
    load_dotenv()
    database_manager.init_db()
    session = requests.Session()
    
    target_date = "2026-01-29"
    upcoming_matches = get_scheduled_matches_from_api(session, target_date, tour_type='atp')
    if upcoming_matches:
        print(f"✅ Trovati {len(upcoming_matches)} match per l'Australian Open:")
        for i, match in enumerate(upcoming_matches[:5]):
            print(f"  {i+1}. [{match['tournament']}] {match['p1']} vs {match['p2']}")
    else:
        print("Nessun match trovato.")
