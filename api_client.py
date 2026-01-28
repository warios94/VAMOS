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
        try:
            time.sleep(random.uniform(1, 2))
            response = self.session.get(f"{self.url_base}{endpoint}", headers=self.headers, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore API per endpoint {endpoint}: {e}")
            return {}

    def get_fixtures_by_date(self, date_str, tour='atp'):
        endpoint = f"/{tour}/fixtures/{date_str}"
        return self._make_request(endpoint).get('data', [])

    def get_player_perf_breakdown(self, player_id, tour='atp'):
        endpoint = f"/{tour}/player/perf-breakdown/{player_id}"
        return self._make_request(endpoint).get('results', [])

    def get_player_titles(self, player_id, tour='atp'):
        endpoint = f"/{tour}/player/titles/{player_id}"
        return self._make_request(endpoint).get('data', [])
        
    def get_player_details(self, player_id, tour='atp'):
        """Recupera i dettagli di un giocatore (ranking, punti, etc.)."""
        endpoint = f"/{tour}/player/{player_id}"
        return self._make_request(endpoint).get('data', {})

    def get_player_profile(self, player_id, tour='atp', surface_name="Hard"):
        """V128: Aggrega i dati di un giocatore in un unico profilo."""
        # 1. Recupera Performance (Surface Win)
        perf = self.get_player_perf_breakdown(player_id, tour) 
        surface_data = next((item for item in perf if item.get('surface') == surface_name), {})
        surface_win = float(surface_data.get('win_pct', 60)) / 100

        # 2. Recupera Killer Instinct (Titoli)
        titles = self.get_player_titles(player_id, tour)
        total_won = sum(int(t.get('titlesWon', 0)) for t in titles)
        total_lost = sum(int(t.get('titlesLost', 0)) for t in titles)
        killer_instinct = total_won / (total_won + total_lost) if (total_won + total_lost) > 0 else 0.5

        # 3. Recupera Ranking (Points)
        details = self.get_player_details(player_id, tour)
        points = int(details.get('points', 0))

        return {
            'surface_win': surface_win,
            'killer_instinct': killer_instinct,
            'points': points
        }

if __name__ == '__main__':
    client = RapidTennisClient()
    # Esempio Sinner
    sinner_profile = client.get_player_profile(249137)
    print(f"Sinner Profile: {sinner_profile}")
