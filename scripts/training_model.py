import pandas as pd
import xgboost as xgb
import os

# --- CONFIGURAZIONE ---
# ATTENZIONE: Qui serve il file con i NOMI, non quello solo numerico per l'AI
NOME_DB_NOMI = "database_tennis_completo.csv"
NOME_MODELLO = "modello_tennis.json"


def recupera_stato_giocatore(nome_giocatore, df):
    """Cerca l'ultimo ELO e Ranking registrato per un giocatore"""
    # Filtriamo i match dove compare il giocatore
    last_match_w = df[df['winner_name'] == nome_giocatore].tail(1)
    last_match_l = df[df['loser_name'] == nome_giocatore].tail(1)

    if last_match_w.empty and last_match_l.empty:
        print(f"⚠️ Giocatore '{nome_giocatore}' non trovato. Controlla maiuscole e spazi!")
        return 1500, 1500, 500

    idx_w = last_match_w.index[0] if not last_match_w.empty else -1
    idx_l = last_match_l.index[0] if not last_match_l.empty else -1

    if idx_w > idx_l:
        # L'ultimo match lo ha vinto: prendiamo i dati dalle colonne 'winner'
        return (last_match_w['elo_vincitore'].values[0],
                last_match_w.get('elo_surf_vincitore', last_match_w['elo_vincitore']).values[0],
                last_match_w['winner_rank'].values[0])
    else:
        # L'ultimo match lo ha perso: prendiamo i dati dalle colonne 'loser'
        return (last_match_l['elo_perdente'].values[0],
                last_match_l.get('elo_surf_perdente', last_match_l['elo_perdente']).values[0],
                last_match_l['loser_rank'].values[0])


def esegui_pronostico():
    if not os.path.exists(NOME_MODELLO):
        print("❌ Modello .json non trovato!")
        return

    if not os.path.exists(NOME_DB_NOMI):
        print(f"❌ File {NOME_DB_NOMI} non trovato! Assicurati di averlo generato.")
        return

    model = xgb.XGBClassifier()
    model.load_model(NOME_MODELLO)

    print("📂 Caricamento database nomi...")
    df = pd.read_csv(NOME_DB_NOMI, low_memory=False)

    print("\n" + "=" * 40)
    p1_name = input("Inserisci Giocatore 1 (es. Jannik Sinner): ").strip()
    p2_name = input("Inserisci Giocatore 2 (es. Carlos Alcaraz): ").strip()
    print("=" * 40)

    # Recupero dati
    elo1, elo_s1, rank1 = recupera_stato_giocatore(p1_name, df)
    elo2, elo_s2, rank2 = recupera_stato_giocatore(p2_name, df)

    # Pulizia Rank (se sono NaN mettiamo 500)
    r1 = rank1 if pd.notna(rank1) else 500
    r2 = rank2 if pd.notna(rank2) else 500

    # Input per AI (deve avere le stesse 4 colonne dell'allenamento)
    features = pd.DataFrame([[
        elo1 - elo2,
        elo_s1 - elo_s2,
        0,  # Ace diff (valore neutro)
        r1 - r2
    ]], columns=['elo_diff', 'elo_surf_diff', 'ace_diff', 'rank_diff'])

    probs = model.predict_proba(features)[0]

    vincitore = p1_name if probs[1] > probs[0] else p2_name
    confidenza = max(probs)

    print(f"\n🎾 PRONOSTICO AI:")
    print(f"🏆 VINCITORE: {vincitore.upper()}")
    print(f"📈 PROBABILITÀ: {confidenza:.2%}")
    print("=" * 40)


if __name__ == "__main__":
    esegui_pronostico()