from tabulate import tabulate
from datetime import datetime
from core.engine import TennisEngine
from api_client import RapidTennisClient
from player_vault import get_or_fetch_player # V163: Importa la nuova funzione
from dotenv import load_dotenv
import os
import json

def format_predictions(predictions):
    headers = ["Player 1", "Player 2", "Final Winner"]
    table = []
    for pred in predictions:
        if not pred: continue
        p1 = pred['p1']
        p2 = pred['p2']
        winner = p1 if pred['final_win_prob'] > 0.5 else p2
        win_prob = pred['final_win_prob'] if pred['final_win_prob'] > 0.5 else 1 - pred['final_win_prob']
        table.append([p1, p2, f"{winner} ({win_prob:.2%})"])
    return tabulate(table, headers=headers, tablefmt="grid")

if __name__ == "__main__":
    load_dotenv()
    engine = TennisEngine()
    client = RapidTennisClient()
    
    target_date = "2026-01-30"
    matches = []
    
    try:
        print("📡 Tentativo di recupero fixtures live dall'API...")
        matches = client.get_fixtures_by_date(target_date, tour='atp')
        if not matches:
            raise ValueError("L'API ha restituito una lista vuota.")
        print(f"✅ {len(matches)} match live recuperati con successo.")
    except Exception as e:
        print(f"⚠️ Errore API ({e}). Attivo il paracadute: carico manual_fixtures.json.")
        try:
            with open('data/manual_fixtures.json', 'r') as f:
                matches = json.load(f)
            print(f"✅ {len(matches)} match caricati dal file di override.")
        except FileNotFoundError:
            print("❌ ERRORE CRITICO: File di override manual_fixtures.json non trovato.")
            matches = []

    predictions = []
    for match_data in matches:
        p1_id = match_data.get('player1', {}).get('id')
        p2_id = match_data.get('player2', {}).get('id')

        if not p1_id or not p2_id:
            continue
        
        # --- V163: Logica "Lookup Blindato" ---
        p1_profile = get_or_fetch_player(p1_id, client)
        p2_profile = get_or_fetch_player(p2_id, client)

        if not p1_profile or not p2_profile:
            print(f"⚠️ Analisi saltata per match ID {match_data.get('id')}: dati giocatore insufficienti.")
            continue
            
        # L'engine ora riceve i profili completi dal Vault
        prediction = engine.predict(p1_profile, p2_profile)
        predictions.append(prediction)
        
        if prediction:
            print(f"📊 RISULTATO: {prediction.get('p1')} vs {prediction.get('p2')} -> {prediction.get('final_win_prob', 0):.2%}")

    if predictions:
        results_table = format_predictions(predictions)
        print("\n--- PREDIZIONI V163 ---")
        print(results_table)
    else:
        print("\nNessuna predizione generata.")
