import sqlite3
import json
from datetime import datetime, timedelta

DB_PATH = 'tennis_ai_cache.db'

def init_db():
    """Inizializza il database e crea le tabelle se non esistono."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players_map (
                rapidapi_id INTEGER PRIMARY KEY,
                player_name TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats_cache (
                player_id INTEGER PRIMARY KEY,
                stats_json TEXT,
                updated_at TIMESTAMP
            )
        ''')
        # --- V94: Tabella per la cache della fatica ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_fatigue_cache (
                player_id INTEGER PRIMARY KEY,
                data TEXT,
                updated_at TIMESTAMP
            )
        ''')
        conn.commit()

def get_player_id_from_map(player_name):
    """Recupera un ID dalla mappa locale."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT rapidapi_id FROM players_map WHERE player_name = ?", (player_name,))
        row = cursor.fetchone()
        return row[0] if row else None

def save_player_id_to_map(player_id, player_name):
    """Salva un mapping ID-nome nel database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO players_map (rapidapi_id, player_name) VALUES (?, ?)', (player_id, player_name))
        conn.commit()

def get_cached_player_stats(player_id):
    """Recupera le statistiche dalla cache se sono più recenti di 12 ore."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stats_json, updated_at FROM player_stats_cache WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        if row:
            stats_json, updated_at_str = row
            updated_at = datetime.fromisoformat(updated_at_str)
            if datetime.now() - updated_at < timedelta(hours=12):
                return json.loads(stats_json)
    return None

def cache_player_stats(player_id, stats_data):
    """Salva le statistiche di un giocatore nella cache."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO player_stats_cache (player_id, stats_json, updated_at) VALUES (?, ?, ?)',
                       (player_id, json.dumps(stats_data), datetime.now().isoformat()))
        conn.commit()

def get_cached_form_data(player_id):
    """
    V94: Recupera i dati sulla forma/stanchezza salvati localmente.
    Se non ci sono, restituisce None per forzare il recupero LIVE.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data, updated_at FROM player_fatigue_cache WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        if row:
            data, updated_at_str = row
            updated_at = datetime.fromisoformat(updated_at_str)
            if datetime.now() - updated_at < timedelta(hours=12):
                return json.loads(data)
    return None

def cache_form_data(player_id, data):
    """Salva i dati di fatica di un giocatore nella cache."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO player_fatigue_cache (player_id, data, updated_at) VALUES (?, ?, ?)',
                       (player_id, json.dumps(data), datetime.now().isoformat()))
        conn.commit()

if __name__ == '__main__':
    print("Inizializzazione database V94...")
    init_db()
    print("Database V94 inizializzato con successo.")
