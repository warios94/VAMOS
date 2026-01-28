# config.py
import os

# Telegram
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN" # Replace with your actual token

# --- Percorsi ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Percorso alla cartella dei dati grezzi (per main.py)
CARTELLA_DATI = os.path.join(BASE_DIR, 'data')

# Percorso al database storico completo per lookup di nomi e statistiche (per engine.py)
DB_PATH = os.path.join(CARTELLA_DATI, "database_tennis_completo.csv")

# Percorso al database generato dall'AI (usato solo per training)
AI_DB_PATH = os.path.join(BASE_DIR, "database_ultimate_ai_v6.csv")

# Percorsi per i modelli allenati
MODEL_WIN_PATH = os.path.join(BASE_DIR, "modello_tennis_v6.json")
MODEL_SETS_PATH = os.path.join(BASE_DIR, "modello_durata_v6.json")

# NUOVI PERCORSI: File di stato per Elo e storico giocatori
ELO_GEN_PATH = os.path.join(BASE_DIR, "models", "elo_gen.json")
ELO_SURF_PATH = os.path.join(BASE_DIR, "models", "elo_surf.json")
PLAYER_HISTORY_PATH = os.path.join(BASE_DIR, "models", "player_history.json")
# V71.1: Aggiunta la riga mancante
ELO_GEN_GENERIC_PATH = os.path.join(BASE_DIR, "data", "elo_gen_generic.json")

# Parametri IA
MIN_CONFIDENCE = 0.70
