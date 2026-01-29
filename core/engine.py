import numpy as np
import json
from datetime import datetime
from api_client import RapidTennisClient

class TennisEngine:
    def __init__(self):
        self.api_client = RapidTennisClient()
        try:
            with open('data/players_registry.json', 'r') as f:
                self.player_registry = json.load(f)
        except FileNotFoundError:
            self.player_registry = {}

    def export_feature_vector(self, p1_name, p2_name, features):
        """
        V164: Salva l'esatto vettore matematico inviato al modello AI.
        """
        snapshot = {
            "match": f"{p1_name} vs {p2_name}",
            "input_features": features,
            "timestamp": datetime.now().isoformat()
        }
        with open('logs/model_input_snapshot.json', 'a') as f:
            f.write(json.dumps(snapshot) + "\n")

    def predict(self, p1_data, p2_data):
        p1_id = str(p1_data.get('id'))
        p2_id = str(p2_data.get('id'))
        
        p1_registry_data = self.player_registry.get(p1_id, {})
        p2_registry_data = self.player_registry.get(p2_id, {})

        p1_name = p1_registry_data.get('name', p1_data.get('name', 'Player 1'))
        p2_name = p2_registry_data.get('name', p2_data.get('name', 'Player 2'))
        
        p1_points = p1_registry_data.get('points', 0)
        p2_points = p2_registry_data.get('points', 0)
        
        points_diff = p1_points - p2_points
        
        feature_vector = {
            'points_diff': points_diff,
            # Aggiungi qui altre feature man mano che vengono sviluppate
        }
        
        # --- V164: Chiama il Model X-Ray ---
        self.export_feature_vector(p1_name, p2_name, feature_vector)

        base_prob = 0.5
        if (p1_points + p2_points) > 0:
            base_prob = 0.5 + ((points_diff / (p1_points + p2_points)) * 0.25)
        
        final_prob = np.clip(base_prob, 0.01, 0.99)
        
        return {
            "p1": p1_name, "p2": p2_name,
            "final_win_prob": final_prob,
        }
