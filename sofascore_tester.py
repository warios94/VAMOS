import requests
import json
import time

# 1. HEADER PROFESSIONALI (Quelli che hai chiesto tu, Capo)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': '*/*',
    'Origin': 'https://www.sofascore.com',
    'Referer': 'https://www.sofascore.com/'
}

# 2. MAPPING ID REALI (Ecco dove sta l'errore nel Main!)
TEST_PLAYERS = {
    "Novak Djokovic": 14882,    # Corretto (Era 14472 - Sbagliato)
    "Jannik Sinner": 1054778,   # Corretto (Era 206570 - Calciatore!)
    "Carlos Alcaraz": 1083042,  # Corretto (Era 209857 - Sbagliato)
    "Alexander Zverev": 259137  # Corretto (Era 57163 - Sbagliato)
}


def test_sofascore_pipeline():
    print("🚀 AVVIO TEST DIAGNOSTICO SOFASCORE\n" + "=" * 40)

    for name, s_id in TEST_PLAYERS.items():
        print(f"\n🎾 Analisi Giocatore: {name} (ID: {s_id})")

        # TEST STEP A: Recupero Ultimi Match
        url_events = f"https://api.sofascore.com/api/v1/player/{s_id}/events/last/0"
        print(f"📡 Chiamata Events: {url_events}")

        try:
            res = requests.get(url_events, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                events = res.json().get('events', [])
                print(f"✅ SUCCESSO: Trovati {len(events)} match recenti.")

                if events:
                    last_match = events[0]
                    m_id = last_match.get('id')
                    m_name = f"{last_match['homeTeam']['name']} vs {last_match['awayTeam']['name']}"
                    print(f"   🏆 Ultimo match trovato: {m_name} (ID: {m_id})")

                    # TEST STEP B: Recupero Statistiche (I Minuti Giocati)
                    url_stats = f"https://api.sofascore.com/api/v1/event/{m_id}/statistics"
                    res_stats = requests.get(url_stats, headers=HEADERS, timeout=10)

                    if res_stats.status_code == 200:
                        print(f"✅ STATS AGGANCIATE: Minuti e Bio-dati pronti.")
                    else:
                        print(f"❌ ERRORE STATS: {res_stats.status_code}")
            else:
                print(f"❌ ERRORE 404/403: Il server ha rifiutato l'ID {s_id}")
        except Exception as e:
            print(f"⚠️ CRASH: {e}")

        time.sleep(1)  # Rispetto per il server


if __name__ == "__main__":
    test_sofascore_pipeline()