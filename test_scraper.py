# V24: Script di test rapido per lo scraper a due righe
import sys
from scraper.tennis_explorer import scrape_matches

if __name__ == "__main__":
    print("--- [DEBUG] Avvio test scraper V24 ---")
    
    try:
        upcoming_matches = scrape_matches()
        
        if upcoming_matches:
            num_matches = len(upcoming_matches)
            first_match = upcoming_matches[0]
            p1, p2, o1, o2, tournament = first_match.values()
            print(f"✅ [DEBUG] Match trovati: {num_matches} | Primo Match: [{tournament}] {p1} vs {p2} (Quote: {o1}/{o2})")
        else:
            print("❌ [DEBUG] Nessun match trovato. Lo scraper non ha estratto dati.")
            
    except Exception as e:
        print(f"🔥 [DEBUG] Errore critico durante l'esecuzione dello scraper: {e}")
        import traceback
        traceback.print_exc()

    print("--- [DEBUG] Test scraper completato ---")
