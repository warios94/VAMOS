import pandas as pd
import os

# Trova la cartella principale del progetto indipendentemente da dove lanci lo script
base_dir = os.path.dirname(os.path.abspath(__file__))
# Se lo script è in una sottocartella, risale di un livello
if "models" in base_dir or "scripts" in base_dir:
    base_dir = os.path.dirname(base_dir)

data_folder = os.path.join(base_dir, "data")

print(f"🔎 Sto scansionando la cartella: {data_folder}\n")

if os.path.exists(data_folder):
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    if not files:
        print("⚠️ La cartella 'data' è vuota! Non ci sono file CSV.")

    for f in files:
        path = os.path.join(data_folder, f)
        try:
            # Leggiamo solo la prima riga per velocità
            df = pd.read_csv(path, nrows=1)
            colonne = [c.lower() for c in df.columns]

            print(f"📄 File: {f}")
            if 'score' in colonne or 'w_sets' in colonne or 'winner_sets' in colonne:
                print("✅ TROVATO! Questo file ha i dati per la durata dei set.")
                print(f"   Colonne utili: {[c for c in df.columns if c.lower() in ['score', 'w_sets', 'winner_sets']]}")
            else:
                print("❌ Mancano i dati dei set (score/w_sets).")
            print("-" * 30)
        except Exception as e:
            print(f"Err leggendo {f}: {e}")
else:
    print(f"❌ La cartella {data_folder} non esiste ancora. Creala in PyCharm!")