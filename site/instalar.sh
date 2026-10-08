#!/bin/bash
set -e

em_portugues() {
  local v="${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}"
  if [ -z "$v" ] && [ "$(uname)" = "Darwin" ]; then
    v="$(defaults read -g AppleLocale 2>/dev/null || true)"
  fi
  case "$v" in
    pt*|PT*) return 0 ;;
    *) return 1 ;;
  esac
}

if em_portugues; then PT=1; else PT=0; fi

m() {
  if [ "$PT" = 1 ]; then printf '%s\n' "$1"; else printf '%s\n' "$2"; fi
}

principal() {
  ORIGEM="${1%/}"
  if [ -z "$ORIGEM" ]; then
    m "Uso: curl -fsSL ENDERECO-DO-SITE/instalar.sh | bash -s -- ENDERECO-DO-SITE" \
      "Usage: curl -fsSL SITE-ADDRESS/instalar.sh | bash -s -- SITE-ADDRESS"
    exit 1
  fi
  DESTINO="$HOME/Deck"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  m "Baixando o Deck…" "Downloading Deck…"
  curl -fsSL "$ORIGEM/deck.zip" -o "$TMP/deck.zip"
  if command -v unzip >/dev/null 2>&1; then
    unzip -q "$TMP/deck.zip" -d "$TMP/novo"
  else
    python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$TMP/deck.zip" "$TMP/novo"
  fi
  NOVO="$TMP/novo/deck"
  if [ ! -f "$NOVO/server.py" ]; then
    m "O arquivo baixado não parece ser o Deck." "The downloaded file doesn't look like Deck."
    exit 1
  fi
  if [ -f "$DESTINO/server.py" ]; then
    m "Atualizando o Deck em $DESTINO (seus botões e ícones ficam)…" \
      "Updating Deck in $DESTINO (your buttons and icons stay)…"
    if [ -f "$DESTINO/config.json" ]; then
      rm -f "$NOVO/config.json"
    fi
  else
    m "Instalando o Deck em $DESTINO…" "Installing Deck in $DESTINO…"
  fi
  mkdir -p "$DESTINO"
  cp -R "$NOVO/." "$DESTINO/"
  chmod +x "$DESTINO/Iniciar no Mac.command" "$DESTINO/iniciar-linux.sh" "$DESTINO/server.py" 2>/dev/null || true
  if [ "$(uname)" = "Darwin" ]; then
    xattr -dr com.apple.quarantine "$DESTINO" 2>/dev/null || true
  fi
  rm -rf "$TMP"
  trap - EXIT
  m "Pronto: $DESTINO" "Done: $DESTINO"
  if [ "$(uname)" = "Darwin" ]; then
    m "Da próxima vez, dê duplo clique em \"Iniciar no Mac.command\" dentro da pasta Deck." \
      "Next time, double-click \"Iniciar no Mac.command\" inside the Deck folder."
    if ! python3 -c pass >/dev/null 2>&1; then
      echo
      m "O macOS vai pedir para instalar as \"ferramentas de linha de comando\": aceite, espere terminar e rode este comando de novo (ou dê duplo clique em \"Iniciar no Mac.command\")." \
        "macOS will ask to install the \"command line developer tools\": accept, wait for it to finish and run this command again (or double-click \"Iniciar no Mac.command\")."
      exit 0
    fi
  else
    m "Da próxima vez, rode ./iniciar-linux.sh dentro da pasta Deck." \
      "Next time, run ./iniciar-linux.sh inside the Deck folder."
    if ! command -v python3 >/dev/null 2>&1; then
      m "Falta o Python 3: instale pelo gerenciador de pacotes (por exemplo, sudo apt install python3) e rode este comando de novo." \
        "Python 3 is missing: install it with your package manager (for example, sudo apt install python3) and run this command again."
      exit 1
    fi
  fi
  m "Ligando o deck…" "Starting the deck…"
  cd "$DESTINO"
  exec python3 server.py
}

principal "$@"
