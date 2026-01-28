import http.client
import json


def analyze_titles_efficiency(player_id, player_name):
    conn = http.client.HTTPSConnection("tennis-api-atp-wta-itf.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "1397977a20msh6113f4f1a0ec3c4p157aadjsn53c94114ed5b",
        'x-rapidapi-host': "tennis-api-atp-wta-itf.p.rapidapi.com"
    }

    print(f"\n📊 ANALISI KILLER INSTINCT: {player_name}")
    conn.request("GET", f"/tennis/v2/atp/player/titles/{player_id}", headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8")).get('data', [])

    total_won = 0
    total_lost = 0

    for entry in data:
        rank = entry.get('tourRank', 'N/D')
        # Convertiamo in int per evitare il TypeError
        won = int(entry.get('titlesWon', 0))
        lost = int(entry.get('titlesLost', 0))

        total_won += won
        total_lost += lost

        if won > 0 or lost > 0:
            win_rate = (won / (won + lost)) * 100 if (won + lost) > 0 else 0
            print(
                f"🏆 {rank.ljust(15)} | Vinte: {str(won).ljust(2)} | Perse: {str(lost).ljust(2)} | Win-Rate: {win_rate:.1f}%")

    print(f"---")
    final_rate = (total_won / (total_won + total_lost)) * 100 if (total_won + total_lost) > 0 else 0
    print(f"🔥 TOTALI: {total_won} Titoli vinti su {total_won + total_lost} Finali giocate.")
    print(f"🎯 KILLER INSTINCT TOTALE: {final_rate:.2f}%")

    return final_rate


# Test definitivo
analyze_titles_efficiency("5992", "Novak Djokovic")
analyze_titles_efficiency("47275", "Jannik Sinner")