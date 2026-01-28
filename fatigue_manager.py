import requests
import json
from datetime import datetime, timedelta
import time
import random
import database_manager

# --- V99: Correzione ID Sofascore (Tabella di Traduzione) ---
SOFASCORE_MAPPING = {
    5992: 14472,    # Djokovic
    47275: 206570,  # Sinner
    68074: 209857,  # Alcaraz
    24008: 57163    # Zverev
}

class FatigueManager:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://www.sofascore.com/',
            'x-requested-with': 'XMLHttpRequest',
            'Accept': '*/*'
        }
        self.session = requests.Session()
        self.session.get('https://www.sofascore.com/', headers={'User-Agent': 'Mozilla/5.0'})

    def get_real_fatigue(self, rapid_id):
        sofa_id = SOFASCORE_MAPPING.get(rapid_id, rapid_id)
        
        try:
            cached = database_manager.get_cached_form_data(sofa_id)
            if cached: return cached
        except Exception as e:
            print(f"⚠️ Errore accesso cache: {e}")
            pass

        print(f"📡 Recupero dati stanchezza LIVE per ID Sofascore {sofa_id} (da RapidID {rapid_id})...")
        
        try:
            time.sleep(random.uniform(1, 2))
            events_api_url = f"https://api.sofascore.com/api/v1/player/{sofa_id}/events/last/0"
            events_response = self.session.get(events_api_url, headers=self.headers, timeout=15)
            
            if events_response.status_code != 200:
                print(f"❌ Errore API {events_response.status_code} per ID {sofa_id}")
                return {'total_minutes': 0, 'rest_ratio': 48.0, 'status': 'default'}

            events_data = events_response.json()
            
            past_matches = [e for e in events_data.get('events', []) if e.get('status', {}).get('type') == 'finished'][:3]
            
            total_minutes = 0
            rest_ratio = 48.0 # Default a 48 ore
            
            if past_matches:
                # --- V99: Fix del Rest Ratio (RR) ---
                last_match_start_timestamp = past_matches[0].get('startTimestamp')
                if last_match_start_timestamp:
                    hours_since = (time.time() - last_match_start_timestamp) / 3600
                    rest_ratio = hours_since if hours_since < 100 else 48.0
                
                for m in past_matches:
                    match_id = m.get('id')
                    if match_id:
                        stats_api_url = f"https://api.sofascore.com/api/v1/event/{match_id}/statistics"
                        stats_response = self.session.get(stats_api_url, headers=self.headers, timeout=10)
                        if stats_response.status_code == 200:
                            match_stats = stats_response.json()
                            for period in match_stats.get('statistics', []):
                                for group in period.get('groups', []):
                                    for stat in group.get('statisticsItems', []):
                                        if stat.get('name') == 'gameDuration':
                                            is_home_player = m.get('homeTeam', {}).get('id') == sofa_id
                                            duration_seconds = stat.get('home', 0) if is_home_player else stat.get('away', 0)
                                            total_minutes += duration_seconds / 60
                                            break
            
            fatigue_data = {'total_minutes': total_minutes, 'rest_ratio': rest_ratio, 'status': 'live'}
            database_manager.cache_form_data(sofa_id, fatigue_data)
            return fatigue_data

        except Exception as e:
            print(f"❌ Errore generico nel recupero fatica per ID {sofa_id}: {e}")
            return {'total_minutes': 0, 'rest_ratio': 48.0, 'status': 'default'}

if __name__ == '__main__':
    database_manager.init_db()
    fm = FatigueManager()
    sinner_fatigue = fm.get_real_fatigue(47275)
    print(f"Sinner Fatigue: {sinner_fatigue}")
