# V53: Hardcoded Sofascore IDs for key players
# This dictionary is used to ensure correct player identification, bypassing potential API mapping errors.

PLAYER_SOFASCORE_IDS = {
    # UOMINI
    'Jannik Sinner': 249137,
    'Novak Djokovic': 14882,
    'Carlos Alcaraz': 275923,
    'Alexander Zverev': 57163,
    'Ben Shelton': 399105, # Corretto ID per Ben Shelton
    'Lorenzo Musetti': 261015,
    'Alex de Minaur': 201239,
    'Learner Tien': 412818, # Esempio, verificare se necessario

    # DONNE
    'Aryna Sabalenka': 157754,
    'Coco Gauff': 264983,
    'Iga Swiatek': 228272,
    'Elena Rybakina': 186312,
    'Jessica Pegula': 44834,
    'Amanda Anisimova': 230628
}

# V53: Stime manuali per la fatica (rolling_minutes) per i Quarti AO
# Usato come fallback se l'API fallisce per questi giocatori.
MANUAL_FATIGUE_ESTIMATES = {
    'Jannik Sinner': 180,
    'Novak Djokovic': 190,
    'Carlos Alcaraz': 180,
    'Alexander Zverev': 220, # Esempio
    'Aryna Sabalenka': 150,  # Esempio
    'Coco Gauff': 160,       # Esempio
    'Lorenzo Musetti': 320,
    'Ben Shelton': 290,
    'Alex de Minaur': 250
}
