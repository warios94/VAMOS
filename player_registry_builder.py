import requests
import json
import os
from dotenv import load_dotenv
import time

def build_full_registry():
    """
    V159: Usa la paginazione per costruire un registro giocatori completo.
    """
    load_dotenv()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise ValueError("Chiave RapidAPI non trovata nel file .env")

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "tennis-api-atp-wta-itf.p.rapidapi.com"
    }
    
    all_players = {}
    print("📡 Avvio Full Dump dei giocatori ATP con paginazione...")

    # Giriamo le prime 50 pagine (11 player a botta = ~550 giocatori)
    for page in range(1, 51):
        url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/atp/player/?page={page}"
        print(f"📡 Scaricando pagina {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"🛑 Stop alla pagina {page}. Codice di stato: {response.status_code}. Errore o fine dati.")
                break
            
            data = response.json().get('data', [])
            if not data:
                print(f"🏁 Fine dei dati alla pagina {page}.")
                break
                
            for p in data:
                player_id = p.get('id')
                if player_id:
                    all_players[str(player_id)] = {
                        "name": p.get('name'),
                        "points": p.get('ranking_points', 0),
                        "ranking": p.get('ranking', 999)
                    }
            
            # Un piccolo respiro per non farci bannare dall'API
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"❌ Errore di rete alla pagina {page}: {e}")
            break
        except json.JSONDecodeError:
            print(f"❌ Errore di decodifica JSON alla pagina {page}.")
            break

    if not os.path.exists('data'):
        os.makedirs('data')
        
    file_path = 'data/players_registry.json'
    with open(file_path, 'w') as f:
        json.dump(all_players, f, indent=2)
        
    print(f"✅ Registro giocatori completo creato: {len(all_players)} giocatori salvati in {file_path}")

if __name__ == "__main__":
    build_full_registry()
