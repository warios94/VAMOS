import requests
import json

headers = {
    "X-RapidAPI-Key": "1397977a20msh6113f4f1a0ec3c4p157aadjsn53c94114ed5b",
    "X-RapidAPI-Host": "tennis-api-atp-wta-itf.p.rapidapi.com"
}

# Proviamo i tre ingressi standard della V2
endpoints = [
    "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/seasons",
    "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/tournaments",
    "https://tennis-api-atp-wta-itf.p.rapidapi.com/tennis/v2/active-tournaments"
]

print("📡 Avvio scansione profonda degli endpoint...")

for url in endpoints:
    print(f"\n🔍 Testando: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', [])
            print(f"✅ SUCCESSO! Trovati {len(data)} elementi.")

            # Cerchiamo tracce di "2026" o "Australian"
            for item in data[:20]:  # Controlliamo i primi 20 per non intasare il log
                name = item.get('name', '')
                item_id = item.get('id')
                print(f"   📍 {name} (ID: {item_id})")

                if "2026" in str(name) or "Australian" in str(name):
                    print(f"      🔥 TARGET TROVATO: {name} ID -> {item_id}")
        else:
            print(f"❌ Errore {response.status_code}")
    except Exception as e:
        print(f"⚠️ Errore tecnico: {e}")

print("\n🏁 Scansione terminata.")