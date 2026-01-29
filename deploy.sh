#!/bin/bash

# V164: Script per il Report delle Modifiche (Git Intelligence)

# Controlla se ci sono modifiche da committare
if [ -z "$(git status --porcelain)" ]; then
    echo "Nessuna modifica da committare."
    exit 0
fi

# 1. Genera un report tecnico delle differenze di codice
echo "📝 Generazione del report delle modifiche..."
git diff HEAD~1 HEAD --stat > logs/code_changes_report.txt

# 2. Carica tutto su GitHub
echo "⬆️ Aggiunta dei file e commit..."
git add .

# Chiedi un messaggio di commit descrittivo
echo "Inserisci un messaggio di commit per la V164 (es: Fix: Allineamento API Client):"
read -r commit_message

git commit -m "V164: $commit_message"

echo "🚀 Push su origin main..."
git push origin main

echo "✅ Processo di deploy completato!"
