import json
import os
import time

def get_or_fetch_player(player_id, api_client, registry_path='data/players_registry.json'):
    """
    V163: Implementa la logica "Lookup Blindato". Cerca prima nel Vault locale,
    poi esegue un fetch chirurgico se il giocatore non è presente.
    """
    # 1. Carica il registro locale
    registry = {}
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            try:
                registry = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ File del registro {registry_path} corrotto o vuoto. Verrà ricreato.")
                registry = {}

    # 2. Controlla se il giocatore è già in "cassaforte"
    p_id_str = str(player_id)
    if p_id_str in registry:
        print(f"✅ Dati per ID {p_id_str} ({registry[p_id_str].get('name')}) recuperati dal Vault locale.")
        return registry[p_id_str]

    # 3. Se non c'è, esegui la "Chirurgia"
    print(f"📡 ID {p_id_str} non nel Vault. Eseguo fetch chirurgico...")
    
    try:
        response = api_client.get_player_profile(p_id_str)
        
        if response:
            player_data = {
                "name": response.get('name'),
                "points": response.get('ranking_points') or response.get('points') or 0,
                "ranking": response.get('ranking') or 999,
                "last_update": time.strftime("%Y-%m-%d")
            }
            
            registry[p_id_str] = player_data
            if not os.path.exists('data'):
                os.makedirs('data')
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"💾 {player_data['name']} salvato nel Vault.")
            return player_data
            
    except Exception as e:
        print(f"❌ Errore nel fetch chirurgico per l'ID {p_id_str}: {e}")
    
    print(f"⚠️ Impossibile recuperare i dati per l'ID {p_id_str}. Analisi a rischio.")
    return None
