import requests
import os
from dotenv import load_dotenv
import time
import random
from datetime import datetime
import logging
import json

# --- V164: Configurazione Log Professionale ---
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(
    filename='logs/api_intelligence.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_api_call(url, status_code, response_body, headers):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "status": status_code,
        "headers_sent": {k: v for k, v in headers.items() if "key" not in k.lower()},
        "response_preview": response_body[:500]
    }
    logging.debug(f"API_CALL_DATA: {json.dumps(log_entry)}")

class RapidTennisClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("Chiave RapidAPI non trovata nel file .env")
        
        self.url_base = "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2"
        self.headers = {
            "x-rapidapi-host": "tennis-api-atp-wta-itf.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }
        self.session = requests.Session()

    def _make_request(self, endpoint):
        url = f"{self.url_base}{endpoint}"
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(url, headers=self.headers, timeout=20)
            # --- V164: Chiama il logger ---
            log_api_call(url, response.status_code, response.text, self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_api_call(url, "ConnectionError", str(e), self.headers)
            print(f"❌ Errore API per endpoint {endpoint}: {e}")
            return {}

    def get_fixtures_by_date(self, date_str, tour='atp'):
        endpoint = f"/{tour}/fixtures/{date_str}"
        return self._make_request(endpoint).get('data', [])

    def get_player_profile(self, player_id, tour='atp'):
        endpoint = f"/{tour}/player/{player_id}"
        return self._make_request(endpoint).get('data', {})
