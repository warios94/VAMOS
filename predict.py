
from tabulate import tabulate
import numpy as np
from datetime import datetime
import requests
from core.engine import TennisEngine
from api_client import RapidTennisClient
import database_manager
from dotenv import load_dotenv
import os

def format_predictions(predictions):
    headers = ["Player 1", "Player 2", "Final Winner", "FORM / FATIGUE", "SUGGESTION"]
    table = []

    for i, pred_data in enumerate(predictions):
        if pred_data['prediction'] is None: continue
        
        pred = pred_data['prediction']
        p1, p2, is_slam, final_win_prob, suggestion_override, p1_form, p2_form = pred.values()
        
        winner = p1 if final_win_prob > 0.5 else p2
        winner_conf_val = final_win_prob if final_win_prob > 0.5 else (1-final_win_prob)
        winner_conf_str = f"{winner} ({winner_conf_val:.2%})"
        
        form_str_p1 = f"RM:{p1_form.get('rolling_minutes', 0):.0f}"
        form_str_p2 = f"RM:{p2_form.get('rolling_minutes', 0):.0f}"
        form_str = f"{form_str_p1} vs {form_str_p2}"
        
        suggestion = suggestion_override if suggestion_override else "✅ FRESH"

        table.append([p1, p2, winner_conf_str, form_str, suggestion])
    
    return tabulate(table, headers=headers, tablefmt="grid")

if __name__ == "__main__":
    load_dotenv()
    database_manager.init_db()
    engine = TennisEngine()
    
    client = RapidTennisClient()
    
    target_date = "2026-01-30"
    
    try:
        matches = client.get_fixtures_by_date(target_date, tour='atp')
        print(f"DEBUG: L'API ha restituito {len(matches)} match totali.")
    except Exception as e:
        print(f"❌ Errore durante l'acquisizione dei match: {e}")
        matches = []

    predictions = []
    if engine.model_win:
        # --- V118: FIX ESTRAZIONE DATI LIVE ---
        for match in matches:
            try:
                p1_data = match.get('player1', {})
                p2_data = match.get('player2', {})
                
                p1_name = p1_data.get('name')
                p2_name = p2_data.get('name')
                p1_id = p1_data.get('id')
                p2_id = p2_data.get('id')

                if not p1_id or not p2_id:
                    print(f"⚠️ Salto match: ID mancanti per {p1_name} vs {p2_name}")
                    continue

                print(f"🎾 Analizzo match reale: {p1_name} vs {p2_name}")

                p1_perf = client.get_player_perf_breakdown(p1_id, tour='atp')
                p2_perf = client.get_player_perf_breakdown(p2_id, tour='atp')
                
                p1_skills = client.get_player_skills(p1_id, tour='atp')
                p2_skills = client.get_player_skills(p2_id, tour='atp')

                prediction = engine.predict(
                    p1_data=p1_data, 
                    p2_data=p2_data, 
                    p1_stats=p1_perf,
                    p2_stats=p2_perf,
                    p1_skills=p1_skills,
                    p2_skills=p2_skills,
                    is_slam=True
                )
                predictions.append({'prediction': prediction})
                
                if prediction:
                    print(f"📊 RISULTATO: {p1_name} vs {p2_name} -> {prediction.get('final_win_prob', 0):.2%}")

            except Exception as e:
                print(f"❌ Errore nel ciclo match: {e}")
    else:
        print("❌ Modello non trovato. Esegui prima lo script di training.")

    if predictions:
        results_table = format_predictions(predictions)
        print("\n--- PREDIZIONI V118 ---")
        print(results_table)
