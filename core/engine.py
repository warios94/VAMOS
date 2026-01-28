import pandas as pd
import xgboost as xgb
import os
import json
import numpy as np
import config

def extract_surface_performance(stats_dict):
    if not stats_dict: return 0.5
    win_rates = []
    for year in ['2026', '2025']:
        year_data = stats_dict.get(year, {})
        hard_stats = year_data.get('court', {}).get('1', {})
        wins = hard_stats.get('w', 0) + hard_stats.get('aw', 0)
        losses = hard_stats.get('l', 0) + hard_stats.get('al', 0)
        total = wins + losses
        if total > 0:
            win_rates.append(wins / total)
    return np.mean(win_rates) if win_rates else 0.5

def estimate_fatigue(stats_2026):
    if not stats_2026: return 0
    matches_won = stats_2026.get('level', {}).get('grandSlam', {}).get('w', 0)
    return matches_won * 150

class TennisEngine:
    def __init__(self):
        self.model_win = self._load_model(config.MODEL_WIN_PATH)
        self.elo_gen = self._load_json(config.ELO_GEN_GENERIC_PATH, default={})

    def _load_model(self, path):
        if os.path.exists(path): m = xgb.XGBClassifier(); m.load_model(path); return m
        return None

    def _load_json(self, path, default):
        if os.path.exists(path):
            with open(path, 'r') as f: return json.load(f)
        return default

    def predict(self, p1_data, p2_data, p1_stats=None, p2_stats=None, p1_skills=None, p2_skills=None, is_slam=False):
        if not self.model_win: return None
        
        p1_name = p1_data.get('name')
        p2_name = p2_data.get('name')

        p1_points = p1_data.get('ranking', 2000)
        p2_points = p2_data.get('ranking', 2000)
        points_diff = p1_points - p2_points
        
        p1_surface_win = extract_surface_performance(p1_stats)
        p2_surface_win = extract_surface_performance(p2_stats)
        
        p1_fatigue_minutes = estimate_fatigue(p1_stats.get('2026', {})) if p1_stats else 0
        p2_fatigue_minutes = estimate_fatigue(p2_stats.get('2026', {})) if p2_stats else 0

        feature_vector = {
            'points_diff': points_diff,
            'p1_fatigue': p1_fatigue_minutes,
            'p2_fatigue': p2_fatigue_minutes,
            'p1_surface_win': p1_surface_win,
            'p2_surface_win': p2_surface_win,
        }
        
        # --- V115: Aggiornamento del Cervello ---
        if p1_skills and p2_skills:
            skill_gap_rtn = p2_skills['return_win'] - p1_skills['return_win']
            skill_gap_serve = p2_skills['first_serve_win'] - p1_skills['first_serve_win']
            ace_df_edge = p2_skills['ace_df_ratio'] - p1_skills['ace_df_ratio']
            
            feature_vector.update({
                'rtn_edge': skill_gap_rtn,
                'serve_edge': skill_gap_serve,
                'ace_df_edge': ace_df_edge
            })
        
        print(f"DEBUG VECTOR {p1_name}: {feature_vector}")

        base_prob = 0.5 + ((points_diff / 10000) * 0.20)
        perf_adjustment = (p1_surface_win - p2_surface_win) * 0.15
        fatigue_adjustment = (p2_fatigue_minutes - p1_fatigue_minutes) / 5000
        
        # Aggiustamento basato sulle skill
        skill_adjustment = 0
        if 'rtn_edge' in feature_vector:
            skill_adjustment += feature_vector['rtn_edge'] * 0.1 # Peso del 10%
            skill_adjustment += feature_vector['serve_edge'] * 0.1
        
        final_prob = base_prob + perf_adjustment - fatigue_adjustment + skill_adjustment
        final_prob = np.clip(final_prob, 0.01, 0.99)
        
        return {
            "p1": p1_name, "p2": p2_name, "is_slam": is_slam, 
            "final_win_prob": final_prob, 
            "suggestion_override": "",
            "p1_form": {'rolling_minutes': p1_fatigue_minutes}, 
            "p2_form": {'rolling_minutes': p2_fatigue_minutes}
        }
