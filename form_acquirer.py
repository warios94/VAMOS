import os
from dotenv import load_dotenv
import database_manager
import json
import api_client
import numpy as np

def get_player_form_from_api(session, player_id, tour):
    """
    V70: Recupera e calcola le statistiche di forma dal perf-breakdown di RapidAPI.
    """
    if not player_id:
        return {'live_data_available': False, 'surface_win_perc': 0, 'fatigue_score': 0, 'pressure_index': 0}

    cached_stats = database_manager.get_cached_player_stats(player_id)
    if cached_stats:
        return cached_stats

    print(f"↳ Recupero performance breakdown da RapidAPI V2 per player ID {player_id} ({tour.upper()})...")
    
    try:
        data = api_client.get_player_stats_history(session, player_id, tour)
        if not data:
            raise ValueError("Dati di breakdown non validi o mancanti.")

        # --- V70: Deep Feature Engineering ---
        surface_win_perc = 0
        fatigue_score = 0
        pressure_index = 0
        
        # Cerca le statistiche su Hard Court
        for stat_entry in data:
            if stat_entry.get('surface') == 'Hard':
                surface_win_perc = stat_entry.get('win_perc', 0)
                fatigue_score = stat_entry.get('avg_minutes_in_3_set_matches', 0) # Esempio
                pressure_index = stat_entry.get('tie_breaks_won_perc', 0) # Esempio
                break
        
        form_data = {
            'surface_win_perc': surface_win_perc,
            'fatigue_score': fatigue_score,
            'pressure_index': pressure_index,
            'live_data_available': True
        }

        database_manager.cache_player_stats(player_id, form_data)
        return form_data

    except Exception as e:
        print(f"❌ Errore API durante il recupero del breakdown per player ID {player_id}: {e}")
        return {'live_data_available': False, 'surface_win_perc': 0, 'fatigue_score': 0, 'pressure_index': 0}

if __name__ == '__main__':
    load_dotenv()
    database_manager.init_db()
    import requests
    session = requests.Session()
    
    test_player_id = 249137 # Sinner
    form = get_player_form_from_api(session, test_player_id, 'atp')
    if form:
        print(f"\n--- Risultati Test Form Acquirer V70 per Player ID {test_player_id} ---")
        print(json.dumps(form, indent=4))
    else:
        print(f"Test fallito per Player ID {test_player_id}.")
