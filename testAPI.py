import requests
import json

def diagnostic_prediction_run(date_str, tour_type='atp'):
    # 1. Mostra l'URL esatto
    url = f"https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/{tour_type}/fixtures/{date_str}"
    print(f"\n🔍 [STEP 1] Chiamata all'URL: {url}")
    
    headers = {
        "X-RapidAPI-Key": "1397977a20msh6113f4f1a0ec3c4p157aadjsn53c94114ed5b",
        "X-RapidAPI-Host": "tennis-api-atp-wta-itf.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        
        # 2. Mostra lo stato del server
        print(f"📡 [STEP 2] Risposta Server: {response.status_code}")
        
        if response.status_code == 200:
            raw_data = response.json()
            # 3. STAMPA TUTTO IL JSON GREZZO
            print(f"📦 [STEP 3] Dati ricevuti dal server: {json.dumps(raw_data, indent=2)}")
            
            # --- V87: FIX CHIAVE JSON ---
            matches = raw_data.get('data', [])
            print(f"📊 [STEP 4] Numero di match trovati nella chiave 'data': {len(matches)}")
            
            if len(matches) > 0:
                for i, m in enumerate(matches):
                    p1 = m.get('player1', {}).get('name', 'N/A')
                    p2 = m.get('player2', {}).get('name', 'N/A')
                    t_id = m.get('tournamentId', 'N/A')
                    print(f"   🎾 Match {i+1}: {p1} vs {p2} (Tournament ID: {t_id})")
            else:
                print("⚠️ ATTENZIONE: La chiave 'data' è vuota. Forse la data è errata o il server è in aggiornamento.")
        else:
            print(f"❌ ERRORE CRITICO: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRORE DI CONNESSIONE: {e}")

if __name__ == "__main__":
    # Esegui il test per la data delle semifinali
    target_date = "2026-01-30"
    diagnostic_prediction_run(target_date, tour_type='atp')
    diagnostic_prediction_run(target_date, tour_type='wta')
