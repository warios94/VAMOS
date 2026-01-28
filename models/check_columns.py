import pandas as pd
import os

# Questo comando trova la cartella principale del progetto (Tennis_AI_V2)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base_dir, "data", "database_tennis_completo.csv")

print(f"🔍 Sto cercando il database qui: {path}")

if os.path.exists(path):
    df = pd.read_csv(path, nrows=1)
    print("\n✅ FILE TROVATO!")
    print("--- COLONNE DISPONIBILI ---")
    print(df.columns.tolist())
    print("---------------------------\n")
else:
    print("\n❌ NON LO TROVO ANCORA.")
    print(f"Assicurati che:")
    print(f"1. Esista una cartella chiamata 'data' in {base_dir}")
    print(f"2. Il file si chiami esattamente: database_tennis_completo.csv")

    # Vediamo cosa c'è effettivamente nella cartella data (se esiste)
    data_folder = os.path.join(base_dir, "data")
    if os.path.exists(data_folder):
        print(f"\nContenuto della cartella 'data': {os.listdir(data_folder)}")
    else:
        print("\nLa cartella 'data' non esiste proprio!")