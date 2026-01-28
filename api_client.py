import requests
import os
from dotenv import load_dotenv
import time
import random

class RapidTennisClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key or "tua_chiave_qui" in api_key:
            raise ValueError("Chiave RapidAPI non trovata o non configurata nel file .env")
        
        self.url_base = "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2"
        self.headers = {
            "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com",
            "x-rapidapi-key": api_key
        }
        self.session = requests.Session()

    def _make_request(self, endpoint):
        """Helper per effettuare richieste API con gestione errori."""
        try:
            time.sleep(random.uniform(1, 2))
            response = self.session.get(f"{self.url_base}{endpoint}", headers=self.headers, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore API per endpoint {endpoint}: {e}")
            return {}

    def get_fixtures_by_date(self, date_str, tour='atp'):
        """
        V117: Corregge la chiave di estrazione dati da 'results' a 'data'.
        """
        endpoint = f"/{tour}/fixtures/{date_str}"
        # --- V117: FIX CHIAVE JSON ---
        return self._make_request(endpoint).get('data', [])

    def get_player_perf_breakdown(self, player_id, tour='atp'):
        endpoint = f"/{tour}/player/perf-breakdown/{player_id}"
        return self._make_request(endpoint).get('results', [])

    def get_player_skills(self, player_id, tour='atp'):
        endpoint = f"/{tour}/player/match-stats/{player_id}"
        data = self._make_request(endpoint).get('data', {})
        
        svc = data.get('serviceStats', {})
        rtn = data.get('rtnStats', {})
        
        return {
            'ace_df_ratio': svc.get('acesGm', 0) / (svc.get('doubleFaultsGm', 1) or 1),
            'first_serve_win': svc.get('winningOnFirstServeGm', 0) / (svc.get('firstServeGm', 1) or 1),
            'return_win': rtn.get('winningOnFirstServeGm', 0) / (rtn.get('firstServeOfGm', 1) or 1)
        }

if __name__ == '__main__':
    client = RapidTennisClient()
    sinner_skills = client.get_player_skills(249137)
    print(f"Sinner Skills: {sinner_skills}")
