import pandas as pd
import os


def download_raw_data():
    print("🌐 Download dei dati storici con punteggi in corso...")

    # URL dei dati grezzi di Sackmann (2024 e 2025)
    url_2024 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
    url_2025 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2025.csv"

    try:
        df_24 = pd.read_csv(url_2024)
        df_25 = pd.read_csv(url_2025)
        df_total = pd.concat([df_24, df_25])

        # Verifichiamo se c'è la colonna score
        if 'score' in df_total.columns:
            output_path = "data/database_con_punteggi.csv"
            os.makedirs("data", exist_ok=True)
            df_total.to_csv(output_path, index=False)
            print(f"✅ Successo! Salvato '{output_path}' con {len(df_total)} match.")
            print(f"📊 Colonne disponibili: {df_total.columns.tolist()[:10]}... e soprattutto 'score'!")
        else:
            print("❌ Errore: Anche questi dati non hanno la colonna score (strano).")

    except Exception as e:
        print(f"❌ Errore durante il download: {e}")


if __name__ == "__main__":
    download_raw_data()