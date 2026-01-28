import pandas as pd
import numpy as np
import xgboost as xgb
import os, glob, sys, json, requests
from datetime import timedelta
from tqdm import tqdm
from sklearn.utils.class_weight import compute_sample_weight
import config

def scarica_nuovi_dati():
    print("🌐 Fase 1: Download dati estesi (2010-2026)...")
    if not os.path.exists(config.CARTELLA_DATI):
        os.makedirs(config.CARTELLA_DATI)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    fonti = [
        *[(f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{a}.csv", f"atp_{a}.csv") for a in range(2010, 2025)],
        *[(f"https://raw.githubusercontent.com/Tennismylife/TML-Database/master/{a}.csv", f"atp_{a}.csv") for a in [2025, 2026]]
    ]
    for url, nome in fonti:
        path_file = os.path.join(config.CARTELLA_DATI, nome)
        if not os.path.exists(path_file):
            try:
                r = requests.get(url, headers=headers, timeout=20)
                if r.status_code == 200:
                    with open(path_file, 'wb') as f: f.write(r.content)
                    print(f"✅ {nome} scaricato.")
            except Exception as e:
                print(f"❌ Errore download {nome}: {e}")
        else:
            print(f"ℹ️ {nome} già presente.")

def custom_serializer(obj):
    if isinstance(obj, pd.Timestamp): return obj.isoformat()
    if pd.isna(obj): return None
    raise TypeError(f"Type {type(obj)} not serializable")

def prepara_motore_v35_restored():
    print(f"🚀 Ripristino a V35: Decider Engine Stabile")
    files = sorted(glob.glob(os.path.join(config.CARTELLA_DATI, "*.csv")))
    df = pd.concat([pd.read_csv(f, low_memory=False, encoding='latin1') for f in files])
    df['tourney_date'] = pd.to_datetime(df['tourney_date'], format='%Y%m%d', errors='coerce')
    df = df.sort_values('tourney_date').dropna(subset=['winner_name', 'loser_name'])

    elo_gen, elo_surf, player_history, data_training = {}, {'Hard': {}, 'Clay': {}, 'Grass': {}}, {}, []
    
    print(f"🧠 Analisi e feature engineering V35 su {len(df)} match...")
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        score = str(row.get('score', ''))
        if not (score and score != 'nan' and len(score.split()) >= 2): continue
        
        label_sets = min(len(score.split()) - 2, 3)
        w, l = row['winner_name'], row['loser_name']
        d, surf = row['tourney_date'], row.get('surface') or 'Hard'
        is_slam = 1 if row.get('best_of') == 5 else 0
        
        # Salva i dati grezzi per il calcolo del DNA nel motore di predizione
        w_stats = {'win': 1, 'mins': row.get('minutes'), 'svpt': row.get('w_svpt'), '1stIn': row.get('w_1stIn'), '1stWon': row.get('w_1stWon'), '2ndWon': row.get('w_2ndWon'), 'ace': row.get('w_ace'), 'bpSaved': row.get('w_bpSaved'), 'bpFaced': row.get('w_bpFaced'), 'rank': row.get('winner_rank'), 'age': row.get('winner_age'), 'date': d, 'opponent_svpt': row.get('l_svpt'), 'opponent_1stIn': row.get('l_1stIn'), 'opponent_2ndWon': row.get('l_2ndWon')}
        l_stats = {'win': 0, 'mins': row.get('minutes'), 'svpt': row.get('l_svpt'), '1stIn': row.get('l_1stIn'), '1stWon': row.get('l_1stWon'), '2ndWon': row.get('l_2ndWon'), 'ace': row.get('l_ace'), 'bpSaved': row.get('l_bpSaved'), 'bpFaced': row.get('l_bpFaced'), 'rank': row.get('loser_rank'), 'age': row.get('loser_age'), 'date': d, 'opponent_svpt': row.get('w_svpt'), 'opponent_1stIn': row.get('w_1stIn'), 'opponent_2ndWon': row.get('w_2ndWon')}
        player_history.setdefault(w, []).append(w_stats)
        player_history.setdefault(l, []).append(l_stats)

        # Per il training, usiamo una versione semplificata delle metriche
        def get_simple_metrics(player, current_date):
            h = player_history.get(player, [])
            past = [m for m in h if m.get('date') and m['date'] < current_date and m.get('svpt', 0) > 0][-20:]
            if len(past) < 10: return 0.5, 0.6
            sd = np.mean([(m.get('1stWon',0) + m.get('2ndWon',0)) / m.get('svpt',1) for m in past])
            win_rate = np.mean([m['win'] for m in past])
            return win_rate, sd

        rw_w, sd_w = get_simple_metrics(w, d)
        rw_l, sd_l = get_simple_metrics(l, d)
        
        rEloW, rEloL = elo_gen.get(w, 1500), elo_gen.get(l, 1500)
        rsEloW, rsEloL = elo_surf.get(surf, {}).get(w, 1500), elo_surf.get(surf, {}).get(l, 1500)

        elo_diff = rEloW - rEloL
        features = {'elo_diff': elo_diff, 'elo_surf_diff': rsEloW - rsEloL, 'rolling_win_diff': rw_w - rw_l, 'serve_dom_diff': sd_w - sd_l, 'is_grand_slam': is_slam}
        data_training.append({**features, 'label': 1, 'label_sets': label_sets})
        data_training.append({**{k: -v for k, v in features.items() if k != 'is_grand_slam'}, 'is_grand_slam': is_slam, 'label': 0, 'label_sets': label_sets})

        exp_w = 1 / (1 + 10 ** ((rEloL - rEloW) / 400)); k = 40 if is_slam else 32
        elo_gen[w], elo_gen[l] = rEloW + k * (1 - exp_w), rEloL + k * (0 - (1 - exp_w))
        exp_sw = 1 / (1 + 10 ** ((rsEloL - rsEloW) / 400))
        elo_surf.setdefault(surf, {})[w] = rsEloW + k * (1 - exp_sw)
        elo_surf.setdefault(surf, {})[l] = rsEloL + k * (0 - (1 - exp_sw))

    full_df = pd.DataFrame(data_training)
    X = full_df.drop(columns=['label', 'label_sets'])
    
    print("🎾 Training Modello Vincitore...")
    model_win = xgb.XGBClassifier(n_estimators=500, learning_rate=0.02, max_depth=4, random_state=42)
    model_win.fit(X, full_df['label'])
    model_win.save_model(config.MODEL_WIN_PATH)

    print("📊 Training Modello Durata Set...")
    y_sets = full_df['label_sets']
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_sets)
    model_sets = xgb.XGBClassifier(objective='multi:softprob', num_class=4, n_estimators=400, learning_rate=0.02, max_depth=4, random_state=42)
    model_sets.fit(X, y_sets, sample_weight=sample_weights)
    model_sets.save_model(config.MODEL_SETS_PATH)

    print("💾 Salvataggio stato finale...")
    with open(config.ELO_GEN_PATH, 'w') as f: json.dump(elo_gen, f)
    with open(config.ELO_SURF_PATH, 'w') as f: json.dump(elo_surf, f)
    with open(config.PLAYER_HISTORY_PATH, 'w') as f: json.dump(player_history, f, default=custom_serializer)
    print("✅ PROCESSO COMPLETATO!")

if __name__ == "__main__":
    prepara_motore_v35_restored()
    print("\n🚀 Avvio pipeline di predizione per i match di domani...")
    os.system(f'{sys.executable} predict.py')
