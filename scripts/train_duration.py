import pandas as pd
import xgboost as xgb
import os
import sys

# Aggiunta percorso per config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def estrai_set_da_score(score_str):
    """Conta quanti set sono stati giocati basandosi sulla stringa del punteggio (es. '6-4 6-2')"""
    if pd.isna(score_str) or score_str == "" or "RET" in str(score_str):
        return None
    # Conta i blocchi di punteggio (es. "6-4 2-6 7-6" -> 3 blocchi)
    return len(str(score_str).split())


def train_sets_model():
    print("📊 Caricamento dati per il Modello Durata...")
    df = pd.read_csv(config.DB_PATH)

    # --- LOGICA DI RECUPERO SET ---
    if 'w_sets' in df.columns and 'l_sets' in df.columns:
        df['total_sets'] = df['w_sets'] + df['l_sets']
    elif 'w_set' in df.columns and 'l_set' in df.columns:
        df['total_sets'] = df['w_set'] + df['l_set']
    elif 'score' in df.columns:
        print("🔍 Colonne set non trovate, estrazione da 'score'...")
        df['total_sets'] = df['score'].apply(estrai_set_da_score)
    else:
        print("❌ Errore: Non trovo colonne per i set (w_sets, w_set o score).")
        return

    # Pulizia dati
    df = df[df['total_sets'].isin([2, 3, 4, 5])].dropna(subset=['elo_diff', 'minutes'])

    # Feature V6
    features = ['elo_diff', 'elo_surf_diff', 'rolling_win_diff', 'serve_dom_diff',
                'fatigue_diff', 'is_grand_slam', 'best_of_5', 'rank_diff']

    X = df[features]
    y = df['total_sets'].map({2: 0, 3: 1, 4: 2, 5: 3})

    print(f"🧠 Training Modello Durata su {len(df)} match...")
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=4,
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5
    )

    model.fit(X, y)

    # Salvataggio
    os.makedirs(os.path.dirname(config.MODEL_SETS_PATH), exist_ok=True)
    model.save_model(config.MODEL_SETS_PATH)
    print(f"✅ Modello Durata salvato in: {config.MODEL_SETS_PATH}")


if __name__ == "__main__":
    train_sets_model()