# Script d'emergenza per vedere Sinner vs Djokovic ORA
from core.engine import TennisEngine
from dotenv import load_dotenv

def run_emergency_analysis():
    """
    V161.1: Esegue un'analisi diretta per i match di Melbourne,
    bypassando la chiamata alle fixtures bloccata dall'API.
    """
    load_dotenv()
    engine = TennisEngine()

    # Dati dei semifinalisti
    djokovic_id = "5992"
    sinner_id = "47275"
    alcaraz_id = "68074"
    zverev_id = "24008"

    print("🚀 Analisi d'emergenza Melbourne...")

    # --- Match 1: Djokovic vs Sinner ---
    try:
        risultato_1 = engine.predict_from_ids(djokovic_id, sinner_id, surface="Hard")
        if risultato_1:
            p1 = risultato_1['p1']
            p2 = risultato_1['p2']
            winner = p1 if risultato_1['final_win_prob'] > 0.5 else p2
            win_prob = risultato_1['final_win_prob'] if risultato_1['final_win_prob'] > 0.5 else 1 - risultato_1['final_win_prob']
            print(f"📊 RISULTATO: {p1} vs {p2} -> {winner} ({win_prob:.2%})")
        else:
            print("❌ Predizione fallita per Djokovic vs Sinner.")
    except Exception as e:
        print(f"❌ Errore durante l'analisi di Djokovic vs Sinner: {e}")

    # --- Match 2: Alcaraz vs Zverev ---
    try:
        risultato_2 = engine.predict_from_ids(alcaraz_id, zverev_id, surface="Hard")
        if risultato_2:
            p1 = risultato_2['p1']
            p2 = risultato_2['p2']
            winner = p1 if risultato_2['final_win_prob'] > 0.5 else p2
            win_prob = risultato_2['final_win_prob'] if risultato_2['final_win_prob'] > 0.5 else 1 - risultato_2['final_win_prob']
            print(f"📊 RISULTATO: {p1} vs {p2} -> {winner} ({win_prob:.2%})")
        else:
            print("❌ Predizione fallita per Alcaraz vs Zverev.")
    except Exception as e:
        print(f"❌ Errore durante l'analisi di Alcaraz vs Zverev: {e}")

if __name__ == "__main__":
    run_emergency_analysis()
