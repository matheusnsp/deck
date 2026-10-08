#!/bin/bash
set -e

principal() {
  ORIGEM="${1%/}"
  if [ -z "$ORIGEM" ]; then
    echo "Uso: curl -fsSL ENDERECO-DO-SITE/instalar.sh | bash -s -- ENDERECO-DO-SITE"
    exit 1
  fi
  DESTINO="$HOME/Deck"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "Baixando o Deck…"
  curl -fsSL "$ORIGEM/deck.zip" -o "$TMP/deck.zip"
  if command -v unzip >/dev/null 2>&1; then
    unzip -q "$TMP/deck.zip" -d "$TMP/novo"
  else
    python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$TMP/deck.zip" "$TMP/novo"
  fi
  NOVO="$TMP/novo/deck"
  if [ ! -f "$NOVO/server.py" ]; then
    echo "O arquivo baixado não parece ser o Deck."
    exit 1
  fi
  if [ -f "$DESTINO/server.py" ]; then
    echo "Atualizando o Deck em $DESTINO (seus botões e ícones ficam)…"
    if [ -f "$DESTINO/config.json" ]; then
      rm -f "$NOVO/config.json"
    fi
  else
    echo "Instalando o Deck em $DESTINO…"
  fi
  mkdir -p "$DESTINO"
  cp -R "$NOVO/." "$DESTINO/"
  chmod +x "$DESTINO/Iniciar no Mac.command" "$DESTINO/iniciar-linux.sh" "$DESTINO/server.py" 2>/dev/null || true
  if [ "$(uname)" = "Darwin" ]; then
    xattr -dr com.apple.quarantine "$DESTINO" 2>/dev/null || true
  fi
  rm -rf "$TMP"
  trap - EXIT
  echo "Pronto: $DESTINO"
  if [ "$(uname)" = "Darwin" ]; then
    echo "Da próxima vez, dê duplo clique em \"Iniciar no Mac.command\" dentro da pasta Deck."
    if ! python3 -c pass >/dev/null 2>&1; then
      echo
      echo "O macOS vai pedir para instalar as \"ferramentas de linha de comando\": aceite, espere terminar e rode este comando de novo (ou dê duplo clique em \"Iniciar no Mac.command\")."
      exit 0
    fi
  else
    echo "Da próxima vez, rode ./iniciar-linux.sh dentro da pasta Deck."
    if ! command -v python3 >/dev/null 2>&1; then
      echo "Falta o Python 3: instale pelo gerenciador de pacotes (por exemplo, sudo apt install python3) e rode este comando de novo."
      exit 1
    fi
  fi
  echo "Ligando o deck…"
  cd "$DESTINO"
  exec python3 server.py
}

principal "$@"
