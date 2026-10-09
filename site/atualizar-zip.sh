#!/bin/bash
set -e
cd "$(dirname "$0")/.."
find deck -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
rm -f site/deck.zip
zip -r -q site/deck.zip deck -x "*.DS_Store" "deck/config.local.json" "deck/autoteste.txt" "deck/.config-anterior.json" "deck/icones/*.png" "deck/icones/*.jpg" "deck/icones/*.jpeg" "deck/icones/*.svg" "deck/icones/*.gif" "deck/icones/*.webp" "deck/.deck-dados/*" "deck/.deck-cache/*"
echo "site/deck.zip atualizado ($(du -h site/deck.zip | cut -f1))"
