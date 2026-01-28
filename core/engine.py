import pandas as pd
import xgboost as xgb
import os
import json
import numpy as np
import config

# V130: Tabella "Hardcode d'emergenza" per i dati chiave
EMERGENCY_DATA = {
    "Jannik Sinner": {"surface_win": 0.94, "killer_instinct": 0.738, "fatigue_sets": 13},
    "Novak Djokovic": {"surface_win": 0.875, "killer_instinct": 0.711, "fatigue_sets": 17},
    "Carlos Alcaraz": {"surface_win": 0.85, "killer_instinct": 0.68, "fatigue_sets": 15}, # Stima
    "Alexander Zverev": {"surface_win": 0.80, "killer_instinct": 0.65, "fatigue_sets": 16} # Stima
}

class TennisEngine:
    def __init__(self):
        self.model_win = self._load_model(config.MODEL_WIN_PATH)
        # L'ELO non è più usato in questa versione, ci basiamo sui punti reali
        
    def _load_model(self, path):
        if os.path.exists(path): m = xgb.XGBClassifier(); m.load_model(path); return m
        return None

    def _load_json(self, path, default):
        # Funzione deprecata, mantenuta per compatibilità
        return default

    def predict(self, p1_data, p2_data, is_slam=False):
        if not self.model_win: return None
        
        p1_name = p1_data.get('name')
        p2_name = p2_data.get('name')

        p1_points = p1_data.get('ranking', 2000)
        p2_points = p2_data.get('ranking', 2000)
        points_diff = p1_points - p2_points
        
        # --- V130: Iniezione Dati Reali ---
        p1_emergency_data = EMERGENCY_DATA.get(p1_name, {})
        p2_emergency_data = EMERGENCY_DATA.get(p2_name, {})

        p1_surface_win = p1_emergency_data.get('surface_win', 0.6)
        p2_surface_win = p2_emergency_data.get('surface_win', 0.6)
        
        p1_killer_instinct = p1_emergency_data.get('killer_instinct', 0.5)
        p2_killer_instinct = p2_emergency_data.get('killer_instinct', 0.5)

        p1_fatigue_minutes = p1_emergency_data.get('fatigue_sets', 0) * 45
        p2_fatigue_minutes = p2_emergency_data.get('fatigue_sets', 0) * 45
        
        feature_vector = {
            'points_diff': points_diff,
            'p1_fatigue': p1_fatigue_minutes,
            'p2_fatigue': p2_fatigue_minutes,
            'p1_surface_win': p1_surface_win,
            'p2_surface_win': p2_surface_win,
            'p1_killer_instinct': p1_killer_instinct,
            'p2_killer_instinct': p2_killer_instinct
        }
        print(f"DEBUG VECTOR {p1_name}: {feature_vector}")

        base_prob = 0.5 + ((points_diff / 10000) * 0.10) # Peso ridotto per i punti
        perf_adjustment = (p1_surface_win - p2_surface_win) * 0.20 # Aumentato peso superficie
        
        # --- V130: Inverti/Controlla il Peso della Fatica ---
        # Se p1 è più stanco, il valore è POSITIVO, quindi va SOTTRATTO
        fatigue_adjustment = (p1_fatigue_minutes - p2_fatigue_minutes) / 2000 
        
        killer_instinct_edge = (p1_killer_instinct - p2_killer_instinct) * 0.15

        final_prob = base_prob + perf_adjustment - fatigue_adjustment + killer_instinct_edge
        final_prob = np.clip(final_prob, 0.01, 0.99)
        
        return {
            "p1": p1_name, "p2": p2_name, "is_slam": is_slam, 
            "final_win_prob": final_prob, 
            "suggestion_override": "",
            "p1_form": {'rolling_minutes': p1_fatigue_minutes}, 
            "p2_form": {'rolling_minutes': p2_fatigue_minutes}
        }
