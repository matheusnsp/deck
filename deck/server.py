#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import ctypes
import errno
import hashlib
import hmac
import html.parser
import http.client
import ipaddress
import json
import os
import platform
import plistlib
import queue
import re
import secrets
import shlex
import shutil
import socket
import socketserver
import sqlite3
import ssl
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import unicodedata
import urllib.error
import urllib.request
import webbrowser
import zlib
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as TempoEsgotado
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlencode, urljoin, urlparse

VERSAO = "3.2.6"
PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_WEB = os.path.join(PASTA, "web")
PASTA_ICONES = os.path.join(PASTA, "icones")
PASTA_SITE = os.path.join(os.path.dirname(PASTA), "site")
ARQ_CONFIG = os.path.join(PASTA, "config.json")
ARQ_CONFIG_LOCAL = os.path.join(PASTA, "config.local.json")
ARQ_TOKEN_ANTIGO = os.path.join(PASTA, ".token")
PORTA_PADRAO = 8787


def _detectar_sistema():
    forcado = os.environ.get("DECK_SISTEMA", "").strip().lower()
    if forcado in ("mac", "windows", "linux"):
        return forcado
    if sys.platform == "darwin":
        return "mac"
    if os.name == "nt":
        return "windows"
    return "linux"


SISTEMA = _detectar_sistema()
NOMES_SISTEMA = {"mac": "Mac", "windows": "Windows", "linux": "Linux"}

IDIOMAS = ("pt", "en")


def idioma_do_sistema():
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        v = os.environ.get(var, "").strip()
        if v and v.split(".")[0] not in ("C", "POSIX", ""):
            return "pt" if v.lower().startswith("pt") else "en"
    try:
        if SISTEMA == "windows":
            codigo = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            return "pt" if (codigo & 0x3FF) == 0x16 else "en"
        if SISTEMA == "mac":
            for chave in ("AppleLanguages", "AppleLocale"):
                r = subprocess.run(["defaults", "read", "-g", chave], capture_output=True, text=True, timeout=3)
                m = re.search(r"[A-Za-z]{2}", r.stdout or "")
                if r.returncode == 0 and m:
                    return "pt" if m.group(0).lower() == "pt" else "en"
    except Exception:
        pass
    return "pt"


IDIOMA_SISTEMA = idioma_do_sistema()
IDIOMA_FORCADO = os.environ.get("DECK_IDIOMA", "").strip().lower()
IDIOMA = IDIOMA_FORCADO if IDIOMA_FORCADO in IDIOMAS else IDIOMA_SISTEMA


def idioma_pedido(v):
    v = str(v or "").strip().lower()
    if v in ("en", "en-us", "en_us", "english", "ingles", "inglês"):
        return "en"
    if v in ("pt", "pt-br", "pt_br", "portugues", "português"):
        return "pt"
    return "auto"


def definir_idioma(preferencia):
    global IDIOMA
    if IDIOMA_FORCADO in IDIOMAS:
        IDIOMA = IDIOMA_FORCADO
    else:
        p = idioma_pedido(preferencia)
        IDIOMA = p if p in IDIOMAS else IDIOMA_SISTEMA
    return IDIOMA


def tr(texto):
    if IDIOMA == "en":
        return TEXTOS_EN.get(texto, texto)
    return texto


NOMES_PAGINAS_EN = {"Favoritos": "Favorites", "Mídia": "Media", "Produtividade": "Productivity", "Sistema": "System",
                    "Modos": "Modes", "Chamadas": "Calls",
                    "Apps": "Apps", "Sites": "Sites", "Jogos": "Games", "Trabalho": "Work", "Casa": "Home",
                    "Música": "Music", "Conversas": "Chats", "Reuniões": "Meetings", "Estúdio": "Studio", "Código": "Code"}
NOMES_PAGINAS_PT = {en: pt for pt, en in NOMES_PAGINAS_EN.items()}
TITULOS_EN = {"Navegador": "Browser", "Arquivos": "Files", "Calculadora": "Calculator", "Notas": "Notes",
              "Captura": "Screenshot", "Ajustes": "Settings", "Agenda": "Calendar", "Planilhas": "Sheets",
              "Tocar/Pausar": "Play/Pause", "Anterior": "Previous", "Próxima": "Next", "Mudo": "Mute",
              "Microfone": "Microphone", "Copiar": "Copy", "Colar": "Paste", "Desfazer": "Undo", "Nova aba": "New tab",
              "Fechar aba": "Close tab", "Trocar app": "Switch app", "Já volto": "Be right back", "Bloquear": "Lock",
              "Suspender": "Sleep", "Reiniciar": "Restart", "Desligar": "Shut down", "Área de trabalho": "Desktop",
              "Foco": "Focus", "Trabalho": "Work", "Estudos": "Study", "Casa": "Home", "Pausa": "Break",
              "Atender": "Answer", "Recusar": "Decline", "Mudo na chamada": "Mute call", "Câmera": "Camera",
              "Encerrar": "Hang up"}
TITULOS_PT = {en: pt for pt, en in TITULOS_EN.items()}
TEXTOS_EXEMPLO_EN = {"Já te respondo!": "I'll get back to you soon!"}
TEXTOS_EXEMPLO_PT = {en: pt for pt, en in TEXTOS_EXEMPLO_EN.items()}


def _trocar(d, chave, mapa):
    v = d.get(chave)
    if isinstance(v, str) and v in mapa:
        d[chave] = mapa[v]


def traduzir_nomes_padrao(dados):
    if not isinstance(dados, dict) or not isinstance(dados.get("paginas"), list):
        return
    en = IDIOMA == "en"
    paginas = NOMES_PAGINAS_EN if en else NOMES_PAGINAS_PT
    titulos = TITULOS_EN if en else TITULOS_PT
    textos = TEXTOS_EXEMPLO_EN if en else TEXTOS_EXEMPLO_PT
    for p in dados["paginas"]:
        if not isinstance(p, dict):
            continue
        _trocar(p, "nome", paginas)
        botoes = p.get("botoes")
        if not isinstance(botoes, list):
            continue
        for b in botoes:
            if not isinstance(b, dict):
                continue
            _trocar(b, "titulo", titulos)
            if b.get("tipo") == "texto":
                _trocar(b, "texto", textos)
            if b.get("tipo") in ("pagina", "página"):
                _trocar(b, "pagina", paginas)
                _trocar(b, "titulo", paginas)
            if b.get("tipo") == "modo":
                _trocar(b, "pagina", paginas)


TEXTOS_EN = {
    'O programa "%s" não existe neste computador.': 'The program "%s" does not exist on this computer.',
    "   ↳ %s terminou (código %s)": "   ↳ %s finished (code %s)",
    "Não consegui abrir (%s).": "Couldn't open it (%s).",
    "%s: combinação de teclas vazia": "%s: empty key combination",
    '%s: "%s" está mal escrito (exemplo certo: "ctrl+shift+4")': '%s: "%s" is misspelled (correct example: "ctrl+shift+4")',
    '%s: "%s" não é modificador (use ctrl, alt, shift, cmd ou win)': '%s: "%s" is not a modifier (use ctrl, alt, shift, cmd or win)',
    '%s: não conheço a tecla "%s" (em "%s")': '%s: unknown key "%s" (in "%s")',
    "O macOS bloqueou o controle do teclado. Ative o Terminal (ou o app onde o deck roda) em "
    "Ajustes do Sistema › Privacidade e Segurança › Acessibilidade. Se já estiver ativo, "
    "feche o Terminal e ligue o deck de novo.":
        "macOS blocked keyboard control. Enable Terminal (or the app running the deck) in "
        "System Settings › Privacy & Security › Accessibility. If it is already enabled, "
        "close Terminal and start the deck again.",
    "Falta permissão de Automação: Ajustes do Sistema › Privacidade e Segurança › Automação › "
    "Terminal → ative “System Events”.":
        "Automation permission is missing: System Settings › Privacy & Security › Automation › "
        "Terminal → enable “System Events”.",
    "A saída de som atual não deixa o macOS controlar o volume (comum em HDMI e alguns monitores).":
        "The current sound output doesn't let macOS control the volume (common with HDMI and some monitors).",
    "Falhou sem mensagem.": "Failed without a message.",
    "Botões do app Atalhos só funcionam no Mac.": "Shortcuts app buttons only work on a Mac.",
    "AppleScript só funciona no Mac.": "AppleScript only works on a Mac.",
    "Este computador não sabe %s pelo deck.": "This computer can't %s from the deck.",
    "Comando rodando no computador…": "Command running on the computer…",
    "O comando terminou com erro (%d): %s": "The command ended with an error (%d): %s",
    "sem mensagem": "no message",
    "Não achei o navegador “%s” neste computador.": "Couldn't find the browser “%s” on this computer.",
    "Não achei “%s” neste Mac (use o nome que aparece na pasta Aplicativos).":
        "Couldn't find “%s” on this Mac (use the name shown in the Applications folder).",
    "Não consegui abrir o link.": "Couldn't open the link.",
    "⚠ Para ver as abas abertas e trazê-las para frente, permita que o Terminal controle o "
    "Safari/Chrome: Ajustes do Sistema › Privacidade e Segurança › Automação.":
        "⚠ To see open tabs and bring them to the front, allow Terminal to control "
        "Safari/Chrome: System Settings › Privacy & Security › Automation.",
    "Não consegui abrir o site no %s.": "Couldn't open the site in %s.",
    "atalho “%s”": "shortcut “%s”",
    "Atalho rodando no Mac…": "Shortcut running on the Mac…",
    "Não achei o atalho “%s” no app Atalhos do Mac.": "Couldn't find the shortcut “%s” in the Mac's Shortcuts app.",
    "Atalho falhou: %s": "Shortcut failed: %s",
    "código %d": "code %d",
    "Não consegui bloquear a tela.": "Couldn't lock the screen.",
    "Não consegui suspender o Mac: %s": "Couldn't put the Mac to sleep: %s",
    "Este microfone não deixa o macOS mexer no volume. Use o mudo do próprio app de reunião.":
        "This microphone doesn't let macOS change its volume. Use the mute in the meeting app itself.",
    "A tecla “%s” não existe no layout de teclado atual.": "The key “%s” doesn't exist in the current keyboard layout.",
    "O Windows não aceitou as teclas (erro %s). Se o app da frente roda como "
    "administrador, rode o deck como administrador também.":
        "Windows rejected the keys (error %s). If the app in front runs as "
        "administrator, run the deck as administrator too.",
    "O Windows não abriu “%s” (%s).": "Windows didn't open “%s” (%s).",
    "Não achei “%s” no Windows. Use o nome que aparece no menu Iniciar ou o caminho do .exe.":
        "Couldn't find “%s” on Windows. Use the name shown in the Start menu or the path to the .exe.",
    "Não consegui falar com o áudio do Windows. %s": "Couldn't talk to Windows audio. %s",
    "Resposta estranha do áudio do Windows.": "Strange answer from Windows audio.",
    "Este computador não tem saída de som ativa.": "This computer has no active sound output.",
    "Não consegui bloquear o Windows.": "Couldn't lock Windows.",
    "Não consegui suspender o Windows.": "Couldn't put Windows to sleep.",
    "Não consegui %s o Windows.": "Couldn't %s Windows.",
    "Não achei um microfone padrão no Windows.": "Couldn't find a default microphone on Windows.",
    "Para teclas e texto no Linux, instale o xdotool (sudo apt install xdotool). "
    "Em sessão Wayland, instale o wtype.":
        "For keys and text on Linux, install xdotool (sudo apt install xdotool). "
        "In a Wayland session, install wtype.",
    "Para volume e microfone no Linux, é preciso o pactl (PulseAudio/PipeWire) ou o wpctl.":
        "For volume and microphone on Linux you need pactl (PulseAudio/PipeWire) or wpctl.",
    "Para mídia no Linux, instale o playerctl (sudo apt install playerctl).":
        "For media on Linux, install playerctl (sudo apt install playerctl).",
    "%s falhou: %s": "%s failed: %s",
    "O atalho %s não diz como abrir o app.": "The launcher %s doesn't say how to open the app.",
    "Não achei “%s” neste Linux (use o nome do menu de aplicativos ou o comando).":
        "Couldn't find “%s” on this Linux (use the name from the applications menu or the command).",
    "O atalho do %s não diz como abrir sites.": "The %s launcher doesn't say how to open sites.",
    "Nenhum player de mídia respondeu.": "No media player answered.",
    "Não consegui ler o volume atual.": "Couldn't read the current volume.",
    "Não consegui %s o computador.": "Couldn't %s the computer.",
    "Não achei um microfone padrão.": "Couldn't find a default microphone.",
    "Desligar": "Shut down", "Reiniciar": "Restart", "Suspender": "Sleep", "Bloquear": "Lock",
    '%s: falta "%s" (ex.: %s)': '%s: "%s" is missing (e.g. %s)',
    '%s: "%s" precisa ser um número de segundos (ex.: 0.5)': '%s: "%s" must be a number of seconds (e.g. 0.5)',
    "%s: sequência dentro de sequência demais": "%s: too many nested sequences",
    '%s: falta "tipo" (use: %s)': '%s: "tipo" is missing (use: %s)',
    '%s: tipo "%s" não existe (use: %s)': '%s: type "%s" does not exist (use: %s)',
    '%s: escreva as teclas, ex.: "teclas": "ctrl+c"': '%s: write the keys, e.g. "teclas": "ctrl+c"',
    "%s: no máximo 30 combinações por botão": "%s: at most 30 combinations per button",
    '%s: a tecla "%s" não existe no %s': '%s: the key "%s" does not exist on %s',
    '%s: falta "texto" (ex.: "texto": "Bom dia!")': '%s: "texto" is missing (e.g. "texto": "Good morning!")',
    '%s: falta "app" (ex.: "app": "Spotify")': '%s: "app" is missing (e.g. "app": "Spotify")',
    '"atalho": "Nome no app Atalhos"': '"atalho": "Name in the Shortcuts app"',
    '"comando": "echo oi"': '"comando": "echo hi"',
    '%s: "midia" deve ser play, proxima ou anterior': '%s: "midia" must be play, proxima or anterior',
    '%s: "volume" deve ser subir, descer, mudo ou um número de 0 a 100':
        '%s: "volume" must be subir, descer, mudo or a number from 0 to 100',
    '%s: "energia" deve ser desligar, reiniciar, suspender ou bloquear':
        '%s: "energia" must be desligar, reiniciar, suspender or bloquear',
    '%s: diga para qual página ir, ex.: "pagina": "Apps"': '%s: say which page to go to, e.g. "pagina": "Apps"',
    '%s: "acoes" deve ser uma lista de ações': '%s: "acoes" must be a list of actions',
    "%s: no máximo 30 passos por sequência": "%s: at most 30 steps per sequence",
    "%s, passo %d": "%s, step %d",
    "%s: cada passo é um { ... } com tipo": "%s: each step is a { ... } with a type",
    "%s: nenhum passo vale para o %s": "%s: no step applies to %s",
    "Este botão usa um recurso que só existe no Mac.": "This button uses a feature that only exists on the Mac.",
    '%s: cor "%s" não reconhecida (use #ff8800 ou %s)': '%s: unknown color "%s" (use #ff8800 or %s)',
    "Teclas": "Keys", "Texto": "Text", "Atalho": "Shortcut", "Comando": "Command", "Mídia": "Media",
    "Microfone": "Microphone", "Energia": "Power", "Página": "Page", "Sequência": "Sequence", "Esperar": "Wait",
    "Botão": "Button",
    'Página "%s", botão %d': 'Page "%s", button %d',
    "%s: formato inválido (use { ... } ou null para deixar vazio)": "%s: invalid format (use { ... } or null to leave it empty)",
    '%s: "imagem" deve ser só o nome de um arquivo .png/.jpg/.svg da pasta icones':
        '%s: "imagem" must be just the name of a .png/.jpg/.svg file in the icones folder',
    "%s: não achei icones/%s": "%s: couldn't find icones/%s",
    "Este botão não tem versão para %s.": "This button has no version for %s.",
    "%s: valor inválido (%s)": "%s: invalid value (%s)",
    "config.json precisa começar com { e terminar com }.": "config.json must start with { and end with }.",
    'config.json precisa de "paginas": [ ... ]': 'config.json needs "paginas": [ ... ]',
    "Página %d: formato inválido": "Page %d: invalid format",
    "Página %d": "Page %d",
    'Página "%s": "botoes" deve ser uma lista [ ... ]': 'Page "%s": "botoes" must be a list [ ... ]',
    'Página "%s", botão %d: não existe página "%s"': 'Page "%s", button %d: there is no page "%s"',
    "vírgula sobrando antes de } ou ]": "extra comma before } or ]",
    "faltou uma vírgula": "missing comma",
    "vírgula sobrando antes de } ou nome sem aspas duplas": "extra comma before } or a name without double quotes",
    "faltou um valor (vírgula sobrando antes de ] ?)": "missing value (extra comma before ] ?)",
    "faltou os dois-pontos depois do nome": "missing colon after the name",
    "aspas abertas e não fechadas": "quotes opened and not closed",
    "quebra de linha dentro de um texto (use \\n)": "line break inside a text (use \\n)",
    "sobrou texto depois do último }": "text left over after the last }",
    "barra invertida inválida (use \\\\ ou /)": "invalid backslash (use \\\\ or /)",
    "config.json não está salvo em UTF-8.": "config.json is not saved as UTF-8.",
    "config.json com erro na linha %d, coluna %d: %s": "config.json has an error on line %d, column %d: %s",
    "cabo USB": "USB cable", "rede do computador": "computer's network",
    "Não consegui abrir %s.": "Couldn't open %s.",
    "Erro ao buscar o ícone oficial de %s:\n%s": "Error fetching the official icon of %s:\n%s",
    "Erro ao buscar ícones:\n": "Error fetching icons:\n",
    "Erro ao ler favoritos/histórico:\n": "Error reading bookmarks/history:\n",
    "Erro ao listar os apps:\n": "Error listing apps:\n",
    "Erro inesperado:\n": "Unexpected error:\n",
    "Erro inesperado no computador: %s": "Unexpected error on the computer: %s",
    "… rodando": "… running",
    "Passo %d: %s": "Step %d: %s",
    "Não achei o config.json (%s).": "Couldn't find config.json (%s).",
    "Não consegui ler o config.json (%s).": "Couldn't read config.json (%s).",
    "↻ config.json recarregado": "↻ config.json reloaded",
    " — %d botões": " — %d buttons",
    "  (mantendo a versão anterior)": "  (keeping the previous version)",
    "Escreva o endereço do site.": "Type the site's address.",
    "Esse endereço não parece um site.": "That address doesn't look like a site.",
    "Nenhuma imagem recebida.": "No image received.",
    "Imagem inválida.": "Invalid image.",
    "Imagem grande demais (máximo 4 MB).": "Image too large (4 MB max).",
    "Use uma imagem PNG, JPG, GIF, WEBP ou SVG.": "Use a PNG, JPG, GIF, WEBP or SVG image.",
    "Configuração inválida.": "Invalid configuration.",
    "Páginas ou botões demais.": "Too many pages or buttons.",
    "Não salvei: %s": "Not saved: %s",
    "O config.json mudou fora do editor — carreguei a versão nova.": "config.json changed outside the editor — the new version was loaded.",
    "Não consegui salvar o config.json (%s).": "Couldn't save config.json (%s).",
    "✎ Botões salvos pelo editor": "✎ Buttons saved by the editor",
    "Os botões mudaram no computador — já atualizei aqui. Toque de novo.": "The buttons changed on the computer — updated here. Tap again.",
    "Esse botão não existe mais.": "That button no longer exists.",
    "Rodando no computador…": "Running on the computer…",
    "PC com Windows": "Windows PC", "PC com Linux": "Linux PC",
    "📱 %s conectado": "📱 %s connected",
    "Não consegui gravar o link novo (%s).": "Couldn't save the new link (%s).",
    "Link novo gerado pelo editor: os celulares precisam escanear o QR code de novo.":
        "New link generated by the editor: the phones need to scan the QR code again.",
    "Diga qual aparelho.": "Say which device.",
    "📱 %s (%s) desconectado pelo editor": "📱 %s (%s) disconnected by the editor",
    "Ação desconhecida.": "Unknown action.",
    "O Firewall do Mac está bloqueando o deck. Em Ajustes do Sistema › Rede › "
    "Firewall › Opções, mude o Python para \"Permitir conexões de entrada\" (ou clique em Permitir quando o aviso aparecer).":
        "The Mac's Firewall is blocking the deck. In System Settings › Network › "
        "Firewall › Options, set Python to \"Allow incoming connections\" (or click Allow when the prompt appears).",
    "O celular": "The phone",
    "%s estava usando o endereço %s, que este computador não tem mais — o link salvo "
    "nele não abre. Escaneie o QR code de novo (e prefira o link pelo nome, que não muda).":
        "%s was using the address %s, which this computer no longer has — the link saved "
        "on it won't open. Scan the QR code again (and prefer the link by name, which doesn't change).",
    "O nome deste computador na rede mudou de %s para %s (o Mac faz isso quando acha "
    "outro com o mesmo nome). Escaneie o QR code de novo, ou volte o nome em Ajustes do Sistema › Geral › "
    "Compartilhamento › Nome local.":
        "This computer's network name changed from %s to %s (the Mac does that when it finds "
        "another one with the same name). Scan the QR code again, or restore the name in System Settings › General › "
        "Sharing › Local hostname.",
    "Esta página só abre no próprio computador: http://localhost:%d/editar": "This page only opens on the computer itself: http://localhost:%d/editar",
    "Pedido grande demais.": "Request too large.",
    "Não encontrado.": "Not found.",
    "Pedido inválido.": "Invalid request.",
    "Esta página só abre no próprio computador.": "This page only opens on the computer itself.",
    "Esta página só abre no próprio computador: http://localhost:%d%s": "This page only opens on the computer itself: http://localhost:%d%s",
    "Ícone não encontrado.": "Icon not found.",
    "Erro interno:\n": "Internal error:\n",
    "Erro interno no computador (detalhes no terminal).": "Internal error on the computer (details in the terminal).",
    "Este aparelho foi desconectado pelo computador.": "This device was disconnected by the computer.",
    "Link antigo ou inválido. Escaneie o QR code de novo.": "Old or invalid link. Scan the QR code again.",
    "A pasta site/ não está ao lado da pasta do deck (ela existe só no repositório).": "The site/ folder is not next to the deck folder (it only exists in the repository).",
    "Faltou o arquivo web/%s — descompacte a pasta inteira.": "The file web/%s is missing — unzip the whole folder.",
    "O editor já estava aberto no navegador — não abri outra aba.": "The editor was already open in the browser — no new tab opened.",
    "Deck ligado ✓": "Deck is on ✓",
    "  Escolher os botões:  ": "  Choose the buttons:  ",
    "  Conectar o celular:  http://localhost:%d/parear": "  Connect the phone:   http://localhost:%d/parear",
    "  Link (IP):           ": "  Link (IP):           ",
    "  Link (nome):         ": "  Link (name):         ",
    "O que você muda no editor aparece no celular na hora. Deixe esta janela aberta; Ctrl+C desliga.":
        "Whatever you change in the editor shows up on the phone instantly. Keep this window open; Ctrl+C turns it off.",
    "Se o Windows perguntar sobre o Firewall, marque Redes privadas e clique em Permitir.":
        "If Windows asks about the Firewall, check Private networks and click Allow.",
    "Deck — o celular vira um painel de botões do computador.": "Deck — your phone becomes a button panel for the computer.",
    "abre a página com o QR code": "opens the page with the QR code",
    "troca o link secreto (desconecta os celulares)": "changes the secret link (disconnects the phones)",
    "não abre o editor no navegador ao ligar": "doesn't open the editor in the browser on start",
    "caminho do config.json (se existir config.local.json, ele é usado)": "path to config.json (if config.local.json exists, it is used)",
    "idioma da interface: auto, pt ou en": "interface language: auto, pt or en",
    "Precisa do Python 3.8 ou mais novo (você tem %d.%d).": "Python 3.8 or newer is required (you have %d.%d).",
    "A porta %d já está em uso — o deck já está aberto em outra janela?": "Port %d is already in use — is the deck already open in another window?",
    "\nFeche a outra janela ou use:  --porta %d": "\nClose the other window or use:  --porta %d",
    "Link novo gerado: os celulares precisam escanear o QR code de novo.": "New link generated: the phones need to scan the QR code again.",
    "\n  Deck desligado. Até a próxima!\n": "\n  Deck is off. See you next time!\n",
    "Deck — escolher os botões": "Deck — choose the buttons",
    "Conectar o celular — Deck": "Connect the phone — Deck",
    "Como usar o Deck": "How to use Deck",
    "Modo": "Mode", "Chamada": "Call", "ATIVO": "ON", "Desligado": "Off", "Mudo": "Muted", "Som": "Sound on", "Ligado": "On",
    "Atender": "Answer", "Recusar": "Decline", "Mudo na chamada": "Mute in call", "Câmera": "Camera", "Encerrar": "Hang up",
    "Valor inválido.": "Invalid value.",
    "Nada tocando no computador agora.": "Nothing is playing on the computer right now.",
    "O app que está tocando não aceitou esse comando.": "The app that's playing didn't accept that command.",
    "Este player não deixa pular para outro ponto.": "This player doesn't let you jump to another point.",
    "O Windows não informou o que está tocando.": "Windows didn't report what's playing.",
    "O %s foi fechado.": "%s was closed.",
    "Erro ao ler o que está tocando:\n": "Error reading what's playing:\n",
    "Este computador não deixa ligar o Não perturbe pelo deck.": "This computer doesn't let the deck turn on Do Not Disturb.",
    "O Não perturbe pelo deck precisa do app Atalhos (macOS 12 ou mais novo).":
        "Do Not Disturb from the deck needs the Shortcuts app (macOS 12 or newer).",
    "O atalho “%s” falhou: %s": "The shortcut “%s” failed: %s",
    "Para o Não perturbe, crie no app Atalhos os atalhos “Deck Foco Ligar” e “Deck Foco Desligar” (ação Definir Foco). Veja Como usar › Modos.":
        "For Do Not Disturb, create the shortcuts “Deck Focus On” and “Deck Focus Off” in the Shortcuts app (Set Focus action). See How to use › Modes.",
    "No Windows, o Não perturbe não liga por programa: ligue em Win+N › Não perturbe.":
        "On Windows, Do Not Disturb can't be turned on by a program: turn it on in Win+N › Do not disturb.",
    "Não consegui mudar o Não perturbe neste Linux (funciona no GNOME).": "I couldn't change Do Not Disturb on this Linux (it works on GNOME).",
    "Não sei fechar apps neste computador.": "I don't know how to close apps on this computer.",
    "⏱ %s: tempo encerrado": "⏱ %s: time's up",
    "Atender pelo deck só funciona no Mac. Use o botão do app da chamada.": "Answering from the deck only works on a Mac. Use the call app's button.",
    "A chamada não está mais tocando.": "The call isn't ringing anymore.",
    "Não achei nenhuma reunião aberta (Meet, Zoom, Teams, Webex ou FaceTime). Para Discord e Slack, escolha o app no botão.":
        "I couldn't find an open meeting (Meet, Zoom, Teams, Webex or FaceTime). For Discord and Slack, choose the app on the button.",
    "O %s não tem atalho para “%s”.": "%s has no shortcut for “%s”.",
    "Não achei a janela do %s para mandar o atalho.": "I couldn't find the %s window to send the shortcut to.",
    "📞 Chamada chegando: %s": "📞 Incoming call: %s",
    "⚠ Não consegui ver chamadas chegando (%s). Tento de novo em 5 minutos.": "⚠ I couldn't check for incoming calls (%s). Trying again in 5 minutes.",
    '%s: "volume" do modo deve ser um número de 0 a 100': '%s: the mode\'s "volume" must be a number from 0 to 100',
    '%s: "minutos" deve ser um número (ex.: 25)': '%s: "minutos" must be a number (e.g. 25)',
    "%s: o modo não faz nada — escolha o que ele abre, fecha ou liga": "%s: the mode does nothing — choose what it opens, closes or turns on",
    '%s: "chamada" deve ser atender, recusar, mudo, camera ou encerrar': '%s: "chamada" must be atender, recusar, mudo, camera or encerrar',
    '%s: app de chamada "%s" desconhecido (use auto, zoom, teams, meet, facetime, discord, slack ou webex)':
        '%s: unknown call app "%s" (use auto, zoom, teams, meet, facetime, discord, slack or webex)',
    '%s: no máximo 12 itens em "%s"': '%s: at most 12 items in "%s"',
    "%s: troca de página ou modo não pode ficar dentro de sequência": "%s: a page change or mode can't be inside a sequence",
}


def pasta_do_usuario(tipo):
    casa = os.path.expanduser("~")
    base = os.environ.get("DECK_DADOS")
    if base:
        alvo = os.path.join(base, tipo)
    elif SISTEMA == "mac":
        alvo = os.path.join(casa, "Library", "Caches" if tipo == "cache" else "Application Support", "Deck")
    elif SISTEMA == "windows":
        raiz = os.environ.get("LOCALAPPDATA" if tipo == "cache" else "APPDATA") or casa
        alvo = os.path.join(raiz, "Deck", "cache" if tipo == "cache" else "")
    else:
        xdg = os.environ.get("XDG_CACHE_HOME" if tipo == "cache" else "XDG_CONFIG_HOME")
        alvo = os.path.join(xdg or os.path.join(casa, ".cache" if tipo == "cache" else ".config"), "deck")
    alvo = alvo.rstrip("\\/") or alvo
    try:
        os.makedirs(alvo, exist_ok=True)
        return alvo
    except OSError:
        reserva = os.path.join(PASTA, ".deck-" + tipo)
        os.makedirs(reserva, exist_ok=True)
        return reserva


def _preparar_terminal():
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return False
    if os.name == "nt":
        try:
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            modo = ctypes.c_uint32()
            if not k.GetConsoleMode(h, ctypes.byref(modo)):
                return False
            return bool(k.SetConsoleMode(h, modo.value | 0x0004))
        except Exception:
            return False
    return True


_CORES = _preparar_terminal()
_trava_log = threading.Lock()


def _tinta(codigo, texto):
    return "\033[%sm%s\033[0m" % (codigo, texto) if _CORES else texto


def verde(t):
    return _tinta("32", t)


def vermelho(t):
    return _tinta("31", t)


def amarelo(t):
    return _tinta("33", t)


def cinza(t):
    return _tinta("90", t)


def negrito(t):
    return _tinta("1", t)


def log(msg):
    with _trava_log:
        print(cinza(time.strftime("%H:%M:%S")) + "  " + msg, flush=True)


class ErroConfig(Exception):
    pass


class ErroAcao(Exception):
    pass


def simples(valor):
    t = unicodedata.normalize("NFD", str(valor)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", "_", t.strip().lower())


def comparavel(valor):
    t = unicodedata.normalize("NFD", str(valor)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _int(valor, padrao):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao


def _num(x):
    return ("%.3f" % float(x)).rstrip("0").rstrip(".") or "0"


def _dec(b):
    if not b:
        return ""
    try:
        return b.decode("utf-8").strip()
    except UnicodeDecodeError:
        pass
    for codificacao in ("oem", "mbcs", "cp850"):
        try:
            return b.decode(codificacao).strip()
        except (LookupError, UnicodeDecodeError):
            continue
    return b.decode("latin-1").strip()


SEM_JANELA = 0x08000000 if os.name == "nt" else 0


def rodar(args, espera=10.0, rotulo=None, shell=False, ambiente=None):
    try:
        p = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=shell, env=ambiente, creationflags=SEM_JANELA)
    except FileNotFoundError:
        nome = args.split()[0] if isinstance(args, str) else args[0]
        raise ErroAcao(tr('O programa "%s" não existe neste computador.') % nome)
    try:
        saida, erro = p.communicate(timeout=espera)
    except subprocess.TimeoutExpired:
        def esperar_fim():
            p.communicate()
            if rotulo:
                log(cinza(tr("   ↳ %s terminou (código %s)") % (rotulo, p.returncode)))
        threading.Thread(target=esperar_fim, daemon=True).start()
        return None, "", ""
    return p.returncode, _dec(saida), _dec(erro)


def lancar(args):
    opcoes = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        opcoes["creationflags"] = 0x00000008 | 0x00000200
    else:
        opcoes["start_new_session"] = True
    try:
        p = subprocess.Popen(args, **opcoes)
    except FileNotFoundError:
        raise ErroAcao(tr('O programa "%s" não existe neste computador.') % args[0])
    except OSError as e:
        raise ErroAcao(tr("Não consegui abrir (%s).") % (e.strerror or e))
    threading.Thread(target=p.wait, daemon=True).start()


def _saida(args, ambiente=None):
    try:
        r = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=4, env=ambiente, creationflags=SEM_JANELA)
        return _dec(r.stdout) if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def palavras_do_nome(nome):
    return comparavel(re.sub(r"([a-z])([A-Z])", r"\1 \2", str(nome))).split()


def por_iniciais(alvo, nome):
    q = comparavel(alvo).replace(" ", "")
    p = palavras_do_nome(nome)
    if len(q) < 2 or len(p) < 2:
        return False

    def casa(i, j):
        if i == len(q):
            return True
        if j >= len(p):
            return False
        for n in range(min(len(p[j]), len(q) - i), 0, -1):
            if q[i:i + n] == p[j][:n] and casa(i + n, j + 1):
                return True
        return False
    return casa(0, 0)


def melhor_nome(alvo, opcoes):
    a = comparavel(alvo)
    if not a:
        return None
    melhor = None
    for nome, valor in opcoes:
        n = comparavel(nome)
        if not n:
            continue
        if n == a:
            nota = 0
        elif (" " + a + " ") in (" " + n + " "):
            nota = 1
        elif n.startswith(a):
            nota = 2
        elif (" " + a) in (" " + n):
            nota = 3
        elif a in n:
            nota = 4
        elif por_iniciais(alvo, nome):
            nota = 5
        else:
            continue
        if ("uninstall" in n or "desinstal" in n) and "instal" not in a:
            nota += 5
        chave = (nota, len(n))
        if melhor is None or chave < melhor[0]:
            melhor = (chave, valor)
    return melhor


ASSINATURA_PNG = b"\x89PNG\r\n\x1a\n"


def tipo_imagem(dados):
    if not dados:
        return None
    if dados[:8] == ASSINATURA_PNG:
        return ".png"
    if dados[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if dados[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
        return ".webp"
    if dados[:4] == b"\x00\x00\x01\x00" and len(dados) > 22:
        return ".ico"
    cabeca = dados[:4096].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if b"<svg" in cabeca and b"<html" not in cabeca and cabeca[:1] == b"<":
        return ".svg"
    return None


def tamanho_png(dados):
    if dados[:8] == ASSINATURA_PNG and dados[12:16] == b"IHDR" and len(dados) >= 24:
        return struct.unpack(">II", dados[16:24])
    return None


def png_rgba(largura, altura, rgba):
    def bloco(tipo, conteudo):
        return (struct.pack(">I", len(conteudo)) + tipo + conteudo
                + struct.pack(">I", zlib.crc32(tipo + conteudo) & 0xFFFFFFFF))

    passo = largura * 4
    linhas = bytearray()
    for y in range(altura):
        linhas += b"\x00"
        linhas += rgba[y * passo:(y + 1) * passo]
    cabecalho = struct.pack(">IIBBBBB", largura, altura, 8, 6, 0, 0, 0)
    return (ASSINATURA_PNG + bloco(b"IHDR", cabecalho) + bloco(b"IDAT", zlib.compress(bytes(linhas), 9))
            + bloco(b"IEND", b""))


def bgra_para_rgba(bgra):
    px = bytearray(bgra)
    rgba = bytearray(len(px))
    rgba[0::4] = px[2::4]
    rgba[1::4] = px[1::4]
    rgba[2::4] = px[0::4]
    rgba[3::4] = px[3::4]
    if not any(rgba[3::4]):
        rgba[3::4] = b"\xff" * (len(rgba) // 4)
        return rgba
    for i in range(0, len(rgba), 4):
        a = rgba[i + 3]
        if a < 255 and (rgba[i] > a or rgba[i + 1] > a or rgba[i + 2] > a):
            return rgba
    for i in range(0, len(rgba), 4):
        a = rgba[i + 3]
        if 0 < a < 255:
            meio = a // 2
            rgba[i] = min(255, (rgba[i] * 255 + meio) // a)
            rgba[i + 1] = min(255, (rgba[i + 1] * 255 + meio) // a)
            rgba[i + 2] = min(255, (rgba[i + 2] * 255 + meio) // a)
    return rgba


def png_do_icns(dados, alvo=256):
    if dados[:4] != b"icns":
        return None
    achados = []
    pos = 8
    while pos + 8 <= len(dados):
        tam = struct.unpack(">I", dados[pos + 4:pos + 8])[0]
        if tam < 8:
            break
        conteudo = dados[pos + 8:pos + tam]
        medida = tamanho_png(conteudo)
        if medida:
            achados.append((medida[0], conteudo))
        pos += tam
    if not achados:
        return None
    grandes = [a for a in achados if a[0] >= alvo]
    escolhido = min(grandes, key=lambda a: a[0]) if grandes else max(achados, key=lambda a: a[0])
    return escolhido[1]


def melhor_do_ico(dados):
    if len(dados) < 6 or dados[:4] != b"\x00\x00\x01\x00":
        return None
    total = struct.unpack("<H", dados[4:6])[0]
    melhor = None
    for k in range(min(total, 64)):
        entrada = dados[6 + 16 * k:22 + 16 * k]
        if len(entrada) < 16:
            break
        lado = entrada[0] or 256
        tam, desloc = struct.unpack("<II", entrada[8:16])
        conteudo = dados[desloc:desloc + tam]
        if len(conteudo) != tam or not tam:
            continue
        if melhor is None or lado > melhor[0]:
            melhor = (lado, conteudo)
    return melhor


def medida_imagem(dados):
    tipo = tipo_imagem(dados)
    try:
        if tipo == ".png":
            return max(tamanho_png(dados) or (0, 0))
        if tipo == ".gif":
            return max(struct.unpack("<HH", dados[6:10]))
        if tipo == ".svg":
            return 1000
        if tipo == ".ico":
            melhor = melhor_do_ico(dados)
            return melhor[0] if melhor else None
        if tipo == ".webp":
            bloco = dados[12:16]
            if bloco == b"VP8 ":
                return max(struct.unpack("<H", dados[26:28])[0] & 0x3FFF, struct.unpack("<H", dados[28:30])[0] & 0x3FFF)
            if bloco == b"VP8L":
                b = dados[21:25]
                largura = 1 + (((b[1] & 0x3F) << 8) | b[0])
                altura = 1 + (((b[3] & 0xF) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
                return max(largura, altura)
            if bloco == b"VP8X":
                return 1 + max(int.from_bytes(dados[24:27], "little"), int.from_bytes(dados[27:30], "little"))
        if tipo == ".jpg":
            pos = 2
            while pos + 9 < len(dados):
                if dados[pos] != 0xFF:
                    pos += 1
                    continue
                marca = dados[pos + 1]
                if 0xC0 <= marca <= 0xCF and marca not in (0xC4, 0xC8, 0xCC):
                    altura, largura = struct.unpack(">HH", dados[pos + 5:pos + 9])
                    return max(largura, altura)
                pos += 2 + struct.unpack(">H", dados[pos + 2:pos + 4])[0]
    except (struct.error, IndexError, TypeError):
        return None
    return None


def imagem_boa(dados):
    tipo = tipo_imagem(dados)
    if tipo == ".ico":
        melhor = melhor_do_ico(dados)
        if not melhor:
            return None
        if melhor[1][:8] == ASSINATURA_PNG:
            return melhor[1]
        return dados
    return dados if tipo else None


MODIFICADORES = {
    "cmd": "cmd", "command": "cmd", "comando": "cmd", "⌘": "cmd", "mod": "cmd",
    "ctrl": "ctrl", "control": "ctrl", "controle": "ctrl", "⌃": "ctrl",
    "alt": "alt", "opt": "alt", "option": "alt", "opcao": "alt", "⌥": "alt",
    "shift": "shift", "⇧": "shift",
    "win": "win", "windows": "win", "super": "win", "meta": "win",
}
ORDEM_MODS = ("ctrl", "alt", "shift", "cmd", "win")
TECLAS_NOMEADAS = {
    "enter": "enter", "return": "enter", "retorno": "enter",
    "tab": "tab", "space": "space", "espaco": "space",
    "backspace": "backspace", "apagar": "backspace",
    "delete": "delete",
    "del": "fdelete", "suprimir": "fdelete", "forwarddelete": "fdelete",
    "esc": "esc", "escape": "esc",
    "home": "home", "inicio": "home", "end": "end", "fim": "end",
    "pageup": "pageup", "pgup": "pageup", "pagedown": "pagedown", "pgdn": "pagedown",
    "left": "left", "esquerda": "left", "right": "right", "direita": "right",
    "up": "up", "cima": "up", "down": "down", "baixo": "down",
    "insert": "insert", "ins": "insert",
    "print": "print", "printscreen": "print", "prtsc": "print",
}
TECLAS_NOMEADAS.update({"f%d" % n: "f%d" % n for n in range(1, 25)})
APELIDOS_CARACTERE = {"mais": "+", "plus": "+", "menos": "-", "minus": "-", "virgula": ",", "ponto": ".", "barra": "/"}

MAC_MODS = {"cmd": "command down", "win": "command down", "ctrl": "control down", "alt": "option down",
            "shift": "shift down"}
MAC_CODIGOS = {
    "enter": 36, "tab": 48, "space": 49, "backspace": 51, "delete": 51, "fdelete": 117, "esc": 53,
    "home": 115, "end": 119, "pageup": 116, "pagedown": 121, "left": 123, "right": 124, "down": 125, "up": 126,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97, "f7": 98, "f8": 100, "f9": 101, "f10": 109,
    "f11": 103, "f12": 111, "f13": 105, "f14": 107, "f15": 113, "f16": 106, "f17": 64, "f18": 79, "f19": 80,
    "f20": 90,
}
MAC_MIDIA = {"play": 16, "proxima": 19, "anterior": 20}

WIN_VK = {
    "enter": 0x0D, "tab": 0x09, "space": 0x20, "backspace": 0x08, "delete": 0x2E, "fdelete": 0x2E, "esc": 0x1B,
    "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22, "left": 0x25, "up": 0x26, "right": 0x27,
    "down": 0x28, "insert": 0x2D, "print": 0x2C,
}
WIN_VK.update({"f%d" % n: 0x6F + n for n in range(1, 25)})
WIN_MODS = {"ctrl": 0x11, "cmd": 0x11, "alt": 0x12, "shift": 0x10, "win": 0x5B}
WIN_ESTENDIDAS = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E, 0x5B,
                  0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3}
WIN_MIDIA = {"play": 0xB3, "proxima": 0xB0, "anterior": 0xB1}

LINUX_TECLAS = {
    "enter": "Return", "tab": "Tab", "space": "space", "backspace": "BackSpace", "delete": "Delete",
    "fdelete": "Delete", "esc": "Escape", "home": "Home", "end": "End", "pageup": "Prior", "pagedown": "Next",
    "left": "Left", "right": "Right", "up": "Up", "down": "Down", "insert": "Insert", "print": "Print",
}
LINUX_TECLAS.update({"f%d" % n: "F%d" % n for n in range(1, 25)})
LINUX_MODS = {"ctrl": "ctrl", "cmd": "ctrl", "alt": "alt", "shift": "shift", "win": "super"}
WTYPE_MODS = {"ctrl": "ctrl", "cmd": "ctrl", "alt": "alt", "shift": "shift", "win": "logo"}
LINUX_SIMBOLOS = {
    "+": "plus", "-": "minus", ",": "comma", ".": "period", "/": "slash", "\\": "backslash", ";": "semicolon",
    "'": "apostrophe", "[": "bracketleft", "]": "bracketright", "=": "equal", "`": "grave", "*": "asterisk",
    "!": "exclam", "@": "at", "#": "numbersign", "$": "dollar", "%": "percent", "^": "asciicircum",
    "&": "ampersand", "(": "parenleft", ")": "parenright", "_": "underscore", "?": "question", ":": "colon",
    '"': "quotedbl", "<": "less", ">": "greater", "{": "braceleft", "}": "braceright", "|": "bar",
    "~": "asciitilde", " ": "space",
}
LINUX_MIDIA = {"play": ("play-pause", "XF86AudioPlay"), "proxima": ("next", "XF86AudioNext"),
               "anterior": ("previous", "XF86AudioPrev")}


def tecla_existe(nome, sistema=None):
    s = sistema or SISTEMA
    if s == "mac":
        return nome in MAC_CODIGOS
    if s == "windows":
        return nome in WIN_VK
    return nome in LINUX_TECLAS


def ler_combinacao(texto, onde):
    bruto = str(texto).strip()
    if not bruto:
        raise ErroConfig(tr("%s: combinação de teclas vazia") % onde)
    if bruto == "+":
        partes = ["+"]
    elif bruto.endswith("++"):
        partes = [p.strip() for p in bruto[:-2].split("+")] + ["+"]
    else:
        partes = [p.strip() for p in bruto.split("+")]
    if any(not p for p in partes):
        raise ErroConfig(tr('%s: "%s" está mal escrito (exemplo certo: "ctrl+shift+4")') % (onde, bruto))
    mods = set()
    for m in partes[:-1]:
        mm = MODIFICADORES.get(m.lower()) or MODIFICADORES.get(simples(m))
        if not mm:
            raise ErroConfig(tr('%s: "%s" não é modificador (use ctrl, alt, shift, cmd ou win)') % (onde, m))
        mods.add(mm)
    ordem = tuple(m for m in ORDEM_MODS if m in mods)
    tecla = partes[-1]
    if len(tecla) == 1:
        return (ordem, ("char", tecla.lower()))
    chave = simples(tecla).replace("_", "")
    if chave in APELIDOS_CARACTERE:
        return (ordem, ("char", APELIDOS_CARACTERE[chave]))
    nome = TECLAS_NOMEADAS.get(chave)
    if not nome:
        raise ErroConfig(tr('%s: não conheço a tecla "%s" (em "%s")') % (onde, tecla, bruto))
    return (ordem, ("nome", nome))


def as_texto(s):
    partes = re.split(r"\r\n|\r|\n", str(s))
    return " & linefeed & ".join('"' + p.replace("\\", "\\\\").replace('"', '\\"') + '"' for p in partes)


def as_combo(combo):
    mods, (tipo, valor) = combo
    usando = []
    for m in mods:
        if MAC_MODS[m] not in usando:
            usando.append(MAC_MODS[m])
    sufixo = (" using {%s}" % ", ".join(usando)) if usando else ""
    if tipo == "char":
        return "keystroke " + as_texto(valor) + sufixo
    return "key code %d%s" % (MAC_CODIGOS[valor], sufixo)


def _ativar_mac(app):
    return ["tell application %s to activate" % as_texto(app), "delay 0.3"] if app else []


def script_teclas(combos, app=None, intervalo=0.08):
    linhas = _ativar_mac(app) + ['tell application "System Events"']
    for n, c in enumerate(combos):
        if n:
            linhas.append("\tdelay " + _num(intervalo))
        linhas.append("\t" + as_combo(c))
    linhas.append("end tell")
    return "\n".join(linhas)


def script_texto(texto, app=None):
    return "\n".join(_ativar_mac(app) + [
        "set antigo to missing value",
        "try",
        "\tset antigo to (the clipboard as text)",
        "end try",
        "set the clipboard to " + as_texto(texto),
        "delay 0.05",
        'tell application "System Events" to keystroke "v" using {command down}',
        "delay 0.6",
        "if antigo is not missing value then set the clipboard to antigo",
    ])


def script_volume(op):
    if op == "subir":
        return "\n".join([
            "set v to output volume of (get volume settings)",
            'if v is missing value then error "sem-volume"',
            "set v to v + 6",
            "if v > 100 then set v to 100",
            "set volume output volume v",
            "set volume output muted false",
            "return v",
        ])
    if op == "descer":
        return "\n".join([
            "set v to output volume of (get volume settings)",
            'if v is missing value then error "sem-volume"',
            "set v to v - 6",
            "if v < 0 then set v to 0",
            "set volume output volume v",
            "return v",
        ])
    if op == "mudo":
        return "\n".join([
            "set m to output muted of (get volume settings)",
            'if m is missing value then error "sem-volume"',
            "set volume output muted (not m)",
            "return (not m)",
        ])
    n = max(0, min(100, int(op)))
    return "set volume output volume %d\nset volume output muted false\nreturn %d" % (n, n)


JXA_MIDIA = r"""
ObjC.import('AppKit');
ObjC.import('CoreGraphics');
var confiavel = true;
try { ObjC.import('ApplicationServices'); confiavel = $.AXIsProcessTrusted(); } catch (e) { confiavel = true; }
if (confiavel === false || confiavel === 0) { throw new Error('sem-acessibilidade'); }
[0xa, 0xb].forEach(function (fase) {
  var ev = $.NSEvent.otherEventWithTypeLocationModifierFlagsTimestampWindowNumberContextSubtypeData1Data2(
    14, {x: 0, y: 0}, fase << 8, 0, 0, null, 8, (CODIGO << 16) | (fase << 8), -1);
  $.CGEventPost(0, ev.CGEvent);
});
'ok';
"""

JXA_TOCANDO = r"""
ObjC.import('Foundation');
function nulo(v) { return v === undefined || v === null || (v.isNil && v.isNil()); }
function texto(v) {
  if (nulo(v)) return '';
  try { var s = ObjC.unwrap(v); return s === undefined || s === null ? '' : String(s); } catch (e) { return ''; }
}
function numero(v) {
  if (nulo(v)) return null;
  try { var n = ObjC.unwrap(v); n = Number(n); return isFinite(n) ? n : null; } catch (e) { return null; }
}
function run(argv) {
  var mr = $.NSBundle.bundleWithPath('/System/Library/PrivateFrameworks/MediaRemote.framework/');
  if (nulo(mr)) return JSON.stringify({erro: 'sem-mediaremote'});
  mr.load;
  var R = $.NSClassFromString('MRNowPlayingRequest');
  if (nulo(R)) return JSON.stringify({erro: 'sem-mediaremote'});
  var item = R.localNowPlayingItem;
  if (nulo(item)) return JSON.stringify({tem: false});
  var info = item.nowPlayingInfo;
  if (nulo(info)) return JSON.stringify({tem: false});
  var r = {tem: true};
  r.titulo = texto(info.valueForKey('kMRMediaRemoteNowPlayingInfoTitle'));
  r.artista = texto(info.valueForKey('kMRMediaRemoteNowPlayingInfoArtist'));
  r.album = texto(info.valueForKey('kMRMediaRemoteNowPlayingInfoAlbum'));
  r.duracao = numero(info.valueForKey('kMRMediaRemoteNowPlayingInfoDuration'));
  r.posicao = numero(info.valueForKey('kMRMediaRemoteNowPlayingInfoElapsedTime'));
  r.taxa = numero(info.valueForKey('kMRMediaRemoteNowPlayingInfoPlaybackRate'));
  var quando = info.valueForKey('kMRMediaRemoteNowPlayingInfoTimestamp');
  r.quando = nulo(quando) ? null : Number(quando.timeIntervalSince1970);
  r.tocando = null;
  try { var tocandoAgora = R.localIsPlaying; if (!nulo(tocandoAgora)) r.tocando = !!ObjC.unwrap(tocandoAgora); } catch (e) { r.tocando = null; }
  if (r.tocando === null) r.tocando = (r.taxa || 0) > 0;
  try {
    var cliente = R.localNowPlayingPlayerPath.client;
    r.app = texto(cliente.displayName);
    r.appId = texto(cliente.bundleIdentifier);
  } catch (e) { r.app = ''; r.appId = ''; }
  if (!r.titulo && !r.artista) return JSON.stringify({tem: false});
  r.chave = [r.titulo, r.artista, r.album, r.appId].join('|');
  if (argv.length > 1 && argv[0] !== r.chave) {
    var dados = null;
    try { dados = info.valueForKey('kMRMediaRemoteNowPlayingInfoArtworkData'); } catch (e) { dados = null; }
    if (nulo(dados)) { try { var arte = item.artwork; dados = nulo(arte) ? null : arte.imageData; } catch (e) { dados = null; } }
    try { r.capa = nulo(dados) ? false : (Number(dados.length) > 0 && dados.writeToFileAtomically(argv[1], true) == true); } catch (e) { r.capa = false; }
  }
  return JSON.stringify(r);
}
"""

JXA_TOCANDO_APPS = r"""
function ler(nome, id, divisor) {
  var a = Application(nome);
  if (!a.running()) return null;
  var estado = String(a.playerState());
  if (estado === 'stopped') return null;
  var t = a.currentTrack();
  var r = {tem: true, app: nome, appId: id, tocando: estado === 'playing'};
  r.titulo = String(t.name() || '');
  r.artista = String(t.artist() || '');
  r.album = String(t.album() || '');
  r.duracao = Number(t.duration()) / divisor;
  r.posicao = Number(a.playerPosition());
  if (nome === 'Spotify') { try { r.capaUrl = String(t.artworkUrl() || ''); } catch (e) { r.capaUrl = ''; } }
  r.chave = [r.titulo, r.artista, r.album, id].join('|');
  return r;
}
function run(argv) {
  var r = null;
  try { r = ler('Spotify', 'com.spotify.client', 1000); } catch (e) { r = null; }
  if (!r) { try { r = ler('Music', 'com.apple.Music', 1); } catch (e) { r = null; } }
  return JSON.stringify(r || {tem: false});
}
"""

JXA_CAPA_SPOTIFY = r"""
function run() {
  var a = Application('Spotify');
  if (a.running() === false) return '';
  try { return String(a.currentTrack().artworkUrl() || ''); } catch (e) { return ''; }
}
"""

SCRIPT_CAPA_MUSICA_MAC = """
on run argv
	set destino to item 1 of argv
	if application "Music" is not running then return "nao"
	tell application "Music"
		if (count of artworks of current track) is 0 then return "nao"
		set dados to raw data of artwork 1 of current track
	end tell
	set arquivo to open for access (POSIX file destino) with write permission
	try
		set eof arquivo to 0
		write dados to arquivo
		close access arquivo
	on error
		close access arquivo
		return "nao"
	end try
	return "ok"
end run
"""
JXA_CONTROLE_APP = r"""
function run(argv) {
  var a = Application(argv[0]);
  if (!a.running()) return 'parado';
  if (argv[1] === 'alternar') a.playpause();
  else if (argv[1] === 'proxima') a.nextTrack();
  else if (argv[1] === 'anterior') a.previousTrack();
  else if (argv[1] === 'posicao') a.playerPosition = parseFloat(argv[2]);
  return 'ok';
}
"""

JXA_FECHAR = r"""
function run(argv) {
  var r = [];
  for (var i = 0; i < argv.length; i++) {
    try {
      var a = Application(argv[i]);
      if (a.running()) { a.quit(); r.push(1); } else { r.push(0); }
    } catch (e) { r.push(-1); }
  }
  return JSON.stringify(r);
}
"""

SCRIPT_CHAMADA_MAC = """
set sep to (ASCII character 31)
set fim to (ASCII character 30)
set saida to ""
tell application "System Events"
	if not (exists process "NotificationCenter") then return ""
	tell process "NotificationCenter"
		repeat with w in windows
			try
				repeat with e in (entire contents of w)
					try
						set papel to role of e
						if papel is "AXButton" then
							set d to ""
							try
								set d to description of e
							end try
							if d is missing value then set d to ""
							set n to ""
							try
								set n to name of e
							end try
							if n is missing value then set n to ""
							set saida to saida & "B" & sep & (d as text) & sep & (n as text) & fim
						else if papel is "AXStaticText" then
							set v to value of e
							if v is not missing value then set saida to saida & "T" & sep & (v as text) & sep & fim
						end if
					end try
				end repeat
			end try
			set saida to saida & "W" & sep & sep & fim
		end repeat
	end tell
end tell
return saida
"""

SCRIPT_CLICAR_CHAMADA_MAC = """
on run argv
	set alvo to item 1 of argv
	tell application "System Events"
		tell process "NotificationCenter"
			repeat with w in windows
				repeat with e in (entire contents of w)
					try
						if role of e is "AXButton" then
							set d to ""
							try
								set d to description of e
							end try
							set n to ""
							try
								set n to name of e
							end try
							if d is alvo or n is alvo then
								perform action "AXPress" of e
								return "ok"
							end if
						end if
					end try
				end repeat
			end repeat
		end tell
	end tell
	return "nao"
end run
"""


def _rotulo_de(texto, opcoes):
    t = comparavel(texto)
    return any(t == o or t.startswith(o + " ") for o in opcoes)


def ler_chamada_mac(saida):
    sep, fim = "\x1f", "\x1e"
    janela = {"botoes": [], "textos": []}
    janelas = []
    for item in (saida or "").split(fim):
        partes = item.split(sep)
        if not partes or not partes[0]:
            continue
        if partes[0] == "W":
            janelas.append(janela)
            janela = {"botoes": [], "textos": []}
        elif partes[0] == "B" and len(partes) >= 3:
            rotulo = partes[1].strip() or partes[2].strip()
            if rotulo:
                janela["botoes"].append(rotulo)
        elif partes[0] == "T" and len(partes) >= 2 and partes[1].strip():
            janela["textos"].append(partes[1].strip())
    janelas.append(janela)
    for j in janelas:
        aceitar = next((b for b in j["botoes"] if _rotulo_de(b, ROTULOS_ACEITAR)), None)
        if not aceitar:
            continue
        recusar = next((b for b in j["botoes"] if _rotulo_de(b, ROTULOS_RECUSAR)), None)
        textos = [t for t in j["textos"] if len(t) < 120]
        return {"aceitar": aceitar, "recusar": recusar, "quem": textos[0] if textos else "",
                "detalhe": " · ".join(textos[1:3])}
    return None


JXA_ICONES = r"""
ObjC.import('AppKit');
function desenhar(img, lado) {
  var rep = $.NSBitmapImageRep.alloc.initWithBitmapDataPlanesPixelsWidePixelsHighBitsPerSampleSamplesPerPixelHasAlphaIsPlanarColorSpaceNameBytesPerRowBitsPerPixel(
    null, lado, lado, 8, 4, true, false, 'NSDeviceRGBColorSpace', 0, 0);
  rep.setSize($.NSMakeSize(lado, lado));
  $.NSGraphicsContext.saveGraphicsState;
  $.NSGraphicsContext.setCurrentContext($.NSGraphicsContext.graphicsContextWithBitmapImageRep(rep));
  img.drawInRectFromRectOperationFraction($.NSMakeRect(0, 0, lado, lado), $.NSMakeRect(0, 0, 0, 0), 2, 1);
  $.NSGraphicsContext.restoreGraphicsState;
  return rep.representationUsingTypeProperties(4, $.NSDictionary.dictionary);
}
function pelaTiff(img, lado) {
  var reps = $.NSBitmapImageRep.imageRepsWithData(img.TIFFRepresentation);
  var melhor = null;
  for (var k = 0; k < reps.count; k++) {
    var r = reps.objectAtIndex(k);
    if (!melhor || Math.abs(r.pixelsWide - lado) < Math.abs(melhor.pixelsWide - lado)) melhor = r;
  }
  return melhor ? melhor.representationUsingTypeProperties(4, $.NSDictionary.dictionary) : null;
}
function run(argv) {
  var saida = [];
  if (argv[0] === 'nomes') {
    var fm = $.NSFileManager.defaultManager;
    for (var i = 1; i < argv.length; i++) {
      var nome = '';
      try { nome = ObjC.unwrap(fm.displayNameAtPath(argv[i])) || ''; } catch (e) { nome = ''; }
      saida.push(nome);
    }
    return JSON.stringify(saida);
  }
  var lado = parseInt(argv[1], 10);
  var ws = $.NSWorkspace.sharedWorkspace;
  for (var j = 2; j + 1 < argv.length; j += 2) {
    var ok = false;
    try {
      var img = ws.iconForFile(argv[j]);
      var png = null;
      try { png = desenhar(img, lado); } catch (e1) { png = null; }
      if (!png || (png.isNil && png.isNil())) png = pelaTiff(img, lado);
      ok = !!(png && png.writeToFileAtomically(argv[j + 1], true));
    } catch (e2) { ok = false; }
    saida.push(ok ? 1 : 0);
  }
  return JSON.stringify(saida);
}
"""


def _ultima_lista_json(saida):
    for linha in reversed((saida or "").strip().splitlines()):
        linha = linha.strip()
        if linha.startswith("["):
            try:
                v = json.loads(linha)
            except ValueError:
                return []
            return v if isinstance(v, list) else []
    return []


def nomes_apps_mac(caminhos):
    if not caminhos:
        return {}
    try:
        codigo, saida, erro = rodar(["osascript", "-l", "JavaScript", "-e", JXA_ICONES, "nomes"] + list(caminhos),
                                    espera=40)
    except ErroAcao:
        return {}
    if codigo != 0:
        return {}
    nomes = {}
    for caminho, nome in zip(caminhos, _ultima_lista_json(saida)):
        if isinstance(nome, str) and nome.strip():
            nome = nome.strip()
            nomes[caminho] = nome[:-4] if nome.lower().endswith(".app") else nome
    return nomes


def icone_mac_pelo_icns(app, lado):
    try:
        with open(os.path.join(app, "Contents", "Info.plist"), "rb") as f:
            info = plistlib.load(f)
    except Exception:
        return None
    nome = info.get("CFBundleIconFile") if isinstance(info, dict) else None
    if not isinstance(nome, str) or not nome.strip():
        return None
    nome = nome.strip()
    if not nome.lower().endswith(".icns"):
        nome += ".icns"
    icns = os.path.join(app, "Contents", "Resources", nome)
    try:
        with open(icns, "rb") as f:
            dados = f.read()
    except OSError:
        return None
    png = png_do_icns(dados, lado)
    if png:
        return png
    if not shutil.which("sips"):
        return None
    fd, destino = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        codigo, _, _ = rodar(["sips", "-s", "format", "png", "-Z", str(lado), icns, "--out", destino], espera=20)
        with open(destino, "rb") as f:
            dados = f.read()
        return dados if codigo == 0 and tipo_imagem(dados) == ".png" else None
    except (OSError, ErroAcao):
        return None
    finally:
        try:
            os.remove(destino)
        except OSError:
            pass


def icones_mac(caminhos, lado):
    resultado = {}
    if not caminhos:
        return resultado
    pasta = tempfile.mkdtemp(prefix="deck-icones-")
    try:
        destinos = [os.path.join(pasta, "%d.png" % n) for n in range(len(caminhos))]
        args = ["osascript", "-l", "JavaScript", "-e", JXA_ICONES, "icones", str(lado)]
        for caminho, destino in zip(caminhos, destinos):
            args += [caminho, destino]
        try:
            codigo, saida, _ = rodar(args, espera=180)
        except ErroAcao:
            codigo, saida = 1, ""
        marcas = _ultima_lista_json(saida) if codigo == 0 else []
        for n, (caminho, destino) in enumerate(zip(caminhos, destinos)):
            dados = None
            if n < len(marcas) and marcas[n] == 1:
                try:
                    with open(destino, "rb") as f:
                        dados = f.read()
                except OSError:
                    dados = None
                if tipo_imagem(dados) != ".png":
                    dados = None
            if not dados or len(dados) < 1200:
                dados = icone_mac_pelo_icns(caminho, lado) or dados
            resultado[caminho] = dados
    finally:
        shutil.rmtree(pasta, ignore_errors=True)
    return resultado


def ler_volume_mac(saida):
    v = {}
    padrao = r"(output volume|input volume|alert volume|output muted):\s*(missing value|true|false|-?[\d.]+)"
    for m in re.finditer(padrao, saida or ""):
        k, val = m.groups()
        if val == "missing value":
            v[k] = None
        elif val in ("true", "false"):
            v[k] = val == "true"
        else:
            v[k] = int(round(float(val)))
    return v


def traduzir_erro_mac(texto):
    t = texto or ""
    tl = t.lower()
    if ("1002" in t or "-25211" in t or "sem-acessibilidade" in t or "not allowed to send keystrokes" in tl
            or "assistive access" in tl or "acesso assistivo" in tl):
        return (tr("O macOS bloqueou o controle do teclado. Ative o Terminal (ou o app onde o deck roda) em "
                "Ajustes do Sistema › Privacidade e Segurança › Acessibilidade. Se já estiver ativo, "
                "feche o Terminal e ligue o deck de novo."))
    if "-1743" in t or "not authorized to send apple events" in tl:
        return (tr("Falta permissão de Automação: Ajustes do Sistema › Privacidade e Segurança › Automação › "
                "Terminal → ative “System Events”."))
    if "sem-volume" in t:
        return tr("A saída de som atual não deixa o macOS controlar o volume (comum em HDMI e alguns monitores).")
    m = re.search(r"execution error: (.*?)(?:\s*\((-?\d+)\))?\s*$", t, re.S)
    if m:
        msg = re.sub(r"^(Error: )+", "", m.group(1).strip())
        return msg[:300] or "Falhou."
    return t.strip()[:300] or tr("Falhou sem mensagem.")


def osascript(script, js=False, espera=12.0, argumentos=()):
    args = ["osascript"] + (["-l", "JavaScript"] if js else []) + ["-e", script] + [str(x) for x in argumentos]
    codigo, saida, erro = rodar(args, espera, rotulo="osascript")
    if codigo is None:
        return None
    if codigo != 0:
        raise ErroAcao(traduzir_erro_mac(erro or saida))
    return saida


class Sistema:
    nome = ""

    def motivo(self, a):
        return None

    def atalho(self, nome):
        raise ErroAcao(tr("Botões do app Atalhos só funcionam no Mac."))

    def applescript(self, script, mostrar):
        raise ErroAcao(tr("AppleScript só funciona no Mac."))

    def energia(self, op):
        raise ErroAcao(tr("Este computador não sabe %s pelo deck.") % tr(NOMES_ENERGIA[op]).lower())

    def _primeiro_que_funciona(self, tentativas, falha):
        ultimo = ""
        for args in tentativas:
            if not shutil.which(args[0]) and not os.path.isabs(args[0]):
                continue
            try:
                codigo, saida, erro = rodar(args, espera=15)
            except ErroAcao as e:
                ultimo = str(e)
                continue
            if codigo in (0, None):
                return {"ok": True}
            ultimo = (erro or saida).strip()[-200:]
        raise ErroAcao(falha + (" (%s)" % ultimo if ultimo else ""))

    def _comando_resultado(self, codigo, saida, erro, mostrar):
        if codigo is None:
            return {"ok": True, "pendente": True, "mensagem": tr("Comando rodando no computador…")}
        if codigo:
            raise ErroAcao(tr("O comando terminou com erro (%d): %s") % (codigo, (erro or saida)[-200:] or tr("sem mensagem")))
        return {"ok": True, "mensagem": saida[-300:] if mostrar and saida else None}

    def catalogo(self):
        return []

    def alvo_icone(self, candidatos):
        return None

    def gerar_icones(self, alvos, lado):
        return {}

    def navegadores(self):
        return []

    def navegador_padrao(self):
        return None

    def abas_abertas(self):
        return []

    def focar_aba(self, url, navegador):
        return False

    def abrir_site(self, url, navegador):
        return self.link(url)

    def tocando(self, chave_capa, destino):
        return {"tem": False}

    def nao_perturbe(self, ligar):
        raise ErroAcao(tr("Este computador não deixa ligar o Não perturbe pelo deck."))

    def fechar_apps(self, nomes):
        raise ErroAcao(tr("Não sei fechar apps neste computador."))

    def processos(self):
        return set()

    def ativar_processo(self, nomes):
        return False

    def tem_reuniao_meet(self):
        return False

    def focar_reuniao_meet(self):
        return False

    def chamada_recebida(self):
        return None

    def responder_chamada(self, rotulo):
        raise ErroAcao(tr("Atender pelo deck só funciona no Mac. Use o botão do app da chamada."))

    def controlar_tocando(self, acao, valor, atual):
        if acao in MIDIA_DO_PLAYER:
            return self.midia(MIDIA_DO_PLAYER[acao])
        raise ErroAcao(tr("Este player não deixa pular para outro ponto."))

    def _navegador_escolhido(self, navegador):
        chave = chave_do_navegador(navegador)
        lista = self.navegadores()
        for n in lista:
            if chave and n["chave"] == chave:
                return n
        achado = melhor_nome(navegador, [(n["nome"], n) for n in lista])
        if achado:
            return achado[1]
        raise ErroAcao(tr("Não achei o navegador “%s” neste computador.") % navegador)


PASTAS_APPS_MAC = ["/Applications", "/Applications/Utilities", "/System/Applications",
                   "/System/Applications/Utilities", os.path.expanduser("~/Applications")]
APPS_ESCONDIDOS_MAC = {"/System/Library/CoreServices/Finder.app"}


class SistemaMac(Sistema):
    nome = "Mac"

    def __init__(self):
        self.mic_anterior = None
        self._sem_mediaremote = False
        self._miniaturas = {}
        self._navs = None
        self._navs_quando = 0.0
        self._fora = None
        self._fora_quando = 0.0
        self._avisou_automacao = False

    def teclas(self, combos, app, intervalo):
        r = osascript(script_teclas(combos, app, intervalo))
        return {"ok": True, "pendente": r is None}

    def texto(self, texto, app):
        r = osascript(script_texto(texto, app))
        return {"ok": True, "pendente": r is None}

    def apps_instalados(self):
        achados = []
        for pasta in PASTAS_APPS_MAC:
            try:
                nomes = os.listdir(pasta)
            except OSError:
                continue
            for n in nomes:
                caminho = os.path.join(pasta, n)
                if n.endswith(".app"):
                    achados.append((n[:-4], caminho))
                elif pasta == "/Applications" and not n.startswith(".") and os.path.isdir(caminho):
                    try:
                        for s in os.listdir(caminho):
                            if s.endswith(".app"):
                                achados.append((s[:-4], os.path.join(caminho, s)))
                    except OSError:
                        continue
        vistos = {c for _, c in achados}
        achados += [(n, c) for n, c in self.apps_fora_das_pastas() if c not in vistos]
        return achados

    def apps_fora_das_pastas(self):
        agora = time.time()
        if self._fora is not None and agora - self._fora_quando < 120:
            return self._fora
        achados = []
        casa = os.path.expanduser("~")
        if shutil.which("mdfind") and os.path.isdir(casa):
            try:
                codigo, saida, erro = rodar(["mdfind", "-onlyin", casa, "kMDItemContentType == 'com.apple.application-bundle'"], espera=8)
            except ErroAcao:
                codigo, saida = 1, ""
            for linha in (saida or "").splitlines() if codigo == 0 else []:
                c = linha.strip().rstrip("/")
                if not c.lower().endswith(".app") or not c.startswith(casa.rstrip("/") + "/"):
                    continue
                partes = c[len(casa.rstrip("/")) + 1:].split("/")
                if partes[0] == "Library" or any(x.startswith(".") or x == "node_modules" or x.lower().endswith(".app") for x in partes[:-1]):
                    continue
                if os.path.isdir(c):
                    achados.append((os.path.basename(c)[:-4], c))
        self._fora, self._fora_quando = achados, agora
        return achados

    def todos_os_apps(self):
        achados = self.apps_instalados()
        for caminho in sorted(APPS_ESCONDIDOS_MAC):
            if os.path.isdir(caminho):
                achados.append((os.path.basename(caminho)[:-4], caminho))
        return achados

    def caminho_app(self, nome):
        nome = nome.strip()
        if nome.startswith("/") and nome.rstrip("/").lower().endswith(".app") and os.path.isdir(nome):
            return nome.rstrip("/")
        apps = self.todos_os_apps()
        alvo = comparavel(nome[:-4] if nome.lower().endswith(".app") else nome)
        for n, caminho in apps:
            if comparavel(n) == alvo:
                return caminho
        achado = melhor_nome(nome, apps)
        return achado[1] if achado else None

    def alvo_icone(self, candidatos):
        for nome in candidatos:
            caminho = self.caminho_app(nome)
            if caminho:
                return caminho
        return None

    def catalogo(self):
        unicos = {}
        for nome, caminho in self.todos_os_apps():
            unicos.setdefault(nome.lower(), (nome, caminho))
        itens = list(unicos.values())
        nomes = nomes_apps_mac([c for _, c in itens])
        return [{"nome": nomes.get(c, n), "valor": n, "alvo": c} for n, c in itens]

    def gerar_icones(self, alvos, lado):
        return icones_mac(alvos, lado)

    def app(self, candidatos):
        for nome in candidatos:
            if nome.startswith("/") and os.path.exists(nome):
                codigo, saida, erro = rodar(["open", nome], espera=10)
                if not codigo:
                    return {"ok": True}
            codigo, saida, erro = rodar(["open", "-a", nome], espera=10)
            if not codigo:
                return {"ok": True}
            achado = melhor_nome(nome, self.todos_os_apps())
            if achado:
                codigo, saida, erro = rodar(["open", achado[1]], espera=10)
                if not codigo:
                    return {"ok": True}
        raise ErroAcao(tr("Não achei “%s” neste Mac (use o nome que aparece na pasta Aplicativos).") % candidatos[0])

    def link(self, url):
        codigo, saida, erro = rodar(["open", url], espera=10)
        if codigo:
            raise ErroAcao(erro or saida or tr("Não consegui abrir o link."))
        return {"ok": True}

    def navegadores(self):
        agora = time.time()
        if self._navs is not None and agora - self._navs_quando < 120:
            return self._navs
        instalados = {comparavel(n): c for n, c in self.todos_os_apps()}
        lista = []
        for nav in NAVEGADORES:
            caminho = instalados.get(comparavel(nav["mac"]))
            if caminho:
                lista.append({"chave": nav["chave"], "nome": nav["mac"], "caminho": caminho})
        self._navs, self._navs_quando = lista, agora
        return lista

    def navegador_padrao(self):
        arq = os.path.expanduser("~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist")
        try:
            with open(arq, "rb") as f:
                dados = plistlib.load(f)
        except Exception:
            return None
        for h in (dados.get("LSHandlers") or []) if isinstance(dados, dict) else []:
            if isinstance(h, dict) and h.get("LSHandlerURLScheme") in ("https", "http"):
                bundle = (h.get("LSHandlerRoleAll") or h.get("LSHandlerRoleViewer") or "").lower()
                for nav in NAVEGADORES:
                    if nav["bundle"] == bundle:
                        return nav["chave"]
        return None

    def _rodando(self):
        rodando = []
        for n in self.navegadores():
            nav = POR_CHAVE[n["chave"]]
            if nav["familia"] == "firefox":
                continue
            if _saida(["pgrep", "-x", nav["processo"]]):
                rodando.append(nav)
        return rodando

    def abas_abertas(self):
        rodando = self._rodando()
        if not rodando:
            return []
        try:
            saida = osascript(script_abas(rodando), espera=8)
        except ErroAcao as e:
            self._avisar_automacao(e)
            return []
        return ler_abas(saida or "")

    def _avisar_automacao(self, e):
        if "-1743" in str(e) or "Automação" in str(e):
            if not self._avisou_automacao:
                self._avisou_automacao = True
                log(amarelo(tr("⚠ Para ver as abas abertas e trazê-las para frente, permita que o Terminal controle o "
                            "Safari/Chrome: Ajustes do Sistema › Privacidade e Segurança › Automação.")))

    def focar_aba(self, url, navegador):
        rodando = self._rodando()
        if navegador:
            chave = chave_do_navegador(navegador)
            rodando = [n for n in rodando if n["chave"] == chave]
        if not rodando:
            return False
        padrao = self.navegador_padrao()
        rodando.sort(key=lambda n: 0 if n["chave"] == padrao else 1)
        try:
            abas = ler_abas(osascript(script_abas(rodando), espera=8) or "")
            aba = escolher_aba(abas, url)
            if not aba:
                return False
            osascript(script_focar(aba), espera=6)
            return True
        except ErroAcao as e:
            self._avisar_automacao(e)
            return False

    def abrir_site(self, url, navegador):
        if not navegador:
            return self.link(url)
        n = self._navegador_escolhido(navegador)
        codigo, saida, erro = rodar(["open", "-a", n["caminho"], url], espera=10)
        if codigo:
            raise ErroAcao(erro or saida or tr("Não consegui abrir o site no %s.") % n["nome"])
        return {"ok": True}

    def comando(self, comando, mostrar):
        shell = "/bin/zsh" if os.path.exists("/bin/zsh") else "/bin/sh"
        codigo, saida, erro = rodar([shell, "-lc", comando], espera=3, rotulo="comando")
        return self._comando_resultado(codigo, saida, erro, mostrar)

    def atalho(self, nome):
        codigo, saida, erro = rodar(["shortcuts", "run", nome], espera=3, rotulo=tr("atalho “%s”") % nome)
        if codigo is None:
            return {"ok": True, "pendente": True, "mensagem": tr("Atalho rodando no Mac…")}
        if codigo:
            texto = erro or saida
            if "find" in texto.lower() or "encontr" in texto.lower():
                raise ErroAcao(tr("Não achei o atalho “%s” no app Atalhos do Mac.") % nome)
            raise ErroAcao(tr("Atalho falhou: %s") % (texto[-200:] or tr("código %d") % codigo))
        return {"ok": True}

    def applescript(self, script, mostrar):
        saida = osascript(script)
        if saida is None:
            return {"ok": True, "pendente": True}
        return {"ok": True, "mensagem": saida[-300:] if mostrar and saida else None}

    def midia(self, op):
        r = osascript(JXA_MIDIA.replace("CODIGO", str(MAC_MIDIA[op])), js=True)
        return {"ok": True, "pendente": r is None}

    def tocando(self, chave_capa, destino):
        r = None
        if not self._sem_mediaremote:
            try:
                r = _json_objeto(osascript(JXA_TOCANDO, js=True, espera=6, argumentos=[chave_capa or "-", destino]))
            except ErroAcao:
                r = None
            if r is not None and r.get("erro") == "sem-mediaremote":
                self._sem_mediaremote = True
                r = None
        if r is None or not r.get("tem"):
            try:
                outro = _json_objeto(osascript(JXA_TOCANDO_APPS, js=True, espera=6))
            except ErroAcao:
                outro = None
            if outro and outro.get("tem"):
                self._capa_da_musica(outro, chave_capa, destino)
                return outro
        if r and r.get("tem") and not r.get("capa") and r.get("chave") != chave_capa:
            self._capa_extra(r, chave_capa, destino)
        return r or {"tem": False}

    def _capa_extra(self, r, chave_capa, destino):
        app = (r.get("appId") or "").lower()
        if app == "com.spotify.client":
            try:
                url = (osascript(JXA_CAPA_SPOTIFY, js=True, espera=6) or "").strip()
            except ErroAcao:
                url = ""
            if url.startswith(("http://", "https://")):
                r["capaUrl"] = url
        elif app == "com.apple.music":
            self._capa_da_musica(r, chave_capa, destino)
        else:
            self._capa_do_video(r)

    def _capa_da_musica(self, r, chave_capa, destino):
        if r.get("appId") != "com.apple.Music" or r.get("chave") == chave_capa or not destino:
            return
        try:
            saida = osascript(SCRIPT_CAPA_MUSICA_MAC, espera=6, argumentos=[destino])
        except ErroAcao:
            return
        if saida is not None and saida.strip() == "ok":
            r["capa"] = True

    def _capa_do_video(self, r):
        if not eh_navegador(r.get("appId"), r.get("app")):
            return
        chave = r.get("chave") or ""
        urls = self._miniaturas.get(chave)
        if not urls:
            aba = aba_do_video(self.abas_abertas(), r.get("titulo"))
            urls = miniaturas_youtube(aba["url"]) if aba else None
            if urls:
                self._miniaturas[chave] = urls
                while len(self._miniaturas) > 20:
                    self._miniaturas.pop(next(iter(self._miniaturas)))
        if urls:
            r["capaUrl"] = urls

    def nao_perturbe(self, ligar):
        if not shutil.which("shortcuts"):
            raise ErroAcao(tr("O Não perturbe pelo deck precisa do app Atalhos (macOS 12 ou mais novo)."))
        for nome in ATALHOS_FOCO_MAC[bool(ligar)]:
            codigo, saida, erro = rodar(["shortcuts", "run", nome], espera=10)
            if codigo in (0, None):
                return {"ok": True}
            texto = (erro or saida or "").lower()
            if "find" in texto or "encontr" in texto or "not found" in texto or "exist" in texto:
                continue
            raise ErroAcao(tr("O atalho “%s” falhou: %s") % (nome, (erro or saida or "")[-160:]))
        raise ErroAcao(tr("Para o Não perturbe, crie no app Atalhos os atalhos “Deck Foco Ligar” e “Deck Foco Desligar” "
                          "(ação Definir Foco). Veja Como usar › Modos."))

    def fechar_apps(self, nomes):
        if nomes:
            osascript(JXA_FECHAR, js=True, espera=12, argumentos=nomes)
        return {"ok": True}

    def processos(self):
        return {os.path.basename(x.strip()).lower() for x in _saida(["ps", "axo", "comm="]).splitlines() if x.strip()}

    def ativar_processo(self, nomes):
        rodando = self.processos()
        for nome in nomes:
            if nome.lower() in rodando:
                try:
                    osascript('tell application "System Events" to set frontmost of (first process whose name is %s) to true'
                              % as_texto(nome), espera=6)
                except ErroAcao:
                    continue
                time.sleep(0.3)
                return True
        return False

    def _aba_meet(self):
        for aba in self.abas_abertas():
            if REUNIAO_MEET.search(aba.get("url") or ""):
                return aba
        return None

    def tem_reuniao_meet(self):
        return self._aba_meet() is not None

    def focar_reuniao_meet(self):
        aba = self._aba_meet()
        if not aba:
            return False
        try:
            osascript(script_focar(aba), espera=6)
        except ErroAcao:
            return False
        time.sleep(0.3)
        return True

    def chamada_recebida(self):
        saida = osascript(SCRIPT_CHAMADA_MAC, espera=6)
        return ler_chamada_mac(saida)

    def responder_chamada(self, rotulo):
        saida = osascript(SCRIPT_CLICAR_CHAMADA_MAC, espera=6, argumentos=[rotulo])
        if saida is not None and saida.strip() != "ok":
            raise ErroAcao(tr("A chamada não está mais tocando."))
        return {"ok": True}

    def controlar_tocando(self, acao, valor, atual):
        atual = atual or {}
        ident = atual.get("appId") or ""
        app = "Spotify" if ident == "com.spotify.client" else "Music" if ident == "com.apple.Music" else None
        if app:
            saida = osascript(JXA_CONTROLE_APP, js=True, espera=6, argumentos=[app, acao, _num(valor or 0)])
            if saida is not None and saida.strip() == "parado":
                raise ErroAcao(tr("O %s foi fechado.") % app)
            return {"ok": True}
        return Sistema.controlar_tocando(self, acao, valor, atual)

    def volume(self, op):
        saida = osascript(script_volume(op))
        if saida is None:
            return {"ok": True, "pendente": True}
        if op == "mudo":
            mudo = saida.strip() == "true"
            return {"ok": True, "ativo": mudo, "info": tr("Mudo") if mudo else tr("Som")}
        return {"ok": True, "info": "%s%%" % saida.strip()}

    def energia(self, op):
        if op == "bloquear":
            return self._primeiro_que_funciona([
                ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
                ["osascript", "-e", 'tell application "System Events" to keystroke "q" using {control down, command down}'],
            ], tr("Não consegui bloquear a tela."))
        verbo = {"desligar": "shut down", "reiniciar": "restart", "suspender": "sleep"}[op]
        try:
            osascript('tell application "System Events" to %s' % verbo)
        except ErroAcao as e:
            if op != "suspender":
                raise
            return self._primeiro_que_funciona([["pmset", "sleepnow"]], tr("Não consegui suspender o Mac: %s") % e)
        return {"ok": True, "info": tr(NOMES_ENERGIA[op])}

    def microfone(self):
        v = ler_volume_mac(osascript("get volume settings") or "")
        atual = v.get("input volume")
        if atual is None:
            raise ErroAcao(tr("Este microfone não deixa o macOS mexer no volume. Use o mudo do próprio app de reunião."))
        if atual > 0:
            self.mic_anterior = atual
            osascript("set volume input volume 0")
            return {"ok": True, "ativo": True, "info": tr("Mudo")}
        osascript("set volume input volume %d" % (self.mic_anterior or 75))
        return {"ok": True, "ativo": False, "info": tr("Ligado")}

    def audio(self):
        saida = osascript("get volume settings", espera=3)
        if saida is None:
            return None
        v = ler_volume_mac(saida)
        entrada = v.get("input volume")
        return {
            "som_mudo": v.get("output muted"),
            "volume": v.get("output volume"),
            "mic_mudo": (entrada == 0) if entrada is not None else None,
            "tem_som": v.get("output volume") is not None,
            "tem_mic": entrada is not None,
        }


class TecladoWindows:
    def __init__(self):
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", ctypes.c_uint16), ("wScan", ctypes.c_uint16), ("dwFlags", ctypes.c_uint32),
                        ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_int32), ("dy", ctypes.c_int32), ("mouseData", ctypes.c_uint32),
                        ("dwFlags", ctypes.c_uint32), ("time", ctypes.c_uint32), ("dwExtraInfo", ctypes.c_size_t)]

        class HARDWAREINPUT(ctypes.Structure):
            _fields_ = [("uMsg", ctypes.c_uint32), ("wParamL", ctypes.c_uint16), ("wParamH", ctypes.c_uint16)]

        class UNIAO(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

        class INPUT(ctypes.Structure):
            _fields_ = [("type", ctypes.c_uint32), ("u", UNIAO)]

        self.INPUT = INPUT
        self.KEYBDINPUT = KEYBDINPUT
        self.user32 = self.carregar_user32()

    def carregar_user32(self):
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(self.INPUT), ctypes.c_int)
        u.SendInput.restype = ctypes.c_uint
        u.VkKeyScanW.argtypes = (ctypes.c_wchar,)
        u.VkKeyScanW.restype = ctypes.c_short
        u.MapVirtualKeyW.argtypes = (ctypes.c_uint, ctypes.c_uint)
        u.MapVirtualKeyW.restype = ctypes.c_uint
        return u

    def tecla(self, vk, solta=False):
        flags = 0x0002 if solta else 0
        if vk in WIN_ESTENDIDAS:
            flags |= 0x0001
        e = self.INPUT(type=1)
        e.u.ki = self.KEYBDINPUT(vk, self.user32.MapVirtualKeyW(vk, 0) & 0xFF, flags, 0, 0)
        return e

    def unidade(self, codigo, solta=False):
        e = self.INPUT(type=1)
        e.u.ki = self.KEYBDINPUT(0, codigo, 0x0004 | (0x0002 if solta else 0), 0, 0)
        return e

    def pressionar(self, vk, vezes=1):
        eventos = []
        for _ in range(vezes):
            eventos += [self.tecla(vk), self.tecla(vk, True)]
        return eventos

    def caracteres(self, texto):
        eventos = []
        for ch in texto.replace("\r\n", "\n"):
            if ch == "\n":
                eventos += self.pressionar(0x0D)
                continue
            if ch == "\t":
                eventos += self.pressionar(0x09)
                continue
            dados = ch.encode("utf-16-le")
            for i in range(0, len(dados), 2):
                codigo = int.from_bytes(dados[i:i + 2], "little")
                eventos += [self.unidade(codigo), self.unidade(codigo, True)]
        return eventos

    def combo(self, combo):
        mods, (tipo, valor) = combo
        vks = []
        for m in mods:
            if WIN_MODS[m] not in vks:
                vks.append(WIN_MODS[m])
        if tipo == "nome":
            alvo = WIN_VK[valor]
        else:
            r = self.user32.VkKeyScanW(valor)
            if r == -1:
                if vks:
                    raise ErroAcao(tr("A tecla “%s” não existe no layout de teclado atual.") % valor)
                return self.caracteres(valor)
            alvo = r & 0xFF
            estado = (r >> 8) & 0xFF
            for bit, vk in ((1, 0x10), (2, 0x11), (4, 0x12)):
                if estado & bit and vk not in vks:
                    vks.append(vk)
        return ([self.tecla(v) for v in vks] + [self.tecla(alvo), self.tecla(alvo, True)]
                + [self.tecla(v, True) for v in reversed(vks)])

    def enviar(self, eventos):
        for i in range(0, len(eventos), 64):
            bloco = eventos[i:i + 64]
            lista = (self.INPUT * len(bloco))(*bloco)
            enviados = self.user32.SendInput(len(bloco), lista, ctypes.sizeof(self.INPUT))
            if enviados != len(bloco):
                ultimo = getattr(ctypes, "get_last_error", lambda: 0)()
                raise ErroAcao(tr("O Windows não aceitou as teclas (erro %s). Se o app da frente roda como "
                               "administrador, rode o deck como administrador também.") % ultimo)
            if i + 64 < len(eventos):
                time.sleep(0.01)


def _ps_texto(s):
    return "'" + str(s).replace("'", "''") + "'"


def pastas_menu_iniciar():
    return [os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft", "Windows", "Start Menu",
                         "Programs")]


def app_paths_windows(nome):
    try:
        import winreg
    except ImportError:
        return None
    exe = nome if nome.lower().endswith(".exe") else nome + ".exe"
    for raiz in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(raiz, "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\" + exe) as k:
                valor, _ = winreg.QueryValueEx(k, "")
                if valor:
                    return os.path.expandvars(valor.strip('"'))
        except OSError:
            continue
    return None


class SistemaWindows(Sistema):
    nome = "Windows"

    def __init__(self):
        self._teclado = None
        self._apps = None
        self._lista_iniciar = []
        self._apps_quando = 0.0
        self._trava_apps = threading.Lock()
        self._navs = None
        self._navs_quando = 0.0
        self._trava_player = threading.Lock()
        self._proc_player = None
        self._player_falhou = 0.0

    def teclado(self):
        if self._teclado is None:
            self._teclado = TecladoWindows()
        return self._teclado

    def _ativar(self, app):
        script = "$w = New-Object -ComObject WScript.Shell; if ($w.AppActivate(%s)) { 'ok' }" % _ps_texto(app)
        rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], espera=6)
        time.sleep(0.25)

    def teclas(self, combos, app, intervalo):
        t = self.teclado()
        if app:
            self._ativar(app)
        for n, c in enumerate(combos):
            if n:
                time.sleep(intervalo)
            t.enviar(t.combo(c))
        return {"ok": True}

    def texto(self, texto, app):
        t = self.teclado()
        if app:
            self._ativar(app)
        t.enviar(t.caracteres(texto))
        return {"ok": True}

    def apps_iniciar(self, renovar=False):
        with self._trava_apps:
            if self._apps is not None and not renovar:
                return self._apps
            if renovar and time.time() - self._apps_quando < 60:
                return self._apps or []
            script = ("[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
                      "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress")
            try:
                codigo, saida, erro = rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                                            espera=25)
            except ErroAcao:
                codigo, saida = 1, ""
            apps = []
            lista = []
            if codigo == 0 and saida:
                try:
                    dados = json.loads(saida)
                except ValueError:
                    dados = []
                if isinstance(dados, dict):
                    dados = [dados]
                for d in dados:
                    if isinstance(d, dict) and d.get("AppID"):
                        apps.append((d.get("Name") or "", ("appid", d["AppID"])))
                        apps.append((d["AppID"].split("!")[0].split("\\")[-1], ("appid", d["AppID"])))
                        lista.append((str(d.get("Name") or "").strip(), d["AppID"]))
            self._apps = apps
            self._lista_iniciar = lista
            self._apps_quando = time.time()
            return apps

    def catalogo(self):
        self.apps_iniciar()
        unicos = {}
        for nome, appid in self._lista_iniciar:
            n = comparavel(nome)
            if not nome or "uninstall" in n or "desinstal" in n or re.match(r"^[a-z]+://", appid, re.I):
                continue
            unicos.setdefault(nome.lower(), {"nome": nome, "valor": nome, "alvo": "shell:AppsFolder\\" + appid})
        if not unicos:
            for nome, (tipo, caminho) in self.atalhos_menu():
                n = comparavel(nome)
                if "uninstall" in n or "desinstal" in n:
                    continue
                unicos.setdefault(nome.lower(), {"nome": nome, "valor": nome, "alvo": caminho})
        return list(unicos.values())

    def alvo_icone(self, candidatos):
        for nome in candidatos:
            alvo = self.resolver_app(nome)
            if not alvo:
                continue
            tipo, valor = alvo
            if tipo == "appid":
                return "shell:AppsFolder\\" + valor
            if tipo == "arquivo":
                return valor
        return None

    def gerar_icones(self, alvos, lado):
        resultado = {}
        if not alvos:
            return resultado
        pasta = tempfile.mkdtemp(prefix="deck-icones-")
        try:
            pedidos = [[alvo, os.path.join(pasta, "%d.png" % n)] for n, alvo in enumerate(alvos)]
            arquivo = os.path.join(pasta, "pedidos.json")
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump({"lado": lado, "itens": pedidos}, f)
            try:
                codigo, saida, _ = rodar([sys.executable, os.path.abspath(__file__), "--icones-windows", arquivo],
                                         espera=180)
            except ErroAcao:
                codigo, saida = 1, ""
            marcas = _ultima_lista_json(saida) if codigo == 0 else []
            for n, (alvo, destino) in enumerate(pedidos):
                dados = None
                if n < len(marcas) and marcas[n] == 1:
                    try:
                        with open(destino, "rb") as f:
                            dados = f.read()
                    except OSError:
                        dados = None
                if tipo_imagem(dados) != ".png" and os.path.isfile(alvo):
                    dados = self._icone_pelo_powershell(alvo, destino)
                resultado[alvo] = dados if tipo_imagem(dados) == ".png" else None
        finally:
            shutil.rmtree(pasta, ignore_errors=True)
        return resultado

    def _icone_pelo_powershell(self, alvo, destino):
        script = ("Add-Type -AssemblyName System.Drawing; "
                  "$i = [System.Drawing.Icon]::ExtractAssociatedIcon(%s); "
                  "if ($i) { $i.ToBitmap().Save(%s, [System.Drawing.Imaging.ImageFormat]::Png) }"
                  % (_ps_texto(alvo), _ps_texto(destino)))
        try:
            rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], espera=15)
            with open(destino, "rb") as f:
                return f.read()
        except (OSError, ErroAcao):
            return None

    def atalhos_menu(self):
        opcoes = []
        for pasta in pastas_menu_iniciar():
            for raiz, _, arquivos in os.walk(pasta):
                for arq in arquivos:
                    base, ext = os.path.splitext(arq)
                    if ext.lower() in (".lnk", ".url", ".appref-ms"):
                        opcoes.append((base, ("arquivo", os.path.join(raiz, arq))))
        return opcoes

    def resolver_app(self, nome, renovar=False):
        valor = os.path.expandvars(nome.strip())
        if re.match(r"^[a-zA-Z][\w+.-]+:", valor) and not re.match(r"^[a-zA-Z]:[\\/]", valor):
            return ("uri", valor)
        if os.path.exists(valor):
            return ("arquivo", valor)
        candidatos = []
        exe = shutil.which(valor) or app_paths_windows(valor)
        if exe:
            candidatos.append(((0, 0), ("arquivo", exe)))
        for fonte in (self.atalhos_menu(), self.apps_iniciar(renovar)):
            achado = melhor_nome(valor, fonte)
            if achado:
                candidatos.append(achado)
        if not candidatos:
            return None
        candidatos.sort(key=lambda c: c[0])
        return candidatos[0][1]

    def abrir(self, alvo):
        tipo, valor = alvo
        if tipo == "appid":
            lancar(["explorer.exe", "shell:AppsFolder\\" + valor])
            return
        try:
            os.startfile(valor)
        except OSError as e:
            raise ErroAcao(tr("O Windows não abriu “%s” (%s).") % (valor, e.strerror or e))

    def app(self, candidatos):
        for renovar in (False, True):
            for nome in candidatos:
                alvo = self.resolver_app(nome, renovar)
                if alvo:
                    self.abrir(alvo)
                    return {"ok": True}
        raise ErroAcao(tr("Não achei “%s” no Windows. Use o nome que aparece no menu Iniciar ou o caminho do .exe.")
                       % candidatos[0])

    def link(self, url):
        self.abrir(("uri", url))
        return {"ok": True}

    def navegadores(self):
        agora = time.time()
        if self._navs is not None and agora - self._navs_quando < 120:
            return self._navs
        lista = []
        try:
            import winreg
        except ImportError:
            winreg = None
        vistos = set()
        if winreg:
            for raiz in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(raiz, "Software\\Clients\\StartMenuInternet") as base:
                        n = 0
                        while True:
                            try:
                                sub = winreg.EnumKey(base, n)
                            except OSError:
                                break
                            n += 1
                            try:
                                with winreg.OpenKey(base, sub) as k:
                                    nome = winreg.QueryValueEx(k, "")[0]
                                with winreg.OpenKey(base, sub + "\\shell\\open\\command") as k:
                                    comando = winreg.QueryValueEx(k, "")[0]
                            except OSError:
                                continue
                            exe = os.path.expandvars(str(comando).strip().strip('"').split('"')[0])
                            if not exe or exe.lower() in vistos:
                                continue
                            vistos.add(exe.lower())
                            chave = None
                            base_exe = os.path.basename(exe).lower()
                            for nav in NAVEGADORES:
                                if base_exe in nav["exes"] and (nav["chave"] != "chromium" or "chromium" in exe.lower()):
                                    chave = nav["chave"]
                                    break
                            nome = str(nome).strip()
                            if chave and nome.lower().endswith(".exe"):
                                nome = POR_CHAVE[chave]["nome"]
                            lista.append({"chave": chave or simples(nome), "nome": nome, "caminho": exe})
                except OSError:
                    continue
        self._navs, self._navs_quando = lista, agora
        return lista

    def navegador_padrao(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice") as k:
                progid = str(winreg.QueryValueEx(k, "ProgId")[0]).lower()
        except (ImportError, OSError):
            return None
        for nav in NAVEGADORES:
            if any(progid.startswith(p) for p in nav["progid"]):
                return nav["chave"]
        return None

    def abrir_site(self, url, navegador):
        if not navegador:
            return self.link(url)
        n = self._navegador_escolhido(navegador)
        lancar([n["caminho"], url])
        return {"ok": True}

    def comando(self, comando, mostrar):
        codigo, saida, erro = rodar(comando, espera=3, rotulo="comando", shell=True)
        return self._comando_resultado(codigo, saida, erro, mostrar)

    def midia(self, op):
        t = self.teclado()
        t.enviar(t.pressionar(WIN_MIDIA[op]))
        return {"ok": True}

    def _player(self):
        with self._trava_player:
            if self._proc_player is not None and self._proc_player.vivo():
                return self._proc_player, False
            if time.time() - self._player_falhou < 60:
                raise ErroAcao(tr("O Windows não informou o que está tocando."))
            pasta = os.path.join(pasta_do_usuario("cache"), "capas")
            os.makedirs(pasta, exist_ok=True)
            script = os.path.join(pasta_do_usuario("cache"), "tocando.ps1")
            gravar_atomico(script, PS_TOCANDO.lstrip("\n"))
            try:
                self._proc_player = ProcessoPorLinhas(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                                       "-File", script, pasta])
            except OSError:
                self._player_falhou = time.time()
                raise ErroAcao(tr("O Windows não informou o que está tocando."))
            return self._proc_player, True

    def _pedir_player(self, partes):
        proc, novo = self._player()
        try:
            r = proc.pedir(partes, 15 if novo else 6)
        except ErroAcao:
            proc.fechar()
            self._proc_player = None
            if novo:
                self._player_falhou = time.time()
            raise ErroAcao(tr("O Windows não informou o que está tocando."))
        if r.get("erro") and r.get("erro") not in ("nada", "acao"):
            raise ErroAcao(tr("O Windows não informou o que está tocando."))
        return r

    def nao_perturbe(self, ligar):
        if not ligar:
            return {"ok": True}
        return {"ok": True, "mensagem": tr("No Windows, o Não perturbe não liga por programa: ligue em Win+N › Não perturbe.")}

    def fechar_apps(self, nomes):
        lista = ", ".join(_ps_texto(re.sub(r"\.exe$", "", n, flags=re.I)) for n in nomes)
        if lista:
            script = ("foreach ($n in @(%s)) { Get-Process -Name $n -ErrorAction SilentlyContinue | "
                      "ForEach-Object { [void]$_.CloseMainWindow() } }" % lista)
            rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], espera=12)
        return {"ok": True}

    def processos(self):
        nomes = set()
        for linha in _saida(["tasklist", "/fo", "csv", "/nh"]).splitlines():
            primeiro = linha.split('","')[0].strip().strip('"')
            if primeiro:
                nomes.add(re.sub(r"\.exe$", "", primeiro, flags=re.I).lower())
        return nomes

    def _ativar_ps(self, filtro):
        script = ("$w = New-Object -ComObject WScript.Shell; "
                  "$p = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 -and (%s) } | "
                  "Select-Object -First 1; if ($p -and $w.AppActivate($p.Id)) { 'ok' }" % filtro)
        codigo, saida, erro = rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], espera=8)
        if (saida or "").strip().endswith("ok"):
            time.sleep(0.3)
            return True
        return False

    def ativar_processo(self, nomes):
        if not nomes:
            return False
        filtro = " -or ".join("$_.ProcessName -eq %s" % _ps_texto(n) for n in nomes)
        return self._ativar_ps(filtro)

    def tem_reuniao_meet(self):
        script = ("Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match %s } | "
                  "Select-Object -First 1 | ForEach-Object { 'sim' }" % _ps_texto(REUNIAO_MEET_TITULO))
        codigo, saida, erro = rodar(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], espera=8)
        return "sim" in (saida or "")

    def focar_reuniao_meet(self):
        return self._ativar_ps("$_.MainWindowTitle -match %s" % _ps_texto(REUNIAO_MEET_TITULO))

    def tocando(self, chave_capa, destino):
        r = self._pedir_player(["estado", base64.b64encode((chave_capa or "").encode("utf-8")).decode("ascii")])
        if r.get("tem"):
            r["app"] = nome_do_player(r.get("app"))
            r["pode"] = {"proxima": r.pop("proxima", True), "anterior": r.pop("anterior", True), "posicao": r.pop("pular", False)}
            idade = r.get("idade")
            if not isinstance(idade, (int, float)) or not 0 <= idade < 86400:
                r["idade"] = 0
            if not isinstance(r.get("duracao"), (int, float)) or r["duracao"] <= 0:
                r["duracao"] = None
                r["posicao"] = None
        return r

    def controlar_tocando(self, acao, valor, atual):
        try:
            r = self._pedir_player([acao, _num(valor or 0)])
        except ErroAcao:
            return Sistema.controlar_tocando(self, acao, valor, atual)
        if r.get("erro") == "nada":
            raise ErroAcao(tr("Nada tocando no computador agora."))
        if not r.get("ok"):
            raise ErroAcao(tr("O app que está tocando não aceitou esse comando."))
        return {"ok": True}

    def _audio(self, op="estado", arg=""):
        codigo, saida, erro = rodar([sys.executable, os.path.abspath(__file__), "--audio-windows", op, str(arg)],
                                    espera=8)
        if codigo != 0 or not saida:
            raise ErroAcao(tr("Não consegui falar com o áudio do Windows. %s") % (erro or saida)[-160:])
        try:
            return json.loads(saida.splitlines()[-1])
        except ValueError:
            raise ErroAcao(tr("Resposta estranha do áudio do Windows."))

    def volume(self, op):
        t = self.teclado()
        if op in ("subir", "descer"):
            t.enviar(t.pressionar(0xAF if op == "subir" else 0xAE, 3))
            return {"ok": True}
        if op == "mudo":
            try:
                r = self._audio("som_mudo")
            except ErroAcao:
                t.enviar(t.pressionar(0xAD))
                return {"ok": True}
            mudo = bool(r.get("som_mudo"))
            return {"ok": True, "ativo": mudo, "info": tr("Mudo") if mudo else tr("Som")}
        r = self._audio("volume", op)
        if r.get("volume") is None:
            raise ErroAcao(tr("Este computador não tem saída de som ativa."))
        return {"ok": True, "info": "%s%%" % r["volume"]}

    def energia(self, op):
        if op == "bloquear":
            return self._primeiro_que_funciona([["rundll32.exe", "user32.dll,LockWorkStation"]], tr("Não consegui bloquear o Windows."))
        if op == "suspender":
            return self._primeiro_que_funciona([
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"],
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
            ], tr("Não consegui suspender o Windows."))
        return self._primeiro_que_funciona([["shutdown", "/r" if op == "reiniciar" else "/s", "/t", "3"]],
                                           tr("Não consegui %s o Windows.") % tr(NOMES_ENERGIA[op]).lower())

    def microfone(self):
        r = self._audio("mic")
        if r.get("mic_mudo") is None:
            raise ErroAcao(tr("Não achei um microfone padrão no Windows."))
        mudo = bool(r["mic_mudo"])
        return {"ok": True, "ativo": mudo, "info": tr("Mudo") if mudo else tr("Ligado")}

    def audio(self):
        try:
            r = self._audio()
        except ErroAcao:
            return None
        return {"som_mudo": r.get("som_mudo"), "volume": r.get("volume"), "mic_mudo": r.get("mic_mudo"),
                "tem_som": r.get("som_mudo") is not None, "tem_mic": r.get("mic_mudo") is not None}


PS_TOCANDO = r"""
param([string]$Pasta)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$metodos = [System.WindowsRuntimeSystemExtensions].GetMethods()
$asTask = $metodos | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
function Esperar($op, [Type]$tipo) {
  $tarefa = $asTask.MakeGenericMethod($tipo).Invoke($null, @($op))
  if (-not $tarefa.Wait(5000)) { throw 'tempo' }
  $tarefa.Result
}
$null = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime]
$null = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties, Windows.Media.Control, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStreamWithContentType, Windows.Storage.Streams, ContentType = WindowsRuntime]
$gerente = Esperar ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager])
function Sessao {
  $s = $gerente.GetCurrentSession()
  if ($null -eq $s) {
    $todas = @($gerente.GetSessions())
    if ($todas.Count -gt 0) { $s = $todas[0] }
  }
  $s
}
function Estado([string]$conhecida) {
  $s = Sessao
  if ($null -eq $s) { return @{ tem = $false } }
  $p = Esperar ($s.TryGetMediaPropertiesAsync()) ([Windows.Media.Control.GlobalSystemMediaTransportControlsSessionMediaProperties])
  $tl = $s.GetTimelineProperties()
  $pb = $s.GetPlaybackInfo()
  $r = @{
    tem = $true
    titulo = [string]$p.Title
    artista = [string]$p.Artist
    album = [string]$p.AlbumTitle
    app = [string]$s.SourceAppUserModelId
    tocando = ([string]$pb.PlaybackStatus -eq 'Playing')
    duracao = [double]($tl.EndTime - $tl.StartTime).TotalSeconds
    posicao = [double]$tl.Position.TotalSeconds
    idade = [double]([DateTimeOffset]::Now - $tl.LastUpdatedTime).TotalSeconds
    proxima = [bool]$pb.Controls.IsNextEnabled
    anterior = [bool]$pb.Controls.IsPreviousEnabled
    pular = [bool]$pb.Controls.IsPlaybackPositionEnabled
  }
  $r.chave = $r.titulo + '|' + $r.artista + '|' + $r.album + '|' + $r.app
  if ($r.chave -ne $conhecida -and $null -ne $p.Thumbnail) {
    try {
      $fluxo = Esperar ($p.Thumbnail.OpenReadAsync()) ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
      $leitor = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($fluxo)
      $memoria = New-Object System.IO.MemoryStream
      $leitor.CopyTo($memoria)
      $arquivo = Join-Path $Pasta 'capa-windows.img'
      [System.IO.File]::WriteAllBytes($arquivo, $memoria.ToArray())
      $leitor.Dispose()
      $memoria.Dispose()
      $r.capaArquivo = $arquivo
    } catch { $r.capaArquivo = '' }
  }
  $r
}
function Texto64([string]$b) {
  if (-not $b) { return '' }
  try { [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b)) } catch { '' }
}
function Ascii([string]$json) {
  [regex]::Replace($json, '[^\x00-\x7F]', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) '\u{0:x4}' -f [int][char]$m.Value })
}
function Comando([string]$acao, [string]$valor) {
  $s = Sessao
  if ($null -eq $s) { return @{ ok = $false; erro = 'nada' } }
  if ($acao -eq 'alternar') { $op = $s.TryTogglePlayPauseAsync() }
  elseif ($acao -eq 'proxima') { $op = $s.TrySkipNextAsync() }
  elseif ($acao -eq 'anterior') { $op = $s.TrySkipPreviousAsync() }
  elseif ($acao -eq 'posicao') { $op = $s.TryChangePlaybackPositionAsync([long]([double]::Parse($valor, [Globalization.CultureInfo]::InvariantCulture) * 10000000)) }
  else { return @{ ok = $false; erro = 'acao' } }
  @{ ok = [bool](Esperar $op ([bool])) }
}
while ($true) {
  $linha = [Console]::In.ReadLine()
  if ($null -eq $linha) { break }
  $partes = $linha.Split([char]9)
  $numero = $partes[0]
  $acao = if ($partes.Count -gt 1) { $partes[1] } else { '' }
  $valor = if ($partes.Count -gt 2) { $partes[2] } else { '' }
  try {
    if ($acao -eq 'estado') { $r = Estado (Texto64 $valor) } else { $r = Comando $acao $valor }
  } catch { $r = @{ erro = [string]$_.Exception.Message } }
  $r.n = $numero
  [Console]::Out.WriteLine((Ascii ($r | ConvertTo-Json -Compress)))
  [Console]::Out.Flush()
}
"""


class ProcessoPorLinhas:
    def __init__(self, args):
        self.p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  creationflags=SEM_JANELA)
        self.respostas = queue.Queue()
        self.numero = 0
        threading.Thread(target=self._ler, daemon=True).start()

    def _ler(self):
        for linha in self.p.stdout:
            self.respostas.put(linha)
        self.respostas.put(None)

    def vivo(self):
        return self.p.poll() is None

    def pedir(self, partes, espera):
        self.numero += 1
        n = str(self.numero)
        linha = "\t".join([n] + [str(x).replace("\t", " ").replace("\n", " ") for x in partes]) + "\n"
        self.p.stdin.write(linha.encode("utf-8"))
        self.p.stdin.flush()
        fim = time.time() + espera
        while True:
            resta = fim - time.time()
            if resta <= 0:
                raise ErroAcao("tempo")
            try:
                bruto = self.respostas.get(timeout=resta)
            except queue.Empty:
                raise ErroAcao("tempo")
            if bruto is None:
                raise ErroAcao("fim")
            try:
                r = json.loads(_dec(bruto))
            except ValueError:
                continue
            if isinstance(r, dict) and str(r.get("n")) == n:
                return r

    def fechar(self):
        try:
            self.p.kill()
        except OSError:
            pass


def audio_windows(op, arg):
    import uuid

    class GUID(ctypes.Structure):
        _fields_ = [("a", ctypes.c_uint32), ("b", ctypes.c_uint16), ("c", ctypes.c_uint16),
                    ("d", ctypes.c_ubyte * 8)]

    def guid(s):
        return GUID.from_buffer_copy(uuid.UUID(s).bytes_le)

    def metodo(obj, indice, *tipos):
        tabela = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
        prototipo = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, *tipos)
        funcao = prototipo(tabela[indice])
        return lambda *args: funcao(obj, *args)

    ole32 = ctypes.OleDLL("ole32")
    ole32.CoInitializeEx(None, 0)
    enumerador = ctypes.c_void_p()
    ole32.CoCreateInstance(ctypes.byref(guid("BCDE0395-E52F-467C-8E3D-C4579291692E")), None, 23,
                           ctypes.byref(guid("A95664D2-9614-4F35-A746-DE8DB63617E6")), ctypes.byref(enumerador))
    iid_volume = guid("5CDF2C82-841E-4546-9722-0CF74078229A")

    def ponto(fluxo):
        try:
            dispositivo = ctypes.c_void_p()
            metodo(enumerador, 4, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(
                fluxo, 0, ctypes.byref(dispositivo))
            volume = ctypes.c_void_p()
            metodo(dispositivo, 3, ctypes.POINTER(GUID), ctypes.c_uint32, ctypes.c_void_p,
                   ctypes.POINTER(ctypes.c_void_p))(ctypes.byref(iid_volume), 23, None, ctypes.byref(volume))
            return volume
        except OSError:
            return None

    def mudo(v):
        b = ctypes.c_int()
        metodo(v, 15, ctypes.POINTER(ctypes.c_int))(ctypes.byref(b))
        return bool(b.value)

    def definir_mudo(v, valor):
        metodo(v, 14, ctypes.c_int, ctypes.c_void_p)(1 if valor else 0, None)

    def nivel(v):
        f = ctypes.c_float()
        metodo(v, 9, ctypes.POINTER(ctypes.c_float))(ctypes.byref(f))
        return int(round(f.value * 100))

    def definir_nivel(v, valor):
        metodo(v, 7, ctypes.c_float, ctypes.c_void_p)(max(0, min(100, int(valor))) / 100.0, None)

    saida = ponto(0)
    entrada = ponto(1)
    if op == "som_mudo" and saida:
        definir_mudo(saida, not mudo(saida))
    elif op == "volume" and saida:
        definir_nivel(saida, arg)
        definir_mudo(saida, False)
    elif op == "mic" and entrada:
        definir_mudo(entrada, not mudo(entrada))
    return {"som_mudo": mudo(saida) if saida else None, "volume": nivel(saida) if saida else None,
            "mic_mudo": mudo(entrada) if entrada else None}


def icones_windows(arquivo):
    import uuid

    with open(arquivo, encoding="utf-8") as f:
        pedido = json.load(f)
    lado = int(pedido.get("lado") or 256)

    class GUID(ctypes.Structure):
        _fields_ = [("a", ctypes.c_uint32), ("b", ctypes.c_uint16), ("c", ctypes.c_uint16),
                    ("d", ctypes.c_ubyte * 8)]

    class TAMANHO(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_int32), ("cy", ctypes.c_int32)]

    class BITMAP(ctypes.Structure):
        _fields_ = [("bmType", ctypes.c_int32), ("bmWidth", ctypes.c_int32), ("bmHeight", ctypes.c_int32),
                    ("bmWidthBytes", ctypes.c_int32), ("bmPlanes", ctypes.c_uint16),
                    ("bmBitsPixel", ctypes.c_uint16), ("bmBits", ctypes.c_void_p)]

    class CABECALHO(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16),
                    ("biCompression", ctypes.c_uint32), ("biSizeImage", ctypes.c_uint32),
                    ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                    ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

    class INFO(ctypes.Structure):
        _fields_ = [("cabecalho", CABECALHO), ("cores", ctypes.c_uint32 * 4)]

    ole32 = ctypes.OleDLL("ole32")
    ole32.CoInitializeEx(None, 2)
    shell32 = ctypes.OleDLL("shell32")
    shell32.SHCreateItemFromParsingName.argtypes = (ctypes.c_wchar_p, ctypes.c_void_p, ctypes.POINTER(GUID),
                                                    ctypes.POINTER(ctypes.c_void_p))
    gdi32 = ctypes.WinDLL("gdi32")
    gdi32.GetObjectW.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p)
    gdi32.GetObjectW.restype = ctypes.c_int
    gdi32.GetDIBits.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p,
                                ctypes.c_void_p, ctypes.c_uint)
    gdi32.GetDIBits.restype = ctypes.c_int
    gdi32.DeleteObject.argtypes = (ctypes.c_void_p,)
    user32 = ctypes.WinDLL("user32")
    user32.GetDC.argtypes = (ctypes.c_void_p,)
    user32.GetDC.restype = ctypes.c_void_p
    user32.ReleaseDC.argtypes = (ctypes.c_void_p, ctypes.c_void_p)

    iid = GUID.from_buffer_copy(uuid.UUID("BCC18B79-BA16-442F-80C4-8A59C30C463B").bytes_le)
    pegar_imagem = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_void_p, TAMANHO, ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_void_p))
    soltar = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)

    def tabela(obj):
        return ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents

    marcas = []
    for alvo, destino in pedido.get("itens") or []:
        fabrica = ctypes.c_void_p()
        hbm = ctypes.c_void_p()
        ok = 0
        try:
            shell32.SHCreateItemFromParsingName(alvo, None, ctypes.byref(iid), ctypes.byref(fabrica))
            pegar_imagem(tabela(fabrica)[3])(fabrica, TAMANHO(lado, lado), 0x4, ctypes.byref(hbm))
            bm = BITMAP()
            gdi32.GetObjectW(hbm, ctypes.sizeof(BITMAP), ctypes.byref(bm))
            largura, altura = bm.bmWidth, abs(bm.bmHeight)
            if largura > 0 and altura > 0:
                info = INFO()
                info.cabecalho.biSize = ctypes.sizeof(CABECALHO)
                info.cabecalho.biWidth = largura
                info.cabecalho.biHeight = -altura
                info.cabecalho.biPlanes = 1
                info.cabecalho.biBitCount = 32
                memoria = ctypes.create_string_buffer(largura * altura * 4)
                dc = user32.GetDC(None)
                try:
                    linhas = gdi32.GetDIBits(dc, hbm, 0, altura, memoria, ctypes.byref(info), 0)
                finally:
                    user32.ReleaseDC(None, dc)
                if linhas == altura:
                    with open(destino, "wb") as f:
                        f.write(png_rgba(largura, altura, bgra_para_rgba(memoria.raw)))
                    ok = 1
        except (OSError, ValueError):
            ok = 0
        finally:
            if hbm.value:
                gdi32.DeleteObject(hbm)
            if fabrica.value:
                soltar(tabela(fabrica)[2])(fabrica)
        marcas.append(ok)
    return marcas


def pastas_desktop():
    dados = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    bases = [dados] + (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    bases += ["/var/lib/flatpak/exports/share", os.path.expanduser("~/.local/share/flatpak/exports/share"),
              "/var/lib/snapd/desktop"]
    pastas = []
    for b in bases:
        p = os.path.join(b, "applications")
        if b and p not in pastas and os.path.isdir(p):
            pastas.append(p)
    return pastas


def ler_desktop(caminho):
    dados = {}
    secao = None
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                if linha.startswith("["):
                    secao = linha
                    continue
                if secao == "[Desktop Entry]" and "=" in linha:
                    k, v = linha.split("=", 1)
                    dados.setdefault(k.strip(), v.strip())
    except OSError:
        return {}
    return dados


def nome_local_desktop(d):
    idioma = ""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(var):
            idioma = os.environ[var].split(".")[0].split("@")[0]
            break
    if idioma and idioma not in ("C", "POSIX"):
        for chave in ("Name[%s]" % idioma, "Name[%s]" % idioma.split("_")[0]):
            if d.get(chave):
                return d[chave]
    return d.get("Name", "")


def bases_icones_linux():
    dados = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    bases = [os.path.expanduser("~/.icons"), os.path.join(dados, "icons")]
    for d in (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":"):
        if d:
            bases.append(os.path.join(d, "icons"))
    bases += ["/var/lib/flatpak/exports/share/icons", os.path.expanduser("~/.local/share/flatpak/exports/share/icons")]
    return [b for b in dict.fromkeys(bases) if os.path.isdir(b)]


def tema_icones_linux():
    t = _saida(["gsettings", "get", "org.gnome.desktop.interface", "icon-theme"]).strip().strip("'\"")
    if t:
        return t
    kde = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"), "kdeglobals")
    try:
        secao = None
        with open(kde, encoding="utf-8", errors="replace") as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith("["):
                    secao = linha
                elif secao == "[Icons]" and linha.startswith("Theme="):
                    return linha.split("=", 1)[1].strip()
    except OSError:
        pass
    return None


def temas_linux(bases):
    ordem = []
    fila = [t for t in (tema_icones_linux(),) if t]
    while fila and len(ordem) < 8:
        tema = fila.pop(0)
        if tema in ordem:
            continue
        ordem.append(tema)
        for b in bases:
            indice = ler_desktop_secao(os.path.join(b, tema, "index.theme"), "[Icon Theme]")
            if indice.get("Inherits"):
                fila += [x.strip() for x in indice["Inherits"].split(",") if x.strip()]
                break
    for extra in ("hicolor", "Adwaita", "breeze", "Papirus", "Yaru"):
        if extra not in ordem:
            ordem.append(extra)
    return ordem


def ler_desktop_secao(caminho, secao_alvo):
    dados = {}
    secao = None
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith("["):
                    secao = linha
                elif secao == secao_alvo and "=" in linha and not linha.startswith("#"):
                    k, v = linha.split("=", 1)
                    dados.setdefault(k.strip(), v.strip())
    except OSError:
        return {}
    return dados


def _medida_pasta(nome):
    if nome == "scalable":
        return 1000
    m = re.fullmatch(r"(\d+)x\d+(?:@(\d+)x?)?", nome)
    if not m:
        return None
    return int(m.group(1)) * int(m.group(2) or 1)


def _listar(pasta):
    try:
        return os.listdir(pasta)
    except OSError:
        return []


def achar_icone_linux(nome, bases=None, temas=None):
    if not nome:
        return None
    if os.path.isabs(nome):
        return nome if os.path.isfile(nome) and nome.lower().endswith((".png", ".svg")) else None
    base_nome = nome[:-4] if nome.lower().endswith((".png", ".svg", ".xpm")) else nome
    bases = bases if bases is not None else bases_icones_linux()
    temas = temas if temas is not None else temas_linux(bases)
    for tema in temas:
        melhor = None
        for b in bases:
            raiz = os.path.join(b, tema)
            for sub in _listar(raiz):
                medida = _medida_pasta(sub)
                pastas = []
                if medida:
                    pastas.append((medida, os.path.join(raiz, sub, "apps")))
                    pastas.append((medida, os.path.join(raiz, sub, "applications")))
                elif sub in ("apps", "applications"):
                    for tam in _listar(os.path.join(raiz, sub)):
                        m = re.fullmatch(r"\d+", tam)
                        medida2 = 1000 if tam == "scalable" else (int(tam) if m else None)
                        if medida2:
                            pastas.append((medida2, os.path.join(raiz, sub, tam)))
                for medida_p, pasta in pastas:
                    for ext in (".svg", ".png"):
                        caminho = os.path.join(pasta, base_nome + ext)
                        if os.path.isfile(caminho):
                            nota = 1000 if ext == ".svg" else min(medida_p, 512)
                            if melhor is None or nota > melhor[0]:
                                melhor = (nota, caminho)
        if melhor:
            return melhor[1]
    for pasta in ("/usr/share/pixmaps", "/usr/local/share/pixmaps"):
        for ext in (".svg", ".png"):
            caminho = os.path.join(pasta, base_nome + ext)
            if os.path.isfile(caminho):
                return caminho
    return None


MSG_SEM_TECLADO = ("Para teclas e texto no Linux, instale o xdotool (sudo apt install xdotool). "
                   "Em sessão Wayland, instale o wtype.")
MSG_SEM_AUDIO = "Para volume e microfone no Linux, é preciso o pactl (PulseAudio/PipeWire) ou o wpctl."
MSG_SEM_MIDIA = "Para mídia no Linux, instale o playerctl (sudo apt install playerctl)."


class SistemaLinux(Sistema):
    nome = "Linux"

    def __init__(self):
        self._apps = None
        self._entradas = {}
        self._apps_quando = 0.0
        self._navs = None
        self._navs_quando = 0.0

    def ferramenta_teclado(self):
        wayland = bool(os.environ.get("WAYLAND_DISPLAY")) or os.environ.get("XDG_SESSION_TYPE") == "wayland"
        if wayland and shutil.which("wtype"):
            return "wtype"
        if shutil.which("xdotool") and os.environ.get("DISPLAY"):
            return "xdotool"
        return None

    def ferramenta_audio(self):
        if shutil.which("pactl"):
            return "pactl"
        if shutil.which("wpctl"):
            return "wpctl"
        return None

    def motivo(self, a):
        t = a["tipo"]
        if t in ("teclas", "texto") and not self.ferramenta_teclado():
            return tr(MSG_SEM_TECLADO)
        if t in ("volume", "microfone") and not self.ferramenta_audio():
            return tr(MSG_SEM_AUDIO)
        if t == "midia" and not shutil.which("playerctl") and not self.ferramenta_teclado():
            return tr(MSG_SEM_MIDIA)
        return None

    def _ok(self, args, espera=8):
        codigo, saida, erro = rodar(args, espera=espera)
        if codigo:
            raise ErroAcao(tr("%s falhou: %s") % (args[0], (erro or saida)[-200:] or tr("código %d") % codigo))
        return saida

    def xdo(self, combo):
        mods, (tipo, valor) = combo
        partes = []
        for m in mods:
            if LINUX_MODS[m] not in partes:
                partes.append(LINUX_MODS[m])
        partes.append(LINUX_TECLAS[valor] if tipo == "nome" else LINUX_SIMBOLOS.get(valor, valor))
        return "+".join(partes)

    def wtype(self, combo):
        mods, (tipo, valor) = combo
        nomes = []
        for m in mods:
            if WTYPE_MODS[m] not in nomes:
                nomes.append(WTYPE_MODS[m])
        args = ["wtype"]
        for m in nomes:
            args += ["-M", m]
        args += ["-k", LINUX_TECLAS[valor] if tipo == "nome" else LINUX_SIMBOLOS.get(valor, valor)]
        for m in reversed(nomes):
            args += ["-m", m]
        return args

    def _ativar(self, app, ferramenta):
        if ferramenta == "xdotool":
            rodar(["xdotool", "search", "--onlyvisible", "--class", app, "windowactivate", "--sync"], espera=4)
            time.sleep(0.2)

    def teclas(self, combos, app, intervalo):
        f = self.ferramenta_teclado()
        if not f:
            raise ErroAcao(tr(MSG_SEM_TECLADO))
        if app:
            self._ativar(app, f)
        if f == "xdotool":
            self._ok(["xdotool", "key", "--clearmodifiers", "--delay", str(int(intervalo * 1000))]
                     + [self.xdo(c) for c in combos])
        else:
            for n, c in enumerate(combos):
                if n:
                    time.sleep(intervalo)
                self._ok(self.wtype(c))
        return {"ok": True}

    def texto(self, texto, app):
        f = self.ferramenta_teclado()
        if not f:
            raise ErroAcao(tr(MSG_SEM_TECLADO))
        if app:
            self._ativar(app, f)
        if f == "xdotool":
            self._ok(["xdotool", "type", "--clearmodifiers", "--delay", "6", "--", texto], espera=30)
        else:
            self._ok(["wtype", texto], espera=30)
        return {"ok": True}

    def apps_instalados(self):
        if self._apps is not None and time.time() - self._apps_quando < 60:
            return self._apps
        vistos = {}
        for pasta in pastas_desktop():
            for raiz, _, arquivos in os.walk(pasta):
                for arq in sorted(arquivos):
                    if not arq.endswith(".desktop"):
                        continue
                    caminho = os.path.join(raiz, arq)
                    ident = os.path.relpath(caminho, pasta).replace(os.sep, "-")
                    if ident in vistos:
                        continue
                    d = ler_desktop(caminho)
                    if d.get("Type", "Application") != "Application" or d.get("Hidden") == "true":
                        continue
                    vistos[ident] = (caminho, d)
        opcoes = []
        for ident, (caminho, d) in vistos.items():
            valor = (ident, caminho, d.get("Exec", ""))
            nomes = {d.get("Name", ""), ident[:-len(".desktop")]}
            for k, v in d.items():
                if k.startswith("Name["):
                    nomes.add(v)
            partes = d.get("Exec", "").split()
            if partes:
                nomes.add(os.path.basename(partes[0]))
            for n in nomes:
                if n:
                    opcoes.append((n, valor))
        self._apps = opcoes
        self._entradas = vistos
        self._apps_quando = time.time()
        return opcoes

    def catalogo(self):
        self.apps_instalados()
        bases = bases_icones_linux()
        temas = temas_linux(bases)
        unicos = {}
        for ident, (caminho, d) in sorted(self._entradas.items()):
            if d.get("NoDisplay") == "true" or not d.get("Exec"):
                continue
            nome = nome_local_desktop(d).strip()
            if not nome:
                continue
            unicos.setdefault(nome.lower(), {"nome": nome, "valor": nome,
                                             "alvo": achar_icone_linux(d.get("Icon", ""), bases, temas)})
        return list(unicos.values())

    def alvo_icone(self, candidatos):
        for nome in candidatos:
            achado = melhor_nome(nome, self.apps_instalados())
            if achado:
                d = ler_desktop(achado[1][1])
                return achar_icone_linux(d.get("Icon", ""))
            if shutil.which(nome):
                return None
        return None

    def gerar_icones(self, alvos, lado):
        resultado = {}
        for alvo in alvos:
            try:
                with open(alvo, "rb") as f:
                    dados = f.read(2 * 1024 * 1024)
            except OSError:
                dados = None
            resultado[alvo] = dados if tipo_imagem(dados) in (".png", ".svg") else None
        return resultado

    def abrir_desktop(self, ident, caminho, linha_exec):
        if shutil.which("gtk-launch"):
            codigo, saida, erro = rodar(["gtk-launch", ident], espera=8)
            if not codigo:
                return
        if shutil.which("gio"):
            codigo, saida, erro = rodar(["gio", "launch", caminho], espera=8)
            if not codigo:
                return
        try:
            partes = [p for p in shlex.split(linha_exec) if not re.fullmatch(r"%[a-zA-Z]", p)]
        except ValueError:
            partes = []
        if not partes:
            raise ErroAcao(tr("O atalho %s não diz como abrir o app.") % os.path.basename(caminho))
        lancar(partes)

    def app(self, candidatos):
        for nome in candidatos:
            achado = melhor_nome(nome, self.apps_instalados())
            if achado:
                self.abrir_desktop(*achado[1])
                return {"ok": True}
            caminho = shutil.which(nome)
            if caminho:
                lancar([caminho])
                return {"ok": True}
        raise ErroAcao(tr("Não achei “%s” neste Linux (use o nome do menu de aplicativos ou o comando).")
                       % candidatos[0])

    def link(self, url):
        self._ok(["xdg-open", url])
        return {"ok": True}

    def navegadores(self):
        agora = time.time()
        if self._navs is not None and agora - self._navs_quando < 120:
            return self._navs
        self.apps_instalados()
        lista = []
        for ident, (caminho, d) in sorted(self._entradas.items()):
            categorias = d.get("Categories", "")
            mimes = d.get("MimeType", "")
            if "WebBrowser" not in categorias and "x-scheme-handler/https" not in mimes:
                continue
            if d.get("NoDisplay") == "true":
                continue
            base = ident[:-len(".desktop")].lower()
            chave = None
            for nav in NAVEGADORES:
                if base in nav["linux"] or any(base.endswith("-" + x) or base.endswith("." + x) for x in nav["linux"]):
                    chave = nav["chave"]
                    break
            lista.append({"chave": chave or base, "nome": nome_local_desktop(d) or ident, "caminho": caminho, "ident": ident,
                          "exec": d.get("Exec", "")})
        self._navs, self._navs_quando = lista, agora
        return lista

    def navegador_padrao(self):
        ident = _saida(["xdg-settings", "get", "default-web-browser"]).strip()
        if not ident:
            return None
        for n in self.navegadores():
            if n.get("ident") == ident:
                return n["chave"]
        return None

    def abrir_site(self, url, navegador):
        if not navegador:
            return self.link(url)
        n = self._navegador_escolhido(navegador)
        if shutil.which("gtk-launch"):
            codigo, saida, erro = rodar(["gtk-launch", n["ident"], url], espera=8)
            if not codigo:
                return {"ok": True}
        try:
            partes = shlex.split(n.get("exec", ""))
        except ValueError:
            partes = []
        if not partes:
            raise ErroAcao(tr("O atalho do %s não diz como abrir sites.") % n["nome"])
        trocado = False
        args = []
        for p in partes:
            if re.fullmatch(r"%[uUfF]", p):
                args.append(url)
                trocado = True
            elif not re.fullmatch(r"%[a-zA-Z]", p):
                args.append(p)
        if not trocado:
            args.append(url)
        lancar(args)
        return {"ok": True}

    def comando(self, comando, mostrar):
        args = ["/bin/bash", "-lc", comando] if os.path.exists("/bin/bash") else ["/bin/sh", "-c", comando]
        codigo, saida, erro = rodar(args, espera=3, rotulo="comando")
        return self._comando_resultado(codigo, saida, erro, mostrar)

    def midia(self, op):
        comando, tecla = LINUX_MIDIA[op]
        if shutil.which("playerctl"):
            codigo, saida, erro = rodar(["playerctl", comando], espera=5)
            if not codigo:
                return {"ok": True}
        f = self.ferramenta_teclado()
        if f == "xdotool":
            self._ok(["xdotool", "key", tecla])
            return {"ok": True}
        if f == "wtype":
            self._ok(["wtype", "-k", tecla])
            return {"ok": True}
        if shutil.which("playerctl"):
            raise ErroAcao(tr("Nenhum player de mídia respondeu."))
        raise ErroAcao(tr(MSG_SEM_MIDIA))

    def nao_perturbe(self, ligar):
        if shutil.which("gsettings"):
            codigo, saida, erro = rodar(["gsettings", "set", "org.gnome.desktop.notifications", "show-banners",
                                         "false" if ligar else "true"], espera=6)
            if not codigo:
                return {"ok": True}
        raise ErroAcao(tr("Não consegui mudar o Não perturbe neste Linux (funciona no GNOME)."))

    def fechar_apps(self, nomes):
        for nome in nomes:
            rodar(["pkill", "-x", "-i", nome], espera=5)
        return {"ok": True}

    def processos(self):
        return {x.strip().lower() for x in _saida(["ps", "axo", "comm="]).splitlines() if x.strip()}

    def ativar_processo(self, nomes):
        if not shutil.which("xdotool"):
            return False
        for nome in nomes:
            codigo, saida, erro = rodar(["xdotool", "search", "--onlyvisible", "--class", nome, "windowactivate", "--sync"], espera=5)
            if codigo == 0:
                time.sleep(0.2)
                return True
        return False

    def tem_reuniao_meet(self):
        if not shutil.which("xdotool"):
            return False
        codigo, saida, erro = rodar(["xdotool", "search", "--onlyvisible", "--name", REUNIAO_MEET_TITULO], espera=5)
        return codigo == 0 and bool((saida or "").strip())

    def focar_reuniao_meet(self):
        if not shutil.which("xdotool"):
            return False
        codigo, saida, erro = rodar(["xdotool", "search", "--onlyvisible", "--name", REUNIAO_MEET_TITULO,
                                     "windowactivate", "--sync"], espera=5)
        if codigo == 0:
            time.sleep(0.2)
            return True
        return False

    def _players(self):
        if not shutil.which("playerctl"):
            raise ErroAcao(tr(MSG_SEM_MIDIA))
        codigo, saida, erro = rodar(["playerctl", "-a", "metadata", "--format", FORMATO_PLAYERCTL], espera=4)
        lista = []
        for linha in (saida or "").splitlines():
            partes = linha.split("\x1f")
            if len(partes) < 8 or partes[1] not in ("Playing", "Paused"):
                continue
            lista.append(partes)
        lista.sort(key=lambda x: 0 if x[1] == "Playing" else 1)
        return lista

    def tocando(self, chave_capa, destino):
        lista = self._players()
        if not lista:
            return {"tem": False}
        nome, estado, titulo, artista, album, duracao, posicao, capa = lista[0][:8]
        pagina = lista[0][8] if len(lista[0]) > 8 else ""
        r = {"tem": True, "player": nome, "app": nome_do_player(nome), "tocando": estado == "Playing",
             "titulo": titulo, "artista": artista, "album": album,
             "duracao": _int(duracao, 0) / 1e6 or None, "posicao": _int(posicao, 0) / 1e6,
             "pode": {"proxima": True, "anterior": True, "posicao": _int(duracao, 0) > 0}}
        r["chave"] = "|".join([titulo, artista, album, nome])
        if capa.startswith("file://"):
            r["capaArquivo"] = unquote(urlparse(capa).path)
        elif capa.startswith(("http://", "https://")):
            r["capaUrl"] = capa
        elif miniaturas_youtube(pagina):
            r["capaUrl"] = miniaturas_youtube(pagina)
        return r

    def controlar_tocando(self, acao, valor, atual):
        nome = (atual or {}).get("player")
        alvo = ["-p", nome] if nome else []
        if acao == "posicao":
            args = ["playerctl"] + alvo + ["position", _num(valor or 0)]
        elif acao in MIDIA_DO_PLAYER:
            args = ["playerctl"] + alvo + [LINUX_MIDIA[MIDIA_DO_PLAYER[acao]][0]]
        else:
            raise ErroAcao(tr("Ação desconhecida."))
        if not shutil.which("playerctl"):
            raise ErroAcao(tr(MSG_SEM_MIDIA))
        codigo, saida, erro = rodar(args, espera=5)
        if codigo:
            raise ErroAcao(tr("O app que está tocando não aceitou esse comando."))
        return {"ok": True}

    def _c(self):
        return dict(os.environ, LC_ALL="C")

    def _ler(self, ferramenta, qual):
        if ferramenta == "pactl":
            alvo = "@DEFAULT_SINK@" if qual == "saida" else "@DEFAULT_SOURCE@"
            tipo = "sink" if qual == "saida" else "source"
            mudo = _saida(["pactl", "get-%s-mute" % tipo, alvo], self._c())
            vol = _saida(["pactl", "get-%s-volume" % tipo, alvo], self._c())
            m = re.search(r"(\d+)%", vol)
            return ({"yes": True, "no": False}.get(mudo.split(":")[-1].strip()) if mudo else None,
                    int(m.group(1)) if m else None)
        alvo = "@DEFAULT_AUDIO_SINK@" if qual == "saida" else "@DEFAULT_AUDIO_SOURCE@"
        texto = _saida(["wpctl", "get-volume", alvo])
        m = re.search(r"Volume:\s*([\d.]+)", texto)
        if not m:
            return (None, None)
        return ("[MUTED]" in texto, int(round(float(m.group(1)) * 100)))

    def _mudar(self, ferramenta, qual, valor):
        if ferramenta == "pactl":
            tipo = "sink" if qual == "saida" else "source"
            alvo = "@DEFAULT_SINK@" if qual == "saida" else "@DEFAULT_SOURCE@"
            self._ok(["pactl", "set-%s-mute" % tipo, alvo, valor])
        else:
            alvo = "@DEFAULT_AUDIO_SINK@" if qual == "saida" else "@DEFAULT_AUDIO_SOURCE@"
            self._ok(["wpctl", "set-mute", alvo, valor])

    def volume(self, op):
        f = self.ferramenta_audio()
        if not f:
            raise ErroAcao(tr(MSG_SEM_AUDIO))
        if op == "mudo":
            self._mudar(f, "saida", "toggle")
            mudo, _ = self._ler(f, "saida")
            return {"ok": True, "ativo": bool(mudo), "info": tr("Mudo") if mudo else tr("Som")}
        _, atual = self._ler(f, "saida")
        if op in ("subir", "descer"):
            if atual is None:
                raise ErroAcao(tr("Não consegui ler o volume atual."))
            alvo = max(0, min(100, atual + (6 if op == "subir" else -6)))
        else:
            alvo = max(0, min(100, int(op)))
        if f == "pactl":
            self._ok(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "%d%%" % alvo])
        else:
            self._ok(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", _num(alvo / 100.0)])
        if op != "descer":
            self._mudar(f, "saida", "0")
        return {"ok": True, "info": "%d%%" % alvo}

    def energia(self, op):
        if op == "bloquear":
            return self._primeiro_que_funciona([
                ["loginctl", "lock-session"], ["xdg-screensaver", "lock"],
                ["dbus-send", "--session", "--dest=org.freedesktop.ScreenSaver", "/ScreenSaver", "org.freedesktop.ScreenSaver.Lock"],
            ], tr("Não consegui bloquear a tela."))
        alvo = {"desligar": "poweroff", "reiniciar": "reboot", "suspender": "suspend"}[op]
        return self._primeiro_que_funciona([["systemctl", alvo], ["loginctl", alvo]],
                                           tr("Não consegui %s o computador.") % tr(NOMES_ENERGIA[op]).lower())

    def microfone(self):
        f = self.ferramenta_audio()
        if not f:
            raise ErroAcao(tr(MSG_SEM_AUDIO))
        self._mudar(f, "entrada", "toggle")
        mudo, _ = self._ler(f, "entrada")
        if mudo is None:
            raise ErroAcao(tr("Não achei um microfone padrão."))
        return {"ok": True, "ativo": mudo, "info": tr("Mudo") if mudo else tr("Ligado")}

    def audio(self):
        f = self.ferramenta_audio()
        if not f:
            return None
        som_mudo, volume = self._ler(f, "saida")
        mic_mudo, _ = self._ler(f, "entrada")
        return {"som_mudo": som_mudo, "volume": volume, "mic_mudo": mic_mudo,
                "tem_som": volume is not None, "tem_mic": mic_mudo is not None}


MIDIA_DO_PLAYER = {"alternar": "play", "proxima": "proxima", "anterior": "anterior"}
REUNIAO_MEET = re.compile(r"^https?://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}", re.I)
REUNIAO_MEET_TITULO = "Meet [-–] [a-z]{3}-[a-z]{4}-[a-z]{3}|Google Meet"
FORMATO_PLAYERCTL = "\x1f".join(["{{playerName}}", "{{status}}", "{{title}}", "{{artist}}", "{{album}}",
                                  "{{mpris:length}}", "{{position}}", "{{mpris:artUrl}}", "{{xesam:url}}"])
YOUTUBE_VIDEO = re.compile(r"(?:youtube\.com/(?:watch\?(?:[^#]*&)?v=|shorts/|live/|embed/)|youtu\.be/)([\w-]{11})", re.I)


def miniaturas_youtube(url):
    m = YOUTUBE_VIDEO.search(url or "")
    if not m:
        return None
    return ["https://i.ytimg.com/vi/%s/maxresdefault.jpg" % m.group(1), "https://i.ytimg.com/vi/%s/mqdefault.jpg" % m.group(1)]


def _titulo_video(t):
    t = re.sub(r"^\(\d+\+?\)\s*", "", str(t or "").strip())
    t = re.sub(r"\s+[-\u2013\u2014|]\s+YouTube(\s+Music)?\s*$", "", t, flags=re.I)
    return re.sub(r"[\W_]+", " ", unicodedata.normalize("NFKC", t).casefold()).strip()


def aba_do_video(abas, titulo):
    alvo = _titulo_video(titulo)
    if not alvo:
        return None
    candidatas = [a for a in abas if YOUTUBE_VIDEO.search(a.get("url") or "")]
    for a in candidatas:
        if _titulo_video(a.get("titulo")) == alvo:
            return a
    for a in candidatas:
        t = _titulo_video(a.get("titulo"))
        if t and min(len(t), len(alvo)) >= 8 and (alvo in t or t in alvo):
            return a
    if len(candidatas) == 1:
        return candidatas[0]
    return None


NOMES_NAVEGADORES = {"safari", "safari technology preview", "google chrome", "chrome", "microsoft edge", "brave browser", "brave",
                     "arc", "vivaldi", "opera", "opera gx", "firefox", "chromium", "orion", "zen", "zen browser"}


def eh_navegador(app_id, nome):
    i = (app_id or "").lower()
    return i in BUNDLES_NAVEGADORES or i.startswith("com.apple.webkit") or (nome or "").strip().lower() in NOMES_NAVEGADORES
NOMES_PLAYERS = {"spotify": "Spotify", "chrome": "Google Chrome", "chromium": "Chromium", "msedge": "Microsoft Edge",
                 "edge": "Microsoft Edge", "firefox": "Firefox", "brave": "Brave", "vlc": "VLC", "zunemusic": "Media Player",
                 "mediaplayer": "Media Player", "music": "Music", "itunes": "iTunes", "opera": "Opera", "vivaldi": "Vivaldi",
                 "deezer": "Deezer", "tidal": "TIDAL", "amazonmusic": "Amazon Music", "applemusic": "Apple Music",
                 "youtubemusic": "YouTube Music", "rhythmbox": "Rhythmbox", "mpv": "mpv", "elisa": "Elisa", "audacious": "Audacious",
                 "clementine": "Clementine", "strawberry": "Strawberry", "netflix": "Netflix", "plexamp": "Plexamp"}


def nome_do_player(bruto):
    t = str(bruto or "").strip()
    if not t:
        return ""
    base = t.split("!")[-1] if "!" in t else t
    base = re.sub(r"\.exe$", "", base, flags=re.I)
    base = base.split("_")[0].split(".instance")[0]
    chave = re.sub(r"[^a-z0-9]", "", base.lower())
    for k, nome in NOMES_PLAYERS.items():
        if k in chave:
            return nome
    partes = [x for x in re.split(r"[.\s]+", base) if x]
    nome = partes[-1] if partes else base
    return nome[:1].upper() + nome[1:]


def _json_objeto(saida):
    for linha in reversed((saida or "").strip().splitlines()):
        linha = linha.strip()
        if linha.startswith("{"):
            try:
                v = json.loads(linha)
            except ValueError:
                return None
            return v if isinstance(v, dict) else None
    return None


def criar_sistema():
    return {"mac": SistemaMac, "windows": SistemaWindows, "linux": SistemaLinux}[SISTEMA]()


TIPOS = {
    "teclas": "teclas", "tecla": "teclas", "keys": "teclas", "hotkey": "teclas", "atalho_de_teclado": "teclas",
    "texto": "texto", "text": "texto", "digitar": "texto",
    "app": "app", "aplicativo": "app", "abrir": "app", "programa": "app",
    "link": "link", "url": "link", "site": "link",
    "atalho": "atalho", "atalhos": "atalho", "shortcut": "atalho",
    "comando": "comando", "shell": "comando", "terminal": "comando",
    "applescript": "applescript",
    "midia": "midia", "media": "midia",
    "volume": "volume",
    "microfone": "microfone", "mic": "microfone",
    "energia": "energia", "power": "energia", "desligar": "energia", "sistema": "energia",
    "pagina": "pagina", "page": "pagina",
    "sequencia": "sequencia", "macro": "sequencia",
    "esperar": "esperar", "espera": "esperar", "wait": "esperar",
    "modo": "modo", "cena": "modo", "scene": "modo", "mode": "modo", "foco": "modo", "focus": "modo",
    "chamada": "chamada", "call": "chamada", "ligacao": "chamada", "reuniao": "chamada", "meeting": "chamada",
}
LISTA_TIPOS = ("app, teclas, texto, link, comando, midia, volume, microfone, energia, pagina, modo, chamada, sequencia, "
               "esperar, atalho e applescript (só Mac)")
ALIAS_CHAMADA = {
    "atender": "atender", "aceitar": "atender", "answer": "atender", "accept": "atender",
    "recusar": "recusar", "rejeitar": "recusar", "decline": "recusar", "reject": "recusar",
    "mudo": "mudo", "mutar": "mudo", "mute": "mudo", "unmute": "mudo", "desmutar": "mudo", "silenciar": "mudo", "microfone": "mudo",
    "camera": "camera", "video": "camera", "webcam": "camera", "cam": "camera",
    "encerrar": "encerrar", "desligar": "encerrar", "sair": "encerrar", "end": "encerrar", "leave": "encerrar", "hangup": "encerrar",
    "endcall": "encerrar", "leavecall": "encerrar",
}
APPS_CHAMADA = {
    "auto": {"nome": "auto"},
    "zoom": {"nome": "Zoom", "mac": ["zoom.us"], "windows": ["Zoom"], "linux": ["zoom", "ZoomLauncher"]},
    "teams": {"nome": "Microsoft Teams", "mac": ["MSTeams", "Microsoft Teams", "Microsoft Teams (work or school)", "Microsoft Teams classic"],
              "windows": ["ms-teams", "Teams"], "linux": ["teams-for-linux", "teams"]},
    "meet": {"nome": "Google Meet", "mac": [], "windows": [], "linux": []},
    "webex": {"nome": "Webex", "mac": ["Webex", "Cisco Webex Meetings"], "windows": ["CiscoCollabHost", "webexmta", "Webex"], "linux": []},
    "facetime": {"nome": "FaceTime", "mac": ["FaceTime"], "windows": [], "linux": []},
    "discord": {"nome": "Discord", "mac": ["Discord"], "windows": ["Discord"], "linux": ["Discord", "discord"]},
    "slack": {"nome": "Slack", "mac": ["Slack"], "windows": ["slack"], "linux": ["slack"]},
}
ALIAS_APP_CHAMADA = {"auto": "auto", "automatico": "auto", "qualquer": "auto", "zoom": "zoom", "zoomus": "zoom",
                     "teams": "teams", "microsoftteams": "teams", "msteams": "teams", "meet": "meet", "googlemeet": "meet",
                     "webex": "webex", "facetime": "facetime", "discord": "discord", "slack": "slack", "whatsapp": "auto"}
ORDEM_CHAMADA = ["meet", "zoom", "teams", "webex", "facetime"]
ATALHOS_CHAMADA = {
    "zoom": {"mac": {"mudo": "cmd+shift+a", "camera": "cmd+shift+v", "encerrar": "cmd+w", "atender": "ctrl+shift+a", "recusar": "ctrl+shift+d"},
             "outros": {"mudo": "alt+a", "camera": "alt+v", "encerrar": "alt+q", "atender": "ctrl+shift+a", "recusar": "ctrl+shift+d"}},
    "teams": {"mac": {"mudo": "cmd+shift+m", "camera": "cmd+shift+o", "encerrar": "cmd+shift+h", "atender": "cmd+shift+s", "recusar": "cmd+shift+d"},
              "outros": {"mudo": "ctrl+shift+m", "camera": "ctrl+shift+o", "encerrar": "ctrl+shift+h", "atender": "ctrl+shift+s", "recusar": "ctrl+shift+d"}},
    "meet": {"mac": {"mudo": "cmd+d", "camera": "cmd+e", "encerrar": "cmd+w"}, "outros": {"mudo": "ctrl+d", "camera": "ctrl+e", "encerrar": "ctrl+w"}},
    "webex": {"mac": {"mudo": "cmd+shift+m", "camera": "cmd+shift+v"}, "outros": {"mudo": "ctrl+m", "camera": "ctrl+shift+v"}},
    "facetime": {"mac": {}, "outros": {}},
    "discord": {"mac": {"mudo": "cmd+shift+m", "atender": "cmd+return", "recusar": "escape"},
                "outros": {"mudo": "ctrl+shift+m", "atender": "ctrl+return", "recusar": "escape"}},
    "slack": {"mac": {"mudo": "cmd+shift+space", "camera": "cmd+shift+v"}, "outros": {"mudo": "ctrl+shift+space", "camera": "ctrl+shift+v"}},
}
NOMES_CHAMADA = {"atender": "Atender", "recusar": "Recusar", "mudo": "Mudo na chamada", "camera": "Câmera", "encerrar": "Encerrar"}
ROTULOS_ACEITAR = ("accept", "aceitar", "atender", "answer", "aceptar", "contestar")
ROTULOS_RECUSAR = ("decline", "recusar", "rejeitar", "rechazar", "reject")
ATALHOS_FOCO_MAC = {True: ("Deck Foco Ligar", "Deck Focus On"), False: ("Deck Foco Desligar", "Deck Focus Off")}
ALIAS_ENERGIA = {
    "desligar": "desligar", "shutdown": "desligar", "poweroff": "desligar", "apagar": "desligar", "off": "desligar",
    "reiniciar": "reiniciar", "restart": "reiniciar", "reboot": "reiniciar",
    "suspender": "suspender", "dormir": "suspender", "sleep": "suspender", "repouso": "suspender", "hibernar": "suspender",
    "bloquear": "bloquear", "lock": "bloquear", "travar": "bloquear", "tela": "bloquear", "bloquear_tela": "bloquear",
}
NOMES_ENERGIA = {"desligar": "Desligar", "reiniciar": "Reiniciar", "suspender": "Suspender", "bloquear": "Bloquear"}
ALIAS_MIDIA = {
    "play": "play", "pause": "play", "playpause": "play", "play/pause": "play", "play_pause": "play",
    "tocar": "play", "pausar": "play", "tocar_pausar": "play", "tocar/pausar": "play",
    "proxima": "proxima", "proximo": "proxima", "next": "proxima", "avancar": "proxima", "seguinte": "proxima",
    "anterior": "anterior", "previous": "anterior", "prev": "anterior", "voltar": "anterior",
}
ALIAS_VOLUME = {
    "subir": "subir", "aumentar": "subir", "mais": "subir", "+": "subir", "up": "subir",
    "descer": "descer", "baixar": "descer", "diminuir": "descer", "menos": "descer", "-": "descer", "down": "descer",
    "mudo": "mudo", "mute": "mudo", "silenciar": "mudo",
}
CORES = {
    "vermelho": "#ff453a", "laranja": "#ff9f0a", "amarelo": "#ffd60a", "verde": "#30d158",
    "menta": "#63e6e2", "ciano": "#64d2ff", "azul": "#0a84ff", "anil": "#5e5ce6", "roxo": "#bf5af2",
    "rosa": "#ff375f", "marrom": "#ac8e68", "cinza": "#636366", "grafite": "#2c2c2e",
    "preto": "#0b0b0c", "branco": "#f2f2f7",
}
SELOS = {"mic": ("MUDO", "#ff453a"), "vol_mudo": ("MUDO", "#ff453a")}
IMAGENS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
CHAVES_SISTEMA = {"mac": "mac", "macos": "mac", "windows": "windows", "win": "windows", "linux": "linux",
                  "padrao": "padrao", "outros": "padrao", "default": "padrao"}
FALTA = object()


def por_sistema(valor):
    if not isinstance(valor, dict) or not valor:
        return valor
    if not all(simples(k) in CHAVES_SISTEMA for k in valor):
        return valor
    mapa = {CHAVES_SISTEMA[simples(k)]: v for k, v in valor.items()}
    if SISTEMA in mapa:
        return mapa[SISTEMA]
    return mapa.get("padrao", FALTA)


def resolver_campos(b):
    saida, faltou = {}, False
    for k, v in b.items():
        r = por_sistema(v)
        if r is FALTA:
            faltou = True
            continue
        saida[k] = r
    return saida, faltou


def pega(d, *nomes):
    for n in nomes:
        if n in d and d[n] is not None:
            return d[n]
    return None


def _texto_obrigatorio(b, onde, nomes, exemplo):
    v = pega(b, *nomes)
    if not isinstance(v, str) or not v.strip():
        raise ErroConfig(tr('%s: falta "%s" (ex.: %s)') % (onde, nomes[0], exemplo))
    return v.strip()


def _segundos(valor, padrao, maximo, onde, nome):
    if valor is None:
        return padrao
    try:
        if isinstance(valor, bool):
            raise ValueError
        return max(0.0, min(maximo, float(str(valor).replace(",", "."))))
    except (TypeError, ValueError):
        raise ErroConfig(tr('%s: "%s" precisa ser um número de segundos (ex.: 0.5)') % (onde, nome))


def _lista_do_modo(b, onde, nomes):
    v = pega(b, *nomes)
    if v in (None, "", []):
        return []
    itens = v if isinstance(v, list) else [v]
    saida = []
    for x in itens:
        x = por_sistema(x)
        if x is FALTA or not isinstance(x, str) or not x.strip():
            continue
        saida.append(x.strip()[:300])
    if len(saida) > 12:
        raise ErroConfig(tr('%s: no máximo 12 itens em "%s"') % (onde, nomes[0]))
    return saida


def normalizar_acao(b, onde, nivel=0):
    if nivel > 3:
        raise ErroConfig(tr("%s: sequência dentro de sequência demais") % onde)
    bruto = b.get("tipo")
    if not bruto:
        raise ErroConfig(tr('%s: falta "tipo" (use: %s)') % (onde, LISTA_TIPOS))
    tipo = TIPOS.get(simples(bruto))
    if not tipo:
        raise ErroConfig(tr('%s: tipo "%s" não existe (use: %s)') % (onde, bruto, LISTA_TIPOS))
    a = {"tipo": tipo}

    if tipo == "teclas":
        t = b.get("teclas")
        lista = t if isinstance(t, list) else [t]
        if not t or not all(isinstance(x, str) and x.strip() for x in lista):
            raise ErroConfig(tr('%s: escreva as teclas, ex.: "teclas": "ctrl+c"') % onde)
        if len(lista) > 30:
            raise ErroConfig(tr("%s: no máximo 30 combinações por botão") % onde)
        a["combos"] = [ler_combinacao(x, onde) for x in lista]
        for _, (k, valor) in a["combos"]:
            if k == "nome" and not tecla_existe(valor):
                raise ErroConfig(tr('%s: a tecla "%s" não existe no %s') % (onde, valor, NOMES_SISTEMA[SISTEMA]))
        if pega(b, "app"):
            a["app"] = str(b["app"])
        a["intervalo"] = _segundos(pega(b, "intervalo"), 0.08, 2.0, onde, "intervalo")
    elif tipo == "texto":
        v = pega(b, "texto", "text")
        if not isinstance(v, str) or not v:
            raise ErroConfig(tr('%s: falta "texto" (ex.: "texto": "Bom dia!")') % onde)
        a["texto"] = v
        if pega(b, "app"):
            a["app"] = str(b["app"])
    elif tipo == "app":
        v = pega(b, "app", "nome", "programa")
        lista = v if isinstance(v, list) else [v]
        lista = [str(x).strip() for x in lista if isinstance(x, str) and x.strip()]
        if not lista:
            raise ErroConfig(tr('%s: falta "app" (ex.: "app": "Spotify")') % onde)
        a["apps"] = lista
    elif tipo == "link":
        url = _texto_obrigatorio(b, onde, ("url", "link"), '"url": "https://..."')
        a["url"] = url if tem_esquema(url) else "https://" + url
        nav = pega(b, "navegador", "browser")
        if isinstance(nav, str) and nav.strip():
            a["navegador"] = nav.strip()[:60]
        a["aba"] = pega(b, "aba", "reaproveitar") is not False
    elif tipo == "atalho":
        a["atalho"] = _texto_obrigatorio(b, onde, ("atalho", "nome"), tr('"atalho": "Nome no app Atalhos"'))
    elif tipo == "comando":
        a["comando"] = _texto_obrigatorio(b, onde, ("comando", "shell"), tr('"comando": "echo oi"'))
        a["mostrar"] = bool(pega(b, "mostrar"))
    elif tipo == "applescript":
        a["script"] = _texto_obrigatorio(b, onde, ("script", "applescript"), '"script": "beep"')
        a["mostrar"] = bool(pega(b, "mostrar"))
    elif tipo == "midia":
        v = pega(b, "midia", "mídia", "acao", "ação") or "play"
        m = ALIAS_MIDIA.get(simples(v))
        if not m:
            raise ErroConfig(tr('%s: "midia" deve ser play, proxima ou anterior') % onde)
        a["midia"] = m
    elif tipo == "volume":
        v = pega(b, "volume", "acao", "ação")
        erro = tr('%s: "volume" deve ser subir, descer, mudo ou um número de 0 a 100') % onde
        if isinstance(v, bool) or v is None:
            raise ErroConfig(erro)
        if isinstance(v, (int, float)):
            a["volume"] = str(max(0, min(100, int(v))))
        else:
            m = ALIAS_VOLUME.get(str(v).strip()) or ALIAS_VOLUME.get(simples(v))
            if not m and str(v).strip().isdigit():
                m = str(max(0, min(100, int(str(v).strip()))))
            if not m:
                raise ErroConfig(erro)
            a["volume"] = m
    elif tipo == "microfone":
        pass
    elif tipo == "energia":
        v = pega(b, "energia", "acao", "ação")
        m = ALIAS_ENERGIA.get(simples(v)) if isinstance(v, str) else None
        if not m:
            raise ErroConfig(tr('%s: "energia" deve ser desligar, reiniciar, suspender ou bloquear') % onde)
        a["energia"] = m
    elif tipo == "pagina":
        v = pega(b, "pagina", "página", "destino")
        if not isinstance(v, (str, int)) or isinstance(v, bool) or (isinstance(v, str) and not v.strip()):
            raise ErroConfig(tr('%s: diga para qual página ir, ex.: "pagina": "Apps"') % onde)
        a["pagina"] = v
    elif tipo == "modo":
        a["abrir"] = _lista_do_modo(b, onde, ("abrir", "open"))
        a["fechar"] = _lista_do_modo(b, onde, ("fechar", "close"))
        np = pega(b, "nao_perturbe", "não_perturbe", "naoPerturbe", "dnd")
        a["nao_perturbe"] = np if isinstance(np, bool) else None
        vol = pega(b, "volume")
        if vol in (None, "") or isinstance(vol, bool):
            a["volume"] = None
        elif isinstance(vol, (int, float)) or str(vol).strip().isdigit():
            a["volume"] = max(0, min(100, int(float(vol))))
        else:
            raise ErroConfig(tr('%s: "volume" do modo deve ser um número de 0 a 100') % onde)
        mins = pega(b, "minutos", "timer", "cronometro", "cronômetro")
        if mins in (None, "", 0, False):
            a["minutos"] = None
        elif isinstance(mins, bool) or not str(mins).strip().replace(".", "", 1).isdigit():
            raise ErroConfig(tr('%s: "minutos" deve ser um número (ex.: 25)') % onde)
        else:
            a["minutos"] = max(1, min(480, int(float(mins))))
        pg = pega(b, "pagina", "página")
        if isinstance(pg, (str, int)) and not isinstance(pg, bool) and str(pg).strip():
            a["pagina"] = pg
        if not (a["abrir"] or a["fechar"] or a["nao_perturbe"] is not None or a["volume"] is not None
                or a["minutos"] or a.get("pagina") is not None):
            raise ErroConfig(tr("%s: o modo não faz nada — escolha o que ele abre, fecha ou liga") % onde)
    elif tipo == "chamada":
        v = pega(b, "chamada", "acao", "ação")
        m = ALIAS_CHAMADA.get(re.sub(r"[^a-z]", "", simples(v))) if isinstance(v, str) else None
        if not m:
            raise ErroConfig(tr('%s: "chamada" deve ser atender, recusar, mudo, camera ou encerrar') % onde)
        a["chamada"] = m
        app = pega(b, "app", "programa") or "auto"
        k = ALIAS_APP_CHAMADA.get(re.sub(r"[^a-z]", "", simples(app))) if isinstance(app, str) else None
        if not k:
            raise ErroConfig(tr('%s: app de chamada "%s" desconhecido (use auto, zoom, teams, meet, facetime, discord, slack ou webex)')
                             % (onde, app))
        a["app"] = k
    elif tipo == "sequencia":
        lista = pega(b, "acoes", "ações", "passos")
        if not isinstance(lista, list) or not lista:
            raise ErroConfig(tr('%s: "acoes" deve ser uma lista de ações') % onde)
        if len(lista) > 30:
            raise ErroConfig(tr("%s: no máximo 30 passos por sequência") % onde)
        passos = []
        for n, item in enumerate(lista):
            sub = tr("%s, passo %d") % (onde, n + 1)
            if not isinstance(item, dict):
                raise ErroConfig(tr("%s: cada passo é um { ... } com tipo") % sub)
            item, faltou = resolver_campos(item)
            if faltou:
                continue
            p = normalizar_acao(item, sub, nivel + 1)
            if p["tipo"] in ("pagina", "modo"):
                raise ErroConfig(tr("%s: troca de página ou modo não pode ficar dentro de sequência") % sub)
            passos.append(p)
        if not passos:
            raise ErroConfig(tr("%s: nenhum passo vale para o %s") % (onde, NOMES_SISTEMA[SISTEMA]))
        a["acoes"] = passos
    elif tipo == "esperar":
        a["segundos"] = _segundos(pega(b, "segundos", "tempo"), 0.5, 10.0, onde, "segundos")
    return a


def chave_estado(a):
    t = a["tipo"]
    if t == "microfone":
        return ("mic",)
    if t == "volume" and a["volume"] == "mudo":
        return ("vol_mudo",)
    if t == "sequencia":
        ultima = None
        for p in a["acoes"]:
            ultima = chave_estado(p) or ultima
        return ultima
    return None


def energia_perigosa(a):
    if not a:
        return False
    if a["tipo"] == "sequencia":
        return any(energia_perigosa(p) for p in a["acoes"])
    return a["tipo"] == "energia" and a["energia"] != "bloquear"


def tipos_em(a):
    if not a:
        return set()
    if a["tipo"] == "sequencia":
        s = set()
        for p in a["acoes"]:
            s |= tipos_em(p)
        return s
    return {a["tipo"]}


def motivo_fixo(a):
    if a and SISTEMA != "mac" and tipos_em(a) & {"atalho", "applescript"}:
        return tr("Este botão usa um recurso que só existe no Mac.")
    return None


def cor_valida(v, onde, avisos):
    if v in (None, ""):
        return None
    s = str(v).strip()
    if s.lower() in CORES:
        return CORES[s.lower()]
    if simples(s) in CORES:
        return CORES[simples(s)]
    if re.fullmatch(r"#?[0-9a-fA-F]{6}", s) or re.fullmatch(r"#?[0-9a-fA-F]{3}", s):
        s = s.lstrip("#")
        if len(s) == 3:
            s = "".join(ch * 2 for ch in s)
        return "#" + s.lower()
    avisos.append(tr('%s: cor "%s" não reconhecida (use #ff8800 ou %s)') % (onde, v, ", ".join(CORES)))
    return None


ROTULO_PADRAO = {"teclas": "Teclas", "texto": "Texto", "app": "App", "link": "Link", "atalho": "Atalho",
                 "comando": "Comando", "applescript": "Script", "midia": "Mídia", "volume": "Volume",
                 "microfone": "Microfone", "energia": "Energia", "pagina": "Página", "sequencia": "Sequência", "esperar": "Esperar",
                 "modo": "Modo", "chamada": "Chamada"}


def montar_botao(b, pi, bi, pnome, avisos):
    onde = tr('Página "%s", botão %d') % (pnome, bi + 1)
    if b is None or b == {}:
        return None
    if not isinstance(b, dict):
        avisos.append(tr("%s: formato inválido (use { ... } ou null para deixar vazio)") % onde)
        return None
    b, faltou = resolver_campos(b)
    titulo = pega(b, "titulo", "título", "nome", "label")
    icone = pega(b, "icone", "ícone", "emoji", "icon")
    imagem = pega(b, "imagem", "image")
    bt = {
        "p": pi, "i": bi, "pagina_nome": pnome,
        "titulo": str(titulo)[:40] if titulo not in (None, "") else "",
        "icone": str(icone)[:16] if icone not in (None, "") else None,
        "imagem": None,
        "cor": cor_valida(pega(b, "cor", "color"), onde, avisos),
        "confirmar": bool(pega(b, "confirmar", "confirm")),
        "confirma_padrao": pega(b, "confirmar", "confirm") is None,
        "titulo_ativo": str(pega(b, "titulo_ativo", "título_ativo") or "")[:40] or None,
        "icone_ativo": str(pega(b, "icone_ativo", "ícone_ativo") or "")[:16] or None,
        "acao": None, "erro": None, "chave": None, "fora": None,
    }
    if imagem:
        nome = str(imagem)
        if os.path.basename(nome) != nome or os.path.splitext(nome)[1].lower() not in IMAGENS:
            avisos.append(tr('%s: "imagem" deve ser só o nome de um arquivo .png/.jpg/.svg da pasta icones') % onde)
        else:
            bt["imagem"] = nome
            if not os.path.isfile(os.path.join(PASTA_ICONES, nome)):
                avisos.append(tr("%s: não achei icones/%s") % (onde, nome))
    if faltou:
        bt["fora"] = tr("Este botão não tem versão para %s.") % NOMES_SISTEMA[SISTEMA]
    else:
        try:
            bt["acao"] = normalizar_acao(b, onde)
            bt["chave"] = chave_estado(bt["acao"])
            bt["fora"] = motivo_fixo(bt["acao"])
        except ErroConfig as e:
            bt["erro"] = str(e)
            avisos.append(str(e))
        except (TypeError, ValueError) as e:
            bt["erro"] = tr("%s: valor inválido (%s)") % (onde, e)
            avisos.append(bt["erro"])
    if not bt["titulo"] and not bt["icone"] and not bt["imagem"]:
        bt["titulo"] = tr(ROTULO_PADRAO.get((bt["acao"] or {}).get("tipo"), "Botão"))
    if bt.pop("confirma_padrao") and energia_perigosa(bt["acao"]):
        bt["confirmar"] = True
    if bt["acao"] and bt["acao"]["tipo"] == "modo":
        bt["acao"].update({"id": "%d.%d" % (pi, bi), "titulo": bt["titulo"] or tr("Modo"), "icone": bt["icone"], "cor": bt["cor"]})
    return bt


ICONES_PAGINA = ("estrela", "grade", "globo", "play", "raio", "engrenagem", "pasta", "casa", "musica", "chat", "camera",
                 "codigo", "coracao", "maleta", "jogo", "video", "lampada", "sino", "lua")
TIPOS_PAGINA = {"": "botoes", "botoes": "botoes", "buttons": "botoes", "player": "player", "dj": "player",
                "musica": "player", "tocando": "player", "nowplaying": "player"}
TEMAS = {"preto": "preto", "black": "preto", "escuro": "preto", "dark": "preto", "oled": "preto",
         "normal": "normal", "cinza": "normal", "grafite": "normal", "claro": "normal"}
LUZES = {"parada": "parada", "parado": "parada", "fixa": "parada", "ligada": "parada", "on": "parada", "static": "parada",
         "correndo": "correndo", "corrente": "correndo", "animada": "correndo", "movendo": "correndo", "running": "correndo",
         "moving": "correndo", "desligada": "desligada", "desligado": "desligada", "off": "desligada", "nenhuma": "desligada",
         "none": "desligada"}


class Deck:
    def __init__(self, nome, colunas, linhas, paginas, avisos, versao, tema="preto", luz="parada"):
        self.nome = nome
        self.colunas = colunas
        self.linhas = linhas
        self.paginas = paginas
        self.avisos = avisos
        self.versao = versao
        self.tema = tema
        self.luz = luz
        self.total = sum(1 for p in paginas for b in p["botoes"] if b)

    @classmethod
    def vazio(cls, motivo):
        return cls("Deck", 4, 2, [], [], "erro-" + hashlib.sha1(motivo.encode()).hexdigest()[:8])

    def botao(self, p, i):
        if 0 <= p < len(self.paginas) and 0 <= i < len(self.paginas[p]["botoes"]):
            return self.paginas[p]["botoes"][i]
        return None

    def publico(self, imgs=None):
        imgs = imgs or {}
        return {
            "nome": self.nome, "versao": self.versao, "tema": self.tema, "luz": self.luz,
            "grade": {"colunas": self.colunas, "linhas": self.linhas},
            "paginas": [dict({"nome": p["nome"], "icone": p.get("icone"), "tipo": p.get("tipo", "botoes"),
                              "botoes": [botao_publico(b, imgs.get((b["p"], b["i"])) if b else None) for b in p["botoes"]]},
                             **({"oculta": True} if p.get("oculta") else {}))
                        for p in self.paginas],
            "avisos": list(self.avisos),
        }


def botao_publico(bt, img=None):
    if bt is None:
        return None
    a = bt["acao"] or {}
    d = {"p": bt["p"], "i": bt["i"], "titulo": bt["titulo"], "tipo": a.get("tipo")}
    if img:
        d["img"] = img[0]
        if img[1]:
            d["img2"] = img[1]
    for k_int, k_pub in (("icone", "icone"), ("cor", "cor"), ("erro", "erro"),
                         ("titulo_ativo", "tituloAtivo"), ("icone_ativo", "iconeAtivo")):
        if bt.get(k_int):
            d[k_pub] = bt[k_int]
    if bt["confirmar"]:
        d["confirmar"] = True
    if a.get("tipo") in ("pagina", "modo") and a.get("destino_idx") is not None:
        d["destino"] = a.get("destino_idx")
    if bt["chave"]:
        selo, cor = SELOS[bt["chave"][0]]
        d["selo"] = tr(selo)
        d["corAtivo"] = cor
    if a.get("tipo") == "modo":
        d["selo"] = tr("ATIVO")
        d["corAtivo"] = bt["cor"] or "#5e5ce6"
    return d


def _limitar(v, minimo, maximo, padrao):
    return max(minimo, min(maximo, _int(v, padrao)))


def montar_deck(dados, versao):
    if not isinstance(dados, dict):
        raise ErroConfig(tr("config.json precisa começar com { e terminar com }."))
    avisos = []
    grade = dados.get("grade") if isinstance(dados.get("grade"), dict) else {}
    brutas = pega(dados, "paginas", "páginas")
    if not isinstance(brutas, list):
        raise ErroConfig(tr('config.json precisa de "paginas": [ ... ]'))
    paginas = []
    for pi, p in enumerate(brutas):
        if not isinstance(p, dict):
            avisos.append(tr("Página %d: formato inválido") % (pi + 1))
            p = {}
        pnome = str(p.get("nome") or tr("Página %d") % (pi + 1))[:24]
        botoes_brutos = pega(p, "botoes", "botões") or []
        if not isinstance(botoes_brutos, list):
            avisos.append(tr('Página "%s": "botoes" deve ser uma lista [ ... ]') % pnome)
            botoes_brutos = []
        picone = pega(p, "icone", "ícone")
        picone = simples(picone) if isinstance(picone, str) and simples(picone) in ICONES_PAGINA else None
        ptipo = TIPOS_PAGINA.get(simples(p.get("tipo") or ""), "botoes")
        poculta = pega(p, "oculta", "oculto", "escondida", "hidden")
        paginas.append({"nome": pnome, "icone": picone, "tipo": ptipo, "oculta": poculta is True,
                        "botoes": [] if ptipo == "player" else
                        [montar_botao(b, pi, bi, pnome, avisos) for bi, b in enumerate(botoes_brutos)]})

    nomes = {simples(p["nome"]): n for n, p in enumerate(paginas)}
    for p in paginas:
        for bt in p["botoes"]:
            a = bt and bt["acao"]
            if not a or a["tipo"] not in ("pagina", "modo") or a.get("pagina") is None:
                continue
            alvo = a["pagina"]
            if isinstance(alvo, int):
                idx = alvo - 1 if 1 <= alvo <= len(paginas) else None
            elif simples(alvo) in ("inicio", "primeira", "home"):
                idx = 0
            else:
                idx = nomes.get(simples(alvo))
                if idx is None and str(alvo).strip().isdigit() and 1 <= int(alvo) <= len(paginas):
                    idx = int(alvo) - 1
            if idx is None:
                aviso = tr('Página "%s", botão %d: não existe página "%s"') % (p["nome"], bt["i"] + 1, alvo)
                avisos.append(aviso)
                if a["tipo"] == "pagina":
                    bt["erro"] = aviso
            a["destino_idx"] = idx

    tema = TEMAS.get(simples(dados.get("tema") or "preto"), "preto")
    luz = dados.get("luz")
    luz = "desligada" if luz is False else LUZES.get(simples(str(luz or "parada")), "parada")
    return Deck(
        nome=str(dados.get("nome") or "Deck")[:40],
        colunas=_limitar(grade.get("colunas"), 1, 8, 4),
        linhas=_limitar(grade.get("linhas"), 1, 8, 2),
        paginas=paginas, avisos=avisos, versao=versao, tema=tema, luz=luz,
    )


ERROS_JSON = [
    ("Illegal trailing comma", "vírgula sobrando antes de } ou ]"),
    ("Expecting ',' delimiter", "faltou uma vírgula"),
    ("Expecting property name enclosed in double quotes", "vírgula sobrando antes de } ou nome sem aspas duplas"),
    ("Expecting value", "faltou um valor (vírgula sobrando antes de ] ?)"),
    ("Expecting ':' delimiter", "faltou os dois-pontos depois do nome"),
    ("Unterminated string", "aspas abertas e não fechadas"),
    ("Invalid control character", "quebra de linha dentro de um texto (use \\n)"),
    ("Extra data", "sobrou texto depois do último }"),
    ("Invalid \\escape", "barra invertida inválida (use \\\\ ou /)"),
]


def ler_config(caminho):
    with open(caminho, "rb") as f:
        bruto = f.read()
    versao = hashlib.sha1(bruto + SISTEMA.encode()).hexdigest()[:12]
    try:
        dados = json.loads(bruto.decode("utf-8-sig"))
    except UnicodeDecodeError:
        raise ErroConfig(tr("config.json não está salvo em UTF-8."))
    except json.JSONDecodeError as e:
        dica = tr(next((pt for en, pt in ERROS_JSON if e.msg.startswith(en)), e.msg))
        raise ErroConfig(tr("config.json com erro na linha %d, coluna %d: %s") % (e.lineno, e.colno, dica))
    if isinstance(dados, dict):
        definir_idioma(dados.get("idioma"))
        traduzir_nomes_padrao(dados)
    return montar_deck(dados, versao), dados


def carregar_config(caminho):
    return ler_config(caminho)[0]


def _json_linha(v):
    return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))


def formatar_config(dados):
    linhas = ["{"]
    itens = list(dados.items())
    for n, (k, v) in enumerate(itens):
        fim = "," if n < len(itens) - 1 else ""
        chave = json.dumps(k, ensure_ascii=False)
        if simples(k) == "paginas" and isinstance(v, list) and v:
            linhas.append("  %s: [" % chave)
            for pn, pagina in enumerate(v):
                pfim = "," if pn < len(v) - 1 else ""
                if not isinstance(pagina, dict):
                    linhas.append("    " + _json_linha(pagina) + pfim)
                    continue
                linhas.append("    {")
                pitens = list(pagina.items())
                for m, (pk, pv) in enumerate(pitens):
                    f2 = "," if m < len(pitens) - 1 else ""
                    pchave = json.dumps(pk, ensure_ascii=False)
                    if simples(pk) == "botoes" and isinstance(pv, list) and pv:
                        linhas.append("      %s: [" % pchave)
                        for bn, b in enumerate(pv):
                            linhas.append("        " + _json_linha(b) + ("," if bn < len(pv) - 1 else ""))
                        linhas.append("      ]" + f2)
                    else:
                        linhas.append("      %s: %s%s" % (pchave, _json_linha(pv), f2))
                linhas.append("    }" + pfim)
            linhas.append("  ]" + fim)
        else:
            linhas.append("  %s: %s%s" % (chave, _json_linha(v), fim))
    linhas.append("}")
    return "\n".join(linhas) + "\n"


def gravar_atomico(caminho, texto):
    pasta = os.path.dirname(os.path.abspath(caminho))
    dados = texto.encode("utf-8") if isinstance(texto, str) else texto
    fd, tmp = tempfile.mkstemp(prefix=".deck-", suffix=".tmp", dir=pasta)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(tmp, os.stat(caminho).st_mode & 0o777)
        except OSError:
            os.chmod(tmp, 0o644)
        for tentativa in range(6):
            try:
                os.replace(tmp, caminho)
                return
            except PermissionError:
                if tentativa == 5:
                    raise
                time.sleep(0.15)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def nome_do_computador():
    if SISTEMA == "mac":
        n = _saida(["scutil", "--get", "ComputerName"])
        if n:
            return n
    if SISTEMA == "windows":
        n = os.environ.get("COMPUTERNAME")
        if n:
            return n
    return platform.node().split(".")[0] or socket.gethostname() or "Computador"


def host_local():
    n = _saida(["scutil", "--get", "LocalHostName"]) if SISTEMA == "mac" else ""
    n = n or socket.gethostname().split(".")[0]
    if not n:
        return None
    return n if n.endswith(".local") else n + ".local"


NOMES_VIA = {"usb": "cabo USB", "bluetooth": "Bluetooth", "compartilhamento": "rede do computador", "rede": "Wi-Fi"}


def tipo_do_endereco(ip, dispositivo, descricao):
    d = (dispositivo or "").lower()
    desc = (descricao or "").lower()
    if "iphone usb" in desc or "ipad usb" in desc or "apple mobile device" in desc or "rndis" in desc or "ncm" in desc \
            or d.startswith(("usb", "enx")) or ip.startswith("192.168.42."):
        return "usb"
    if "bluetooth" in desc or d.startswith("bnep") or ip.startswith("192.168.44."):
        return "bluetooth"
    if d.startswith("bridge") or ip in ("192.168.2.1", "192.168.137.1", "10.42.0.1"):
        return "compartilhamento"
    if ip.startswith("172.20.10.") and "usb" in desc:
        return "usb"
    return "rede"


def _portas_mac():
    portas = {}
    atual = None
    for linha in _saida(["networksetup", "-listallhardwareports"]).splitlines():
        m = re.match(r"Hardware Port:\s*(.+)", linha.strip())
        if m:
            atual = m.group(1).strip()
            continue
        m = re.match(r"Device:\s*(\S+)", linha.strip())
        if m and atual:
            portas[m.group(1)] = atual
    return portas


def _enderecos_mac():
    portas = _portas_mac()
    lista = []
    dispositivo = None
    for linha in _saida(["ifconfig"]).splitlines():
        m = re.match(r"^(\S+):\s+flags", linha)
        if m:
            dispositivo = m.group(1)
            continue
        m = re.search(r"\binet (\d+\.\d+\.\d+\.\d+) netmask \S+ broadcast", linha)
        if m and dispositivo:
            lista.append((m.group(1), dispositivo, portas.get(dispositivo, "")))
    return lista


def _enderecos_linux():
    lista = []
    for m in re.finditer(r"^\d+:\s+(\S+)\s+inet (\d+\.\d+\.\d+\.\d+)/\d+ brd", _saida(["ip", "-4", "-o", "addr", "show"]), re.M):
        lista.append((m.group(2), m.group(1), ""))
    return lista


def _enderecos_windows():
    comando = ("Get-NetIPAddress -AddressFamily IPv4 | ForEach-Object { $a = Get-NetAdapter -InterfaceIndex $_.InterfaceIndex "
               "-ErrorAction SilentlyContinue; [pscustomobject]@{ip=$_.IPAddress; nome=$_.InterfaceAlias; "
               "desc=[string]$a.InterfaceDescription; estado=[string]$a.Status} } | ConvertTo-Json -Compress")
    texto = _saida(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando])
    lista = []
    try:
        dados = json.loads(texto) if texto.strip() else []
    except ValueError:
        dados = []
    if isinstance(dados, dict):
        dados = [dados]
    for e in dados if isinstance(dados, list) else []:
        if not isinstance(e, dict) or not e.get("ip"):
            continue
        if str(e.get("estado") or "").lower() in ("disconnected", "not present", "disabled"):
            continue
        lista.append((str(e["ip"]), str(e.get("nome") or ""), str(e.get("desc") or "") + " " + str(e.get("nome") or "")))
    if not lista:
        try:
            lista = [(ip, "", "") for ip in socket.gethostbyname_ex(socket.gethostname())[2]]
        except OSError:
            lista = []
    return lista


def ip_da_rota_padrao():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
    except OSError:
        return None
    return ip if not ip.startswith("127.") else None


def enderecos_locais():
    if SISTEMA == "mac":
        brutos = _enderecos_mac()
    elif SISTEMA == "linux":
        brutos = _enderecos_linux()
    else:
        brutos = _enderecos_windows()
    padrao = ip_da_rota_padrao()
    lista = []
    vistos = set()
    for ip, dispositivo, descricao in brutos:
        if ip in vistos or ip.startswith(("127.", "169.254.")):
            continue
        vistos.add(ip)
        lista.append({"ip": ip, "via": descricao or dispositivo or "", "tipo": tipo_do_endereco(ip, dispositivo, descricao)})
    if padrao and padrao not in vistos:
        lista.append({"ip": padrao, "via": "", "tipo": "rede"})
    ordem = {"rede": 0, "usb": 1, "bluetooth": 2, "compartilhamento": 3}
    lista.sort(key=lambda e: (ordem.get(e["tipo"], 9), 0 if e["ip"] == padrao else 1))
    return lista


def ips_locais():
    return [e["ip"] for e in enderecos_locais()]


_FIREWALL = [0.0, None]


def firewall_bloqueando():
    if SISTEMA != "mac":
        return False
    if time.time() - _FIREWALL[0] < 60:
        return bool(_FIREWALL[1])
    exe = shutil.which("socketfilterfw") or "/usr/libexec/ApplicationFirewall/socketfilterfw"
    bloqueia = False
    if os.path.exists(exe):
        estado = _saida([exe, "--getglobalstate"]).lower()
        if "enabled" in estado and "disabled" not in estado:
            if "enabled" in _saida([exe, "--getblockall"]).lower().replace("disabled", ""):
                bloqueia = True
            else:
                python = False
                for linha in _saida([exe, "--listapps"]).splitlines():
                    baixa = linha.lower()
                    if "incoming connections" in baixa:
                        if python and "block" in baixa:
                            bloqueia = True
                        python = False
                    elif "python" in baixa:
                        python = True
    _FIREWALL[0] = time.time()
    _FIREWALL[1] = bloqueia
    return bloqueia


def _ler_token(caminho):
    try:
        with open(caminho) as f:
            t = f.read().strip()
    except OSError:
        return None
    return t if re.fullmatch(r"[A-Za-z0-9_\-]{16,}", t) else None


def _gravar_token(caminho, t):
    fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(t + "\n")


def carregar_token(renovar=False):
    arquivo = os.path.join(pasta_do_usuario("dados"), "token")
    if not renovar:
        t = _ler_token(arquivo)
        if t:
            return t, False
        t = _ler_token(ARQ_TOKEN_ANTIGO)
        if t:
            try:
                _gravar_token(arquivo, t)
            except OSError:
                pass
            return t, False
    t = secrets.token_urlsafe(16)
    _gravar_token(arquivo, t)
    if renovar and os.path.exists(ARQ_TOKEN_ANTIGO):
        try:
            os.remove(ARQ_TOKEN_ANTIGO)
        except OSError:
            pass
    return t, True


UA_NAVEGADOR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.5 Safari/605.1.15")


def _baixar_curl(url, limite, tempo):
    fd, tmp = tempfile.mkstemp(prefix="deck-")
    os.close(fd)
    try:
        codigo, saida, erro = rodar(["curl", "-sSL", "--max-time", str(int(tempo)), "--max-filesize", str(limite),
                                     "-A", UA_NAVEGADOR, "-H", "Accept-Language: pt-BR,pt;q=0.9,en;q=0.8",
                                     "-o", tmp, "-w", "%{url_effective}\\n%{content_type}\\n%{http_code}", url],
                                    espera=tempo + 5)
        partes = (saida or "").splitlines()
        if codigo != 0 or len(partes) < 3 or not partes[2].startswith("2"):
            raise ErroAcao(tr("Não consegui abrir %s.") % url)
        with open(tmp, "rb") as f:
            return _descompactar(f.read(limite), "", limite), partes[0], partes[1]
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _descompactar(dados, codificacao, limite):
    cod = (codificacao or "").lower()
    if dados[:2] == b"\x1f\x8b" or "gzip" in cod:
        try:
            return zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(dados, limite)
        except zlib.error:
            return dados
    if "deflate" in cod:
        for bits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
            try:
                return zlib.decompressobj(bits).decompress(dados, limite)
            except zlib.error:
                continue
    return dados


def baixar(url, limite, tempo=8.0):
    pedido = urllib.request.Request(url, headers={
        "User-Agent": UA_NAVEGADOR, "Accept": "text/html,image/*,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    try:
        with urllib.request.urlopen(pedido, timeout=tempo) as r:
            try:
                dados = r.read(limite)
            except http.client.IncompleteRead as e:
                dados = e.partial
            return (_descompactar(dados, r.headers.get("Content-Encoding"), limite), r.geturl(),
                    r.headers.get("Content-Type", ""))
    except (ssl.SSLError, urllib.error.URLError) as e:
        motivo = getattr(e, "reason", e)
        if isinstance(motivo, ssl.SSLError) and shutil.which("curl"):
            return _baixar_curl(url, limite, tempo)
        raise


class LeitorSite(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self, convert_charrefs=True)
        self.icones = []
        self.metas = {}
        self.titulo = None
        self.no_titulo = False
        self.base = None
        self.manifesto = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "").strip() for k, v in attrs}
        if tag == "link" and a.get("href"):
            rel = a.get("rel", "").lower().split()
            if "manifest" in rel and not self.manifesto:
                self.manifesto = a["href"]
            if "icon" in rel or "apple-touch-icon" in rel or "apple-touch-icon-precomposed" in rel:
                self.icones.append((rel, a["href"], a.get("sizes", "").lower(), a.get("type", "").lower(),
                                    a.get("media", "")))
        elif tag == "meta":
            chave = (a.get("property") or a.get("name") or "").lower()
            if chave in ("og:site_name", "application-name", "apple-mobile-web-app-title") and a.get("content"):
                self.metas.setdefault(chave, a["content"])
        elif tag == "title" and self.titulo is None:
            self.titulo = ""
            self.no_titulo = True
        elif tag == "base" and a.get("href") and not self.base:
            self.base = a["href"]

    def handle_endtag(self, tag):
        if tag == "title":
            self.no_titulo = False

    def handle_data(self, data):
        if self.no_titulo and len(self.titulo) < 400:
            self.titulo += data


def _maior_medida(sizes):
    medidas = [int(m) for m in re.findall(r"(\d+)\s*x\s*\d+", sizes or "")]
    return max(medidas) if medidas else None


def _nota_icone(medida, svg):
    if svg:
        return 520
    return min(medida, 512)


def nome_do_dominio(url):
    host = (urlparse(url).hostname or "").lower()
    if not host or re.fullmatch(r"[\d.]+", host) or ":" in host or "." not in host:
        return host
    if host.startswith("www."):
        host = host[4:]
    partes = [p for p in host.split(".") if p]
    if len(partes) >= 3 and partes[-2] in ("com", "net", "org", "gov", "edu", "co", "ac") and len(partes[-1]) == 2:
        partes = partes[:-2]
    elif len(partes) >= 2:
        partes = partes[:-1]
    return partes[-1] if partes else host


def _limpar_texto(t):
    return re.sub(r"\s+", " ", t or "").strip()


GENERICOS = {"caixa de entrada", "inbox", "home", "inicio", "dashboard", "painel", "nova guia", "new tab", "pagina inicial",
             "home page", "feed", "timeline", "entrada", "mensagens", "messages", "chats", "conversas"}


def _partes_titulo(titulo):
    t = _limpar_texto(titulo)
    if not t:
        return []
    partes = [p.strip() for p in re.split(r"\s+[-|–—·:•]\s+|\s+\|\s*", t) if p.strip()]
    return [re.sub(r"\s*\(\d+\)\s*", " ", p).strip() or p for p in partes]


def titulo_curto(titulo, url, pagina=False):
    marca = comparavel(nome_do_dominio(url)).replace(" ", "")
    partes = _partes_titulo(titulo)
    if not partes:
        nome = nome_do_dominio(url)
        return (nome[:1].upper() + nome[1:]) if nome else "Site"
    sem_email = [p for p in partes if "@" not in p] or partes
    com_marca = [p for p in sem_email if marca and marca in comparavel(p).replace(" ", "")]
    try:
        u = urlparse(url)
        if u.path in ("", "/") and not u.query and not u.fragment:
            pagina = False
    except ValueError:
        pass
    if pagina and len(partes) > 1:
        resto = [p for p in sem_email if p not in com_marca]
        if resto and comparavel(resto[0]) not in GENERICOS:
            return resto[0][:30]
    if com_marca:
        return com_marca[0][:30]
    if len(partes) > 1:
        curtas = [p for p in sem_email if len(p) <= 16 and re.search(r"[a-zA-Z]", p)]
        return (min(curtas, key=len) if curtas else min(sem_email, key=len))[:30]
    return partes[0][:30]


def titulo_do_site(leitor, url):
    for chave in ("og:site_name", "application-name", "apple-mobile-web-app-title"):
        t = _limpar_texto(leitor.metas.get(chave))
        if t:
            return t[:30]
    return titulo_curto(leitor.titulo, url)


def _decodificar_html(dados, tipo):
    m = re.search(r"charset=([\w-]+)", tipo or "", re.I) or re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", dados[:4096], re.I)
    cod = m.group(1) if m else "utf-8"
    if isinstance(cod, bytes):
        cod = cod.decode("ascii", "ignore")
    try:
        return dados.decode(cod, errors="replace")
    except LookupError:
        return dados.decode("utf-8", errors="replace")


def candidatos_icone(leitor, pagina, original, extras=()):
    lista = list(extras)
    base = urljoin(pagina, leitor.base) if leitor.base else pagina
    for rel, href, sizes, tipo, media in leitor.icones:
        url = urljoin(base, href)
        if not url.lower().startswith(("http://", "https://")):
            continue
        svg = tipo == "image/svg+xml" or href.lower().split("?")[0].endswith(".svg")
        if "apple-touch-icon" in rel or "apple-touch-icon-precomposed" in rel:
            medida = _maior_medida(sizes) or 180
        else:
            medida = _maior_medida(sizes) or (512 if sizes == "any" else 32)
        lista.append((_nota_icone(medida, svg) - (5 if media else 0), url))
    origem_pag = "%s://%s" % (urlparse(pagina).scheme, urlparse(pagina).netloc)
    origem_orig = "%s://%s" % (urlparse(original).scheme, urlparse(original).netloc)
    bonus = 600 if _host_base(original) != _host_base(pagina) else 0
    for origem, extra in ((origem_pag, 0), (origem_orig, bonus)):
        lista.append((180 + extra, origem + "/apple-touch-icon.png"))
        lista.append((31 + extra, origem + "/favicon.ico"))
    vistos = set()
    ordenados = []
    for nota, url in sorted(lista, key=lambda x: -x[0]):
        if url not in vistos:
            vistos.add(url)
            ordenados.append(url)
    return ordenados


def host_particular(url):
    host = (urlparse(url).hostname or "").lower()
    if not host or "." not in host or host.endswith((".local", ".lan", ".home", ".internal", ".localhost")):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved


def icone_pelo_google(url):
    if host_particular(url):
        return None
    p = urlparse(url)
    origem = "%s://%s" % (p.scheme, p.netloc)
    alvo = ("https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=256&url="
            + quote(origem, safe=""))
    try:
        dados, _, _ = baixar(alvo, 1500000, 6)
    except Exception:
        return None
    return imagem_boa(dados)


def dominio_da_marca(url):
    host = _host_base(url)
    partes = [p for p in host.split(".") if p]
    if len(partes) >= 3 and partes[-2] in ("com", "net", "org", "gov", "edu", "co", "ac") and len(partes[-1]) == 2:
        return ".".join(partes[-3:])
    return ".".join(partes[-2:]) if len(partes) >= 2 else host


_LOJA_TRAVA = threading.Lock()
_LOJA_ULTIMA = [0.0]
_LOJA_BLOQUEADA_ATE = [0.0]


PALAVRAS_SOLTAS = {"web", "online", "app", "site", "oficial", "official", "login", "entrar", "home", "inicio", "portal"}


def termo_da_loja(titulo):
    palavras = [p for p in comparavel(titulo).split() if p not in PALAVRAS_SOLTAS]
    return " ".join(palavras) or comparavel(titulo)


def _bate_nome(nome, procurado):
    n = comparavel(nome)
    return bool(procurado) and (n == procurado or n.startswith(procurado + " ") or (" " + procurado + " ") in (" " + n + " "))


def escolher_na_loja(resultados, marca, termo):
    melhor = (0, None)
    for i, r in enumerate(resultados):
        if not isinstance(r, dict) or not r.get("artworkUrl512"):
            continue
        vendedor = str(r.get("sellerUrl") or "")
        try:
            u = urlparse(vendedor)
            host = _host_base(vendedor)
        except ValueError:
            u, host = None, ""
        nome = comparavel(str(r.get("trackName") or ""))
        nota = 0
        if marca and (host == marca or host.endswith("." + marca)):
            nota += 4
            if u is not None and u.path.strip("/") == "" and not u.query:
                nota += 1
        if _bate_nome(nome, termo):
            nota += 2 if nota else (2 if nome == termo and len(termo) >= 4 else 0)
        nota -= i * 0.01
        if nota >= 2 and nota > melhor[0]:
            melhor = (nota, r)
    return melhor[1]


def icone_pela_loja(url, titulo):
    if host_particular(url) or not titulo:
        return None
    termo = termo_da_loja(titulo)
    alvo = "https://itunes.apple.com/search?" + urlencode({"term": termo, "entity": "software", "limit": 8, "country": "br"})
    with _LOJA_TRAVA:
        if time.time() < _LOJA_BLOQUEADA_ATE[0]:
            return None
        espera = _LOJA_ULTIMA[0] + 3.2 - time.time()
        if espera > 0:
            time.sleep(espera)
        _LOJA_ULTIMA[0] = time.time()
        try:
            dados, _, _ = baixar(alvo, 600000, 6)
            resultados = json.loads(dados.decode("utf-8-sig", "replace")).get("results") or []
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                _LOJA_BLOQUEADA_ATE[0] = time.time() + 90
            return None
        except Exception:
            return None
    escolhido = escolher_na_loja(resultados, dominio_da_marca(url), termo)
    if not escolhido:
        return None
    try:
        conteudo, _, _ = baixar(str(escolhido["artworkUrl512"]), 1500000, 6)
    except Exception:
        return None
    return imagem_boa(conteudo)


def icones_do_manifesto(leitor, pagina):
    if not leitor.manifesto:
        return []
    url = urljoin(pagina, leitor.manifesto)
    try:
        dados, final, _ = baixar(url, 200000, 6)
        m = json.loads(dados.decode("utf-8", "replace"))
    except Exception:
        return []
    lista = []
    for ic in (m.get("icons") or []) if isinstance(m, dict) else []:
        if not isinstance(ic, dict) or not ic.get("src"):
            continue
        propositos = str(ic.get("purpose") or "any").split()
        if "any" not in propositos:
            continue
        svg = "svg" in str(ic.get("type") or "") or str(ic["src"]).lower().split("?")[0].endswith(".svg")
        lista.append((_nota_icone(_maior_medida(str(ic.get("sizes") or "")) or 128, svg), urljoin(final, ic["src"])))
    return lista


def _host_base(url):
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def buscar_site(url, max_tentativas=6, loja=True):
    if not url.lower().startswith(("http://", "https://")):
        return {"titulo": None, "icone": None}
    leitor = LeitorSite()
    try:
        dados, final, tipo = baixar(url, 700000)
        try:
            leitor.feed(_decodificar_html(dados, tipo))
        except Exception:
            pass
    except urllib.error.HTTPError as e:
        final = e.geturl() or url
    except Exception:
        return {"titulo": None, "icone": None, "erro": True}
    melhor = (0, None)
    alternativo = None
    if _host_base(final) == _host_base(url):
        titulo = titulo_do_site(leitor, url)
        extras = icones_do_manifesto(leitor, final)
        melhor = _melhor_icone(candidatos_icone(leitor, final, url, extras), max_tentativas, melhor)
    else:
        titulo = titulo_do_subdominio(url)
        p = urlparse(url)
        origem = "%s://%s" % (p.scheme, p.netloc)
        melhor = _melhor_icone([origem + "/apple-touch-icon.png", origem + "/favicon.ico"], 2, melhor)
        if not melhor[1]:
            melhor = _melhor_icone(candidatos_icone(leitor, final, final), max_tentativas, melhor)
    loja = icone_pela_loja(url, titulo) if loja else None
    google = icone_pelo_google(url)
    for marca in (google, loja):
        medida_marca = (medida_imagem(marca) or 0) if marca else 0
        if marca and (melhor[0] < 128 or not melhor[1]) and medida_marca > melhor[0]:
            melhor = (medida_marca, marca)
            break
    for marca in (loja, google):
        if marca and marca != melhor[1] and (medida_imagem(marca) or 0) >= 64:
            alternativo = marca
            break
    return {"titulo": titulo, "icone": melhor[1], "alternativo": alternativo}


def _melhor_icone(urls, max_tentativas, melhor):
    for alvo in urls[:max_tentativas]:
        try:
            conteudo, _, _ = baixar(alvo, 1500000, 6)
        except Exception:
            continue
        bom = imagem_boa(conteudo)
        if not bom:
            continue
        medida = medida_imagem(bom) or 16
        if medida > melhor[0]:
            melhor = (medida, bom)
        if medida >= 180:
            break
    return melhor


def titulo_do_subdominio(url):
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    partes = host.split(".")
    if len(partes) >= 3 and partes[0] not in ("web", "app", "m", "open", "login", "accounts", "account", "auth", "sso", "my") \
            and not re.fullmatch(r"[\d]+", partes[0]):
        return partes[0][:1].upper() + partes[0][1:]
    nome = nome_do_dominio(url)
    return nome[:1].upper() + nome[1:]


def tem_esquema(url):
    return bool(re.match(r"^[a-zA-Z][\w+.-]*:", url)) and not re.match(r"^[\w.-]+:\d+(/|$)", url)


NAVEGADORES = [
    {"chave": "safari", "nome": "Safari", "familia": "safari", "mac": "Safari", "processo": "Safari",
     "exes": [], "linux": [], "bundle": "com.apple.safari", "progid": ()},
    {"chave": "chrome", "nome": "Google Chrome", "familia": "chromium", "mac": "Google Chrome", "processo": "Google Chrome",
     "exes": ["chrome.exe"], "linux": ["google-chrome", "google-chrome-stable", "com.google.chrome"], "bundle": "com.google.chrome",
     "progid": ("chromehtml", "chromehtm")},
    {"chave": "edge", "nome": "Microsoft Edge", "familia": "chromium", "mac": "Microsoft Edge", "processo": "Microsoft Edge",
     "exes": ["msedge.exe"], "linux": ["microsoft-edge", "microsoft-edge-stable", "com.microsoft.edge"], "bundle": "com.microsoft.edgemac",
     "progid": ("msedgehtm", "msedgehtml")},
    {"chave": "firefox", "nome": "Firefox", "familia": "firefox", "mac": "Firefox", "processo": "firefox",
     "exes": ["firefox.exe"], "linux": ["firefox", "firefox-esr", "org.mozilla.firefox"], "bundle": "org.mozilla.firefox",
     "progid": ("firefoxurl", "firefoxhtml")},
    {"chave": "brave", "nome": "Brave", "familia": "chromium", "mac": "Brave Browser", "processo": "Brave Browser",
     "exes": ["brave.exe"], "linux": ["brave-browser", "brave", "com.brave.browser"], "bundle": "com.brave.browser",
     "progid": ("bravehtml",)},
    {"chave": "arc", "nome": "Arc", "familia": "arc", "mac": "Arc", "processo": "Arc",
     "exes": ["arc.exe"], "linux": [], "bundle": "company.thebrowser.browser", "progid": ("archtml",)},
    {"chave": "vivaldi", "nome": "Vivaldi", "familia": "chromium", "mac": "Vivaldi", "processo": "Vivaldi",
     "exes": ["vivaldi.exe"], "linux": ["vivaldi-stable", "vivaldi"], "bundle": "com.vivaldi.vivaldi", "progid": ("vivaldihtm",)},
    {"chave": "opera", "nome": "Opera", "familia": "chromium", "mac": "Opera", "processo": "Opera",
     "exes": ["opera.exe", "launcher.exe"], "linux": ["opera"], "bundle": "com.operasoftware.opera", "progid": ("operastable", "opera")},
    {"chave": "chromium", "nome": "Chromium", "familia": "chromium", "mac": "Chromium", "processo": "Chromium",
     "exes": ["chromium.exe", "chrome.exe"], "linux": ["chromium", "chromium-browser", "org.chromium.chromium"], "bundle": "org.chromium.chromium",
     "progid": ("chromiumhtm",)},
]
POR_CHAVE = {n["chave"]: n for n in NAVEGADORES}
BUNDLES_NAVEGADORES = {n["bundle"] for n in NAVEGADORES} | {"com.google.chrome.beta", "com.google.chrome.canary", "com.apple.safaritechnologypreview",
                                                          "com.microsoft.edgemac.beta", "com.operasoftware.operagx", "app.zen-browser.zen"}
HOSTS_SEM_GRACA = ("accounts.", "login.", "auth.", "sso.", "signin.", "oauth.", "id.", "idp.", "myaccount.", "account.",
                   "passport.", "secure.", "localhost")
ESQUEMAS_SITE = ("http://", "https://")


def _casa(*partes):
    return os.path.join(os.path.expanduser("~"), *partes)


def pastas_de_dados():
    extra = os.environ.get("DECK_NAVEGADORES_DADOS")
    if extra:
        base = {}
        for chave in POR_CHAVE:
            p = os.path.join(extra, chave)
            if os.path.isdir(p):
                base[chave] = [p]
        return base
    if SISTEMA == "mac":
        ap = _casa("Library", "Application Support")
        return {
            "safari": [_casa("Library", "Safari")],
            "chrome": [os.path.join(ap, "Google", "Chrome")], "edge": [os.path.join(ap, "Microsoft Edge")],
            "brave": [os.path.join(ap, "BraveSoftware", "Brave-Browser")], "arc": [os.path.join(ap, "Arc", "User Data")],
            "vivaldi": [os.path.join(ap, "Vivaldi")], "opera": [os.path.join(ap, "com.operasoftware.Opera")],
            "chromium": [os.path.join(ap, "Chromium")], "firefox": [os.path.join(ap, "Firefox", "Profiles")],
        }
    if SISTEMA == "windows":
        local = os.environ.get("LOCALAPPDATA") or _casa("AppData", "Local")
        roaming = os.environ.get("APPDATA") or _casa("AppData", "Roaming")
        return {
            "chrome": [os.path.join(local, "Google", "Chrome", "User Data")],
            "edge": [os.path.join(local, "Microsoft", "Edge", "User Data")],
            "brave": [os.path.join(local, "BraveSoftware", "Brave-Browser", "User Data")],
            "vivaldi": [os.path.join(local, "Vivaldi", "User Data")],
            "opera": [os.path.join(roaming, "Opera Software", "Opera Stable"), os.path.join(roaming, "Opera Software", "Opera GX Stable")],
            "chromium": [os.path.join(local, "Chromium", "User Data")],
            "arc": [os.path.join(local, "Packages", "TheBrowserCompany.Arc_ttt1ap7aakyb4", "LocalCache", "Local", "Arc", "User Data")],
            "firefox": [os.path.join(roaming, "Mozilla", "Firefox", "Profiles")],
        }
    return {
        "chrome": [_casa(".config", "google-chrome"), _casa(".var", "app", "com.google.Chrome", "config", "google-chrome")],
        "chromium": [_casa(".config", "chromium"), _casa("snap", "chromium", "common", "chromium"),
                     _casa(".var", "app", "org.chromium.Chromium", "config", "chromium")],
        "edge": [_casa(".config", "microsoft-edge"), _casa(".var", "app", "com.microsoft.Edge", "config", "microsoft-edge")],
        "brave": [_casa(".config", "BraveSoftware", "Brave-Browser"),
                  _casa(".var", "app", "com.brave.Browser", "config", "BraveSoftware", "Brave-Browser")],
        "vivaldi": [_casa(".config", "vivaldi")], "opera": [_casa(".config", "opera")],
        "firefox": [_casa(".mozilla", "firefox"), _casa("snap", "firefox", "common", ".mozilla", "firefox"),
                    _casa(".var", "app", "org.mozilla.firefox", ".mozilla", "firefox")],
    }


def perfis_chromium(raiz):
    perfis = []
    if os.path.isfile(os.path.join(raiz, "History")):
        perfis.append(raiz)
    for nome in sorted(_listar(raiz)):
        if nome in ("System Profile", "Guest Profile"):
            continue
        p = os.path.join(raiz, nome)
        if os.path.isfile(os.path.join(p, "History")):
            perfis.append(p)
    return perfis


def perfis_firefox(raiz):
    return [os.path.join(raiz, n) for n in sorted(_listar(raiz)) if os.path.isfile(os.path.join(raiz, n, "places.sqlite"))]


class CopiaSqlite:
    def __init__(self, caminho):
        self.caminho = caminho
        self.pasta = None
        self.con = None

    def __enter__(self):
        self.pasta = tempfile.mkdtemp(prefix="deck-db-")
        destino = os.path.join(self.pasta, "copia.sqlite")
        shutil.copyfile(self.caminho, destino)
        for sufixo in ("-wal", "-journal", "-shm"):
            if os.path.exists(self.caminho + sufixo):
                try:
                    shutil.copyfile(self.caminho + sufixo, destino + sufixo)
                except OSError:
                    pass
        self.con = sqlite3.connect(destino, timeout=2)
        return self.con

    def __exit__(self, *args):
        try:
            if self.con:
                self.con.close()
        finally:
            shutil.rmtree(self.pasta, ignore_errors=True)
        return False


def _consultar(caminho, sql, args=()):
    try:
        with CopiaSqlite(caminho) as con:
            return con.execute(sql, args).fetchall()
    except (OSError, sqlite3.Error, ValueError):
        return []


def _host(url):
    try:
        h = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def _raiz(url):
    p = urlparse(url)
    return "%s://%s" % (p.scheme, p.netloc.lower())


def _site_vale(url):
    if not url or not url.lower().startswith(ESQUEMAS_SITE):
        return False
    h = _host(url)
    if not h or h.startswith(HOSTS_SEM_GRACA) or h in ("newtab", "new-tab-page"):
        return False
    return True


def _chrome_tempo(v):
    try:
        return int(v) / 1e6 - 11644473600
    except (TypeError, ValueError):
        return 0


def historico_chromium(perfil):
    linhas = _consultar(os.path.join(perfil, "History"),
                        "SELECT url, title, visit_count, last_visit_time FROM urls WHERE hidden = 0 AND visit_count > 0 "
                        "ORDER BY visit_count DESC LIMIT 3000")
    return [(u, t or "", int(v or 0), _chrome_tempo(q)) for u, t, v, q in linhas]


def favoritos_chromium(perfil):
    try:
        with open(os.path.join(perfil, "Bookmarks"), encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return []
    saida = []

    def andar(no):
        if not isinstance(no, dict):
            return
        if no.get("type") == "url":
            saida.append((no.get("url", ""), no.get("name", "")))
        for filho in no.get("children") or []:
            andar(filho)

    raizes = dados.get("roots") if isinstance(dados, dict) else None
    if isinstance(raizes, dict):
        for chave in ("bookmark_bar", "other", "synced"):
            andar(raizes.get(chave))
    return saida


def historico_firefox(perfil):
    linhas = _consultar(os.path.join(perfil, "places.sqlite"),
                        "SELECT url, title, visit_count, last_visit_date FROM moz_places WHERE hidden = 0 AND visit_count > 0 "
                        "ORDER BY visit_count DESC LIMIT 3000")
    return [(u, t or "", int(v or 0), (q or 0) / 1e6) for u, t, v, q in linhas]


def favoritos_firefox(perfil):
    linhas = _consultar(os.path.join(perfil, "places.sqlite"),
                        "SELECT p.url, b.title FROM moz_bookmarks b JOIN moz_places p ON p.id = b.fk WHERE b.type = 1 "
                        "AND b.parent NOT IN (SELECT id FROM moz_bookmarks WHERE parent = "
                        "(SELECT id FROM moz_bookmarks WHERE guid = 'tags________')) ORDER BY b.parent, b.position")
    return [(u, t or "") for u, t in linhas]


def historico_safari(pasta):
    linhas = _consultar(os.path.join(pasta, "History.db"),
                        "SELECT i.url, i.visit_count, (SELECT v.title FROM history_visits v WHERE v.history_item = i.id "
                        "AND v.title IS NOT NULL AND v.title != '' ORDER BY v.visit_time DESC LIMIT 1), "
                        "(SELECT MAX(v.visit_time) FROM history_visits v WHERE v.history_item = i.id) "
                        "FROM history_items i WHERE i.visit_count > 0 ORDER BY i.visit_count DESC LIMIT 3000")
    return [(u, t or "", int(v or 0), (q or 0) + 978307200) for u, v, t, q in linhas]


def favoritos_safari(pasta):
    try:
        with open(os.path.join(pasta, "Bookmarks.plist"), "rb") as f:
            dados = plistlib.load(f)
    except Exception:
        return []
    saida = []

    def andar(no):
        if not isinstance(no, dict):
            return
        if no.get("WebBookmarkType") == "WebBookmarkTypeLeaf":
            titulo = (no.get("URIDictionary") or {}).get("title") or ""
            saida.append((no.get("URLString", ""), titulo))
            return
        if no.get("Title") == "com.apple.ReadingList":
            return
        for filho in no.get("Children") or []:
            andar(filho)

    andar(dados)
    return saida


def favicons_chromium(perfil, hosts):
    arq = os.path.join(perfil, "Favicons")
    if not os.path.isfile(arq):
        return {}
    saida = {}
    try:
        with CopiaSqlite(arq) as con:
            for h in hosts:
                melhor = None
                for padrao in ("https://%s/%%" % h, "https://www.%s/%%" % h, "http://%s/%%" % h, "http://www.%s/%%" % h):
                    for dados, largura in con.execute(
                            "SELECT b.image_data, b.width FROM icon_mapping m JOIN favicon_bitmaps b ON b.icon_id = m.icon_id "
                            "WHERE m.page_url LIKE ? ORDER BY b.width DESC LIMIT 3", (padrao,)):
                        if dados and tipo_imagem(bytes(dados)) and (melhor is None or (largura or 0) > melhor[0]):
                            melhor = (largura or 0, bytes(dados))
                    if melhor and melhor[0] >= 32:
                        break
                if melhor:
                    saida[h] = melhor[1]
    except (OSError, sqlite3.Error, ValueError):
        return saida
    return saida


def favicons_firefox(perfil, hosts):
    arq = os.path.join(perfil, "favicons.sqlite")
    if not os.path.isfile(arq):
        return {}
    saida = {}
    try:
        with CopiaSqlite(arq) as con:
            for h in hosts:
                melhor = None
                for padrao in ("https://%s/%%" % h, "https://www.%s/%%" % h, "http://%s/%%" % h, "http://www.%s/%%" % h):
                    for dados, largura in con.execute(
                            "SELECT i.data, i.width FROM moz_icons i JOIN moz_icons_to_pages ip ON ip.icon_id = i.id "
                            "JOIN moz_pages_w_icons p ON p.id = ip.page_id WHERE p.page_url LIKE ? ORDER BY i.width DESC LIMIT 3",
                            (padrao,)):
                        if dados and tipo_imagem(bytes(dados)) and (melhor is None or (largura or 0) > melhor[0]):
                            melhor = (largura or 0, bytes(dados))
                    for dados, largura in con.execute(
                            "SELECT data, width FROM moz_icons WHERE root = 1 AND icon_url LIKE ? ORDER BY width DESC LIMIT 2",
                            (padrao,)):
                        if dados and tipo_imagem(bytes(dados)) and (melhor is None or (largura or 0) > melhor[0]):
                            melhor = (largura or 0, bytes(dados))
                    if melhor and melhor[0] >= 32:
                        break
                if melhor:
                    saida[h] = melhor[1]
    except (OSError, sqlite3.Error, ValueError):
        return saida
    return saida


def _fontes():
    fontes = []
    for chave, raizes in pastas_de_dados().items():
        familia = POR_CHAVE[chave]["familia"]
        for raiz in raizes:
            if not os.path.isdir(raiz):
                continue
            if familia == "firefox":
                fontes += [(chave, "firefox", p) for p in perfis_firefox(raiz)]
            elif familia == "safari":
                fontes.append((chave, "safari", raiz))
            else:
                fontes += [(chave, "chromium", p) for p in perfis_chromium(raiz)]
    return fontes


def _chave_url(url):
    try:
        p = urlparse(url)
    except ValueError:
        return url
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    caminho = (p.path or "").rstrip("/")
    return host + caminho + (("?" + p.query) if p.query else "")


def coletar_sites(primeiro=None, limite=48):
    fontes = _fontes()
    if primeiro:
        fontes.sort(key=lambda f: 0 if f[0] == primeiro else 1)
    favoritos, vistos_fav = [], set()
    grupos = {}
    for chave, familia, perfil in fontes:
        nome_nav = POR_CHAVE[chave]["nome"]
        if familia == "firefox":
            hist, favs = historico_firefox(perfil), favoritos_firefox(perfil)
        elif familia == "safari":
            hist, favs = historico_safari(perfil), favoritos_safari(perfil)
        else:
            hist, favs = historico_chromium(perfil), favoritos_chromium(perfil)
        for url, titulo in favs:
            if not _site_vale(url):
                continue
            k = _chave_url(url)
            if k in vistos_fav:
                continue
            vistos_fav.add(k)
            favoritos.append({"url": url.rstrip("/") if not urlparse(url).query else url,
                              "titulo": titulo_curto(titulo, url, pagina=True) if titulo else titulo_curto("", url),
                              "navegador": nome_nav})
        for url, titulo, visitas, quando in hist:
            if not _site_vale(url):
                continue
            h = _host(url)
            g = grupos.setdefault(h, {"visitas": 0, "quando": 0, "melhor": None, "raiz": None, "navegador": nome_nav})
            g["visitas"] += visitas
            g["quando"] = max(g["quando"], quando or 0)
            if g["melhor"] is None or visitas > g["melhor"][0]:
                g["melhor"] = (visitas, url, titulo)
            if urlparse(url).path in ("", "/") and not urlparse(url).query and titulo and g["raiz"] is None:
                g["raiz"] = (url, titulo)
    visitados = []
    for h, g in sorted(grupos.items(), key=lambda kv: (-kv[1]["visitas"], -kv[1]["quando"])):
        _, url, titulo = g["melhor"]
        visitados.append({"url": _raiz(url), "titulo": _titulo_do_grupo(g, url, titulo), "navegador": g["navegador"],
                          "visitas": g["visitas"]})
        if len(visitados) >= limite:
            break
    return {"favoritos": favoritos[:limite], "visitados": visitados}


def _titulo_do_grupo(g, url, titulo):
    if g["raiz"]:
        return titulo_curto(g["raiz"][1], g["raiz"][0])
    marca = comparavel(nome_do_dominio(url)).replace(" ", "")
    partes = _partes_titulo(titulo)
    for p in partes:
        if marca and marca in comparavel(p).replace(" ", ""):
            return p[:30]
    curtas = [p for p in partes if len(p) <= 16 and "@" not in p and re.search(r"[a-zA-Z]", p)]
    if len(partes) > 1 and curtas:
        return min(curtas, key=len)
    return titulo_do_subdominio(url)


def icones_do_navegador(hosts):
    pendentes = [h for h in dict.fromkeys(hosts) if h]
    saida = {}
    for chave, familia, perfil in _fontes():
        if not pendentes:
            break
        if familia == "firefox":
            achados = favicons_firefox(perfil, pendentes)
        elif familia == "chromium":
            achados = favicons_chromium(perfil, pendentes)
        else:
            achados = {}
        saida.update(achados)
        pendentes = [h for h in pendentes if h not in saida]
    return saida


def icone_do_navegador(url):
    h = _host(url)
    if not h:
        return None
    return icones_do_navegador([h]).get(h)


def _abas_sep():
    return "\x1f", "\x1e"


def script_abas(navegadores):
    linhas = ["set sep to (ASCII character 31)", "set fim to (ASCII character 30)", 'set saida to ""']
    for n in navegadores:
        app = n["mac"]
        familia = n["familia"]
        if familia == "firefox":
            continue
        titulo = "name of t" if familia == "safari" else "title of t"
        linhas += [
            "try",
            "\ttell application %s" % as_texto(app),
            "\t\trepeat with w in windows",
            "\t\t\tset wid to id of w",
            "\t\t\tset n to 0",
            "\t\t\trepeat with t in tabs of w",
            "\t\t\t\tset n to n + 1",
            "\t\t\t\ttry",
            "\t\t\t\t\tset u to URL of t",
            "\t\t\t\t\tif u is missing value then set u to \"\"",
            "\t\t\t\t\tset tt to %s" % titulo,
            "\t\t\t\t\tif tt is missing value then set tt to \"\"",
            "\t\t\t\t\tset saida to saida & %s & sep & wid & sep & n & sep & u & sep & tt & fim" % as_texto(n["chave"]),
            "\t\t\t\tend try",
            "\t\t\tend repeat",
            "\t\tend repeat",
            "\tend tell",
            "end try",
        ]
    linhas.append("return saida")
    return "\n".join(linhas)


def ler_abas(saida):
    sep, fim = _abas_sep()
    abas = []
    for linha in (saida or "").split(fim):
        partes = linha.split(sep)
        if len(partes) < 5:
            continue
        chave, wid, n, url, titulo = partes[0], partes[1], partes[2], partes[3], sep.join(partes[4:])
        nav = POR_CHAVE.get(chave.strip())
        if not nav or not url.strip():
            continue
        try:
            abas.append({"navegador": nav["nome"], "chave": chave.strip(), "janela": int(wid), "indice": int(n),
                         "url": url.strip(), "titulo": titulo.strip()})
        except ValueError:
            continue
    return abas


def script_focar(aba):
    nav = POR_CHAVE[aba["chave"]]
    app = as_texto(nav["mac"])
    if nav["familia"] == "safari":
        meio = ["\tset w to window id %d" % aba["janela"], "\tset current tab of w to tab %d of w" % aba["indice"]]
    elif nav["familia"] == "arc":
        meio = ["\ttell window id %d" % aba["janela"], "\t\tselect tab %d" % aba["indice"], "\tend tell",
                "\tset w to window id %d" % aba["janela"]]
    else:
        meio = ["\tset w to window id %d" % aba["janela"], "\tset active tab index of w to %d" % aba["indice"]]
    return "\n".join(["tell application %s" % app] + meio + ["\ttry", "\t\tset index of w to 1", "\tend try", "\tactivate", "end tell"])


def escolher_aba(abas, url):
    alvo = _chave_url(url)
    host_alvo = alvo.split("/")[0].split("?")[0]
    exatas, prefixo, mesmo_host = [], [], []
    for a in abas:
        k = _chave_url(a["url"])
        if k == alvo:
            exatas.append(a)
        elif k.startswith(alvo + "/") or (alvo and k.startswith(alvo + "?")) or (alvo and k.startswith(alvo + "#")):
            prefixo.append(a)
        elif k.split("/")[0].split("?")[0] == host_alvo and host_alvo == alvo:
            mesmo_host.append(a)
    for grupo in (exatas, prefixo, mesmo_host):
        if grupo:
            return min(grupo, key=lambda a: len(a["url"]))
    return None


def chave_do_navegador(nome):
    if not nome:
        return None
    n = comparavel(nome)
    for nav in NAVEGADORES:
        if n in (comparavel(nav["nome"]), comparavel(nav["mac"]), comparavel(nav["chave"])):
            return nav["chave"]
    for nav in NAVEGADORES:
        if n and (n in comparavel(nav["nome"]) or n in comparavel(nav["mac"])):
            return nav["chave"]
    return None


def pedido_da_acao(acao):
    if not acao:
        return None
    if acao["tipo"] == "app":
        return ("app",) + tuple(acao["apps"])
    if acao["tipo"] == "link" and acao["url"].lower().startswith(("http://", "https://")):
        return ("site", acao["url"])
    return None


def texto_do_pedido(pedido):
    if not pedido:
        return None
    if pedido[0] == "app":
        return "app:" + "\n".join(pedido[1:])
    return "site:" + pedido[1]


class Icones:
    LADO = 256

    def __init__(self, sistema, pasta, avisar=None):
        self.sistema = sistema
        self.pasta = pasta
        self.avisar = avisar or (lambda: None)
        self.trava = threading.Lock()
        self.trabalho = threading.Event()
        self.geracao = 0
        self.indice = {}
        self.falhas = {}
        self.alvos = {}
        self.fila = []
        self.ocupados = set()
        self.titulos = {}
        self.catalogo_lista = None
        self.catalogo_quando = 0.0
        self.catalogo_pedido = False
        self.catalogo_montando = False
        self.sites_lista = None
        self.sites_quando = 0.0
        self.sites_pedido = False
        self.sites_montando = False
        self.pequenos = {}
        self.fila_lenta = []
        self.trabalho_lento = threading.Event()
        self._ler_indice()
        threading.Thread(target=self._laco, daemon=True).start()
        threading.Thread(target=self._laco_lento, daemon=True).start()

    def _arq_indice(self):
        return os.path.join(self.pasta, "indice.json")

    def _ler_indice(self):
        try:
            with open(self._arq_indice(), encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, ValueError):
            return
        if isinstance(dados, dict):
            for chave, arq in dados.items():
                if chave.startswith("titulo|") and isinstance(arq, str) and arq:
                    self.indice[chave] = arq[:60]
                elif isinstance(arq, str) and re.fullmatch(r"[0-9a-f]{20}\.(png|svg|ico|jpg|gif|webp)", arq) \
                        and os.path.isfile(os.path.join(self.pasta, arq)):
                    self.indice[chave] = arq
                    if chave.startswith("fav|"):
                        self.pequenos[chave] = time.time()

    def _gravar_indice(self):
        with self.trava:
            texto = json.dumps(self.indice, ensure_ascii=False, indent=0)
        try:
            gravar_atomico(self._arq_indice(), texto)
        except OSError:
            pass

    def guardar(self, chave, dados):
        ext = tipo_imagem(dados)
        if not ext:
            return None
        nome = hashlib.sha1(dados).hexdigest()[:20] + ext
        caminho = os.path.join(self.pasta, nome)
        if not os.path.isfile(caminho):
            try:
                with open(caminho + ".tmp", "wb") as f:
                    f.write(dados)
                os.replace(caminho + ".tmp", caminho)
            except OSError:
                return None
        with self.trava:
            self.indice[chave] = nome
            self.falhas.pop(chave, None)
        return nome

    def chave_app(self, alvo):
        sinal = 0
        for c in (os.path.join(alvo, "Contents", "Info.plist"), alvo):
            try:
                sinal = int(os.stat(c).st_mtime)
                break
            except (OSError, ValueError):
                continue
        return "app|%s|%s|%d" % (SISTEMA, alvo, sinal)

    def _enfileirar(self, pedido):
        if pedido not in self.ocupados and pedido not in self.fila:
            self.fila.append(pedido)
            self.trabalho.set()

    def consultar(self, pedido):
        with self.trava:
            r = self.alvos.get(pedido)
            if r is None:
                self._enfileirar(pedido)
                return "pendente", None
            chave, quando = r
            if chave and chave in self.indice:
                return "pronto", self.indice[chave]
            if time.time() - quando > (600 if pedido[0] == "site" else 90):
                self._enfileirar(pedido)
            return ("pendente" if pedido in self.fila or pedido in self.ocupados else "sem"), None

    def arquivo(self, chave):
        with self.trava:
            return self.indice.get(chave)

    def _com_reserva(self, url, info):
        if info.get("icone"):
            return info
        try:
            reserva = icone_do_navegador(url)
        except Exception:
            reserva = None
        if reserva:
            info = dict(info)
            info["icone"] = reserva
        return info

    def _guardar_alternativo(self, url, info):
        chave = "alt|" + url
        if info.get("alternativo"):
            return self.guardar(chave, info["alternativo"])
        with self.trava:
            self.indice.pop(chave, None)
            self.falhas[chave] = time.time()
        return None

    def _guardar_titulo(self, url, info):
        with self.trava:
            if info.get("titulo"):
                self.indice["titulo|" + url] = info["titulo"]
                self.titulos[url] = info["titulo"]

    def _fresco(self, arquivo, dias=7):
        try:
            return time.time() - os.stat(os.path.join(self.pasta, arquivo)).st_mtime < dias * 86400
        except OSError:
            return False

    def _reaproveitar_site(self, url):
        chave = "site|" + url
        with self.trava:
            atual = self.indice.get(chave)
            alt = self.indice.get("alt|" + url)
            alt_recente = self._recente("alt|" + url)
        if not atual or not self._fresco(atual):
            return False
        if not alt and not alt_recente:
            self._pedir_oficial(url)
        return True

    def _pedir_oficial(self, url):
        with self.trava:
            if url not in self.fila_lenta:
                self.fila_lenta.append(url)
                self.trabalho_lento.set()

    def _completar_oficial(self, url):
        chave = "site|" + url
        with self.trava:
            titulo = self.indice.get("titulo|" + url)
            atual = self.indice.get(chave)
            alt = self.indice.get("alt|" + url)
            self.falhas["alt|" + url] = time.time()
        marca = icone_pela_loja(url, titulo or titulo_do_subdominio(url)) or icone_pelo_google(url)
        if not marca:
            return
        medida = medida_imagem(marca) or 0
        nome = hashlib.sha1(marca).hexdigest()[:20] + (tipo_imagem(marca) or "")
        if nome in (atual, alt):
            with self.trava:
                self.falhas.pop("alt|" + url, None)
            return
        if not atual:
            if not self.guardar(chave, marca):
                return
        elif medida >= 64:
            if not self.guardar("alt|" + url, marca):
                return
        else:
            return
        with self.trava:
            self.geracao += 1
        self._gravar_indice()
        self.avisar()

    def _laco_lento(self):
        while True:
            self.trabalho_lento.wait()
            with self.trava:
                url = self.fila_lenta.pop(0) if self.fila_lenta else None
                if not self.fila_lenta:
                    self.trabalho_lento.clear()
            if not url:
                continue
            try:
                self._completar_oficial(url)
            except Exception:
                log(vermelho(tr("Erro ao buscar o ícone oficial de %s:\n%s") % (url, traceback.format_exc())))

    def site_agora(self, url):
        info = self._com_reserva(url, buscar_site(url, loja=False))
        chave = "site|" + url
        nome = self.guardar(chave, info["icone"]) if info.get("icone") else None
        alternativo = self._guardar_alternativo(url, info)
        self._guardar_titulo(url, info)
        with self.trava:
            if not nome:
                self.falhas[chave] = time.time()
            self.alvos[("site", url)] = (chave, time.time())
            self.geracao += 1
        self._gravar_indice()
        self.avisar()
        if nome and not info.get("erro"):
            self._pedir_oficial(url)
        titulo = info.get("titulo") or titulo_do_subdominio(url)
        return {"titulo": titulo, "arquivo": nome, "alternativo": alternativo, "falhou": bool(info.get("erro"))}

    def catalogo(self):
        with self.trava:
            velho = time.time() - self.catalogo_quando > 120
            if (self.catalogo_lista is None or velho) and not self.catalogo_pedido and not self.catalogo_montando:
                self.catalogo_pedido = True
                self.trabalho.set()
            lista = []
            for e in self.catalogo_lista or []:
                arq = self.indice.get(e.get("chave")) if e.get("chave") else None
                lista.append({"nome": e["nome"], "valor": e["valor"], "arquivo": arq})
            carregando = self.catalogo_lista is None or self.catalogo_pedido or self.catalogo_montando
        return lista, carregando

    def _laco(self):
        while True:
            self.trabalho.wait()
            with self.trava:
                lote = self.fila[:]
                self.fila = []
                self.ocupados = set(lote)
                quer_catalogo = self.catalogo_pedido
                if quer_catalogo:
                    self.catalogo_pedido = False
                    self.catalogo_montando = True
                quer_sites = self.sites_pedido
                if quer_sites:
                    self.sites_pedido = False
                    self.sites_montando = True
                self.trabalho.clear()
            try:
                if quer_catalogo:
                    self._montar_catalogo()
                if quer_sites:
                    self._montar_sites()
                apps = [p for p in lote if p[0] == "app"]
                sites = [p for p in lote if p[0] == "site"]
                if apps:
                    self._processar_apps(apps)
                if sites:
                    with ThreadPoolExecutor(max_workers=4) as grupo:
                        list(grupo.map(self._processar_site, sites))
            except Exception:
                log(vermelho(tr("Erro ao buscar ícones:\n") + traceback.format_exc()))
            with self.trava:
                self.ocupados = set()
                self.catalogo_montando = False
                self.sites_montando = False
                self.geracao += 1
            self._gravar_indice()
            self.avisar()

    def _recente(self, chave):
        quando = self.falhas.get(chave)
        return quando is not None and time.time() - quando < 300

    def _extrair(self, pendentes):
        if not pendentes:
            return
        try:
            resultados = self.sistema.gerar_icones(list(pendentes), self.LADO)
        except Exception:
            resultados = {}
        for alvo, chave in pendentes.items():
            dados = resultados.get(alvo)
            if not dados or not self.guardar(chave, dados):
                with self.trava:
                    self.falhas[chave] = time.time()

    def _processar_apps(self, pedidos):
        pendentes = {}
        for p in pedidos:
            try:
                alvo = self.sistema.alvo_icone(list(p[1:]))
            except Exception:
                alvo = None
            chave = self.chave_app(alvo) if alvo else None
            with self.trava:
                self.alvos[p] = (chave, time.time())
                if chave and chave not in self.indice and not self._recente(chave):
                    pendentes[alvo] = chave
        self._extrair(pendentes)

    def sites(self, padrao=None):
        with self.trava:
            velho = time.time() - self.sites_quando > 90
            if (self.sites_lista is None or velho) and not self.sites_pedido and not self.sites_montando:
                self.sites_pedido = True
                self.sites_padrao = padrao
                self.trabalho.set()
            lista = self.sites_lista
            carregando = self.sites_lista is None or self.sites_pedido or self.sites_montando
        return lista, carregando

    def img_de_site(self, url):
        with self.trava:
            for base in (url, url.rstrip("/"), _raiz(url), _raiz(url) + "/"):
                arq = self.indice.get("site|" + base)
                if arq:
                    alt = self.indice.get("alt|" + base)
                    return "/auto/" + arq, base in (url, url.rstrip("/")), ("/auto/" + alt) if alt else None
            arq = self.indice.get("fav|" + _host(url))
            return ("/auto/" + arq) if arq else None, False, None

    def pedir_sites(self, urls, limite=20):
        with self.trava:
            n = 0
            for u in urls:
                if n >= limite:
                    break
                if ("site", u) in self.alvos or "site|" + u in self.indice:
                    continue
                self._enfileirar(("site", u))
                n += 1

    def _montar_sites(self):
        try:
            dados = coletar_sites(getattr(self, "sites_padrao", None))
        except Exception:
            log(vermelho(tr("Erro ao ler favoritos/histórico:\n") + traceback.format_exc()))
            dados = {"favoritos": [], "visitados": []}
        with self.trava:
            self.sites_lista = dados
            self.sites_quando = time.time()
            self.geracao += 1
        self.avisar()
        hosts = []
        for grupo in (dados["favoritos"], dados["visitados"]):
            for item in grupo:
                h = _host(item["url"])
                if h and "fav|" + h not in self.indice and "fav|" + h not in self.pequenos:
                    hosts.append(h)
        if hosts:
            try:
                achados = icones_do_navegador(hosts[:120])
            except Exception:
                achados = {}
            for h in hosts[:120]:
                self.pequenos["fav|" + h] = time.time()
                if achados.get(h):
                    self.guardar("fav|" + h, achados[h])
            with self.trava:
                self.geracao += 1
            self.avisar()

    def _processar_site(self, pedido):
        url = pedido[1]
        chave = "site|" + url
        if self._reaproveitar_site(url):
            with self.trava:
                self.alvos[pedido] = (chave, time.time())
                self.geracao += 1
            self.avisar()
            return
        try:
            info = self._com_reserva(url, buscar_site(url, loja=False))
        except Exception:
            info = {"icone": None}
        nome = self.guardar(chave, info["icone"]) if info.get("icone") else None
        self._guardar_alternativo(url, info)
        self._guardar_titulo(url, info)
        with self.trava:
            if not nome:
                self.falhas[chave] = time.time()
            self.alvos[pedido] = (chave, time.time())
            self.geracao += 1
        self.avisar()
        if nome and not info.get("erro"):
            self._pedir_oficial(url)

    def _montar_catalogo(self):
        try:
            entradas = self.sistema.catalogo()
        except Exception:
            log(vermelho(tr("Erro ao listar os apps:\n") + traceback.format_exc()))
            entradas = []
        pendentes = {}
        agora = time.time()
        lista = []
        for e in entradas:
            item = {"nome": e["nome"], "valor": e["valor"], "chave": None}
            alvo = e.get("alvo")
            if alvo:
                item["chave"] = self.chave_app(alvo)
                with self.trava:
                    self.alvos[("app", e["valor"])] = (item["chave"], agora)
                    if item["chave"] not in self.indice and not self._recente(item["chave"]):
                        pendentes[alvo] = item["chave"]
            lista.append(item)
        lista.sort(key=lambda x: comparavel(x["nome"]))
        with self.trava:
            self.catalogo_lista = lista
            self.catalogo_quando = time.time()
            self.geracao += 1
        self.avisar()
        self._extrair(pendentes)


class Player:
    def __init__(self, sistema, pasta):
        self.sistema = sistema
        self.pasta = pasta
        self._trava = threading.Lock()
        self._bruto = None
        self._quando = 0.0
        self._medido = 0.0
        self._chave_capa = ""
        self._capa = None
        self._capas = {}
        self._tentativas = {}
        self._baixando = set()

    def _guardar_capa(self, dados):
        ext = tipo_imagem(dados)
        if ext not in (".png", ".jpg", ".gif", ".webp") or len(dados) > 6 * 1024 * 1024:
            return None
        os.makedirs(self.pasta, exist_ok=True)
        nome = hashlib.sha1(dados).hexdigest()[:20] + ext
        caminho = os.path.join(self.pasta, nome)
        if os.path.exists(caminho):
            try:
                os.utime(caminho)
            except OSError:
                pass
        else:
            gravar_atomico(caminho, dados)
            self._limpar()
        return nome

    def _limpar(self):
        try:
            arquivos = [os.path.join(self.pasta, n) for n in os.listdir(self.pasta)
                        if re.fullmatch(r"[0-9a-f]{20}\.(png|jpg|gif|webp)", n)]
        except OSError:
            return
        arquivos.sort(key=lambda c: os.path.getmtime(c), reverse=True)
        for velho in arquivos[40:]:
            try:
                os.remove(velho)
            except OSError:
                pass

    def _lembrar(self, chave, nome, atual=True):
        self._capas.pop(chave, None)
        self._capas[chave] = nome
        while len(self._capas) > 30:
            self._capas.pop(next(iter(self._capas)))
        self._tentativas.pop(chave, None)
        if atual:
            self._chave_capa, self._capa = chave, nome

    def _falhou(self, chave, limite, atual):
        n = self._tentativas.get(chave, 0) + 1
        self._tentativas = {chave: n}
        if n >= limite:
            self._lembrar(chave, None, atual)

    def _baixar_capa(self, chave, urls):
        nome = None
        for url in urls:
            try:
                nome = self._guardar_capa(baixar(url, 6 * 1024 * 1024, tempo=8)[0])
            except Exception:
                nome = None
            if nome:
                break
        with self._trava:
            self._baixando.discard(chave)
            atual = bool(self._bruto) and self._bruto.get("chave") == chave
            if nome:
                self._lembrar(chave, nome, atual)
            else:
                self._falhou(chave, 3, atual)

    def _capa_de(self, r, temp):
        chave = r.get("chave") or ""
        if chave in self._capas:
            nome = self._capas[chave]
            if nome is None or os.path.exists(os.path.join(self.pasta, nome)):
                self._chave_capa, self._capa = chave, nome
                return
            del self._capas[chave]
        self._chave_capa, self._capa = "", None
        nome = None
        if r.get("capa") is True and os.path.isfile(temp):
            try:
                with open(temp, "rb") as f:
                    nome = self._guardar_capa(f.read())
            except OSError:
                nome = None
        elif r.get("capaArquivo"):
            try:
                with open(r["capaArquivo"], "rb") as f:
                    nome = self._guardar_capa(f.read(6 * 1024 * 1024 + 1))
            except OSError:
                nome = None
        elif r.get("capaUrl"):
            urls = [u for u in (r["capaUrl"] if isinstance(r["capaUrl"], list) else [r["capaUrl"]])
                    if isinstance(u, str) and u.startswith(("http://", "https://"))]
            if not urls:
                self._falhou(chave, 4, True)
                return
            if chave not in self._baixando:
                self._baixando.add(chave)
                threading.Thread(target=self._baixar_capa, args=(chave, urls), daemon=True).start()
            return
        if nome:
            self._lembrar(chave, nome)
            return
        self._falhou(chave, 4, True)

    def estado(self, idade=0.8):
        with self._trava:
            agora = time.time()
            if self._bruto is None or agora - self._quando >= idade:
                temp = os.path.join(self.pasta, "capa-nova.tmp")
                try:
                    os.makedirs(self.pasta, exist_ok=True)
                    if os.path.exists(temp):
                        os.remove(temp)
                except OSError:
                    pass
                try:
                    r = self.sistema.tocando(self._chave_capa, temp) or {}
                except ErroAcao as e:
                    r = {"tem": False, "motivo": str(e)}
                except Exception:
                    log(vermelho(tr("Erro ao ler o que está tocando:\n") + traceback.format_exc()))
                    r = {"tem": False}
                if not isinstance(r, dict):
                    r = {"tem": False}
                agora = time.time()
                if r.get("tem"):
                    self._capa_de(r, temp)
                self._bruto = r
                self._quando = agora
                quando = r.get("quando")
                self._medido = quando if isinstance(quando, (int, float)) and abs(agora - quando) < 86400 * 400 else agora - float(r.get("idade") or 0)
            return self._publico(time.time())

    def atual(self, idade=1.5):
        self.estado(idade)
        with self._trava:
            return dict(self._bruto or {})

    def esquecer(self):
        with self._trava:
            self._quando = 0.0

    def _publico(self, agora):
        r = self._bruto or {}
        if not r.get("tem"):
            return {"tem": False, "motivo": r.get("motivo")}
        duracao = r.get("duracao")
        duracao = float(duracao) if isinstance(duracao, (int, float)) and duracao > 0 else None
        posicao = r.get("posicao")
        posicao = float(posicao) if isinstance(posicao, (int, float)) and posicao >= 0 else None
        tocando = bool(r.get("tocando"))
        if posicao is not None and tocando:
            posicao += max(0.0, agora - self._medido) * (float(r.get("taxa")) if isinstance(r.get("taxa"), (int, float)) and r.get("taxa") > 0 else 1.0)
        if posicao is not None and duracao:
            posicao = min(posicao, duracao)
        pode = dict(r.get("pode") or {})
        pode.setdefault("proxima", True)
        pode.setdefault("anterior", True)
        pode.setdefault("posicao", r.get("appId") in ("com.spotify.client", "com.apple.Music"))
        if not duracao:
            pode["posicao"] = False
        return {
            "tem": True, "tocando": tocando, "titulo": str(r.get("titulo") or "")[:200],
            "artista": str(r.get("artista") or "")[:200], "album": str(r.get("album") or "")[:200],
            "app": str(r.get("app") or "")[:60], "duracao": duracao,
            "posicao": round(posicao, 2) if posicao is not None else None,
            "capa": ("/capa/" + self._capa) if self._capa and self._chave_capa == r.get("chave") else None,
            "pode": pode,
        }


class Executor:
    def __init__(self, estado):
        self.estado = estado
        self.sistema = estado.sistema

    def apertar(self, bt):
        inicio = time.time()
        nome = "%s › %s" % (bt["pagina_nome"], bt["titulo"] or bt["icone"] or bt["imagem"] or "?")
        try:
            if bt["erro"]:
                raise ErroAcao(bt["erro"])
            if bt["fora"]:
                raise ErroAcao(bt["fora"])
            r = self.executar(bt["acao"])
        except ErroAcao as e:
            r = {"ok": False, "mensagem": str(e)}
        except Exception as e:
            log(vermelho(tr("Erro inesperado:\n") + traceback.format_exc()))
            r = {"ok": False, "mensagem": tr("Erro inesperado no computador: %s") % e}
        ms = int((time.time() - inicio) * 1000)
        if not r.get("ok"):
            marca = vermelho("✗ " + r.get("mensagem", ""))
        elif r.get("pendente"):
            marca = amarelo(tr("… rodando"))
        else:
            marca = verde("✓") + cinza(" %dms" % ms)
        log("▶ %s  %s" % (nome, marca))
        self.estado.invalidar()
        return r

    def executar(self, a):
        t = a["tipo"]
        s = self.sistema
        if t == "sequencia":
            final = {"ok": True}
            for n, passo in enumerate(a["acoes"]):
                try:
                    r = self.executar(passo)
                except ErroAcao as e:
                    raise ErroAcao(tr("Passo %d: %s") % (n + 1, e))
                for k in ("ativo", "info", "mensagem", "pendente"):
                    if r.get(k) is not None:
                        final[k] = r[k]
            return final
        if t == "esperar":
            time.sleep(a["segundos"])
            return {"ok": True}
        if t == "pagina":
            return {"ok": True}
        motivo = s.motivo(a)
        if motivo:
            raise ErroAcao(motivo)
        if t == "teclas":
            return s.teclas(a["combos"], a.get("app"), a.get("intervalo", 0.08))
        if t == "texto":
            return s.texto(a["texto"], a.get("app"))
        if t == "app":
            return s.app(a["apps"])
        if t == "link":
            if a.get("aba", True) and a["url"].lower().startswith(ESQUEMAS_SITE) and s.focar_aba(a["url"], a.get("navegador")):
                return {"ok": True}
            return s.abrir_site(a["url"], a.get("navegador"))
        if t == "comando":
            return s.comando(a["comando"], a.get("mostrar"))
        if t == "atalho":
            return s.atalho(a["atalho"])
        if t == "applescript":
            return s.applescript(a["script"], a.get("mostrar"))
        if t == "midia":
            return s.midia(a["midia"])
        if t == "volume":
            return s.volume(a["volume"])
        if t == "microfone":
            return s.microfone()
        if t == "energia":
            return s.energia(a["energia"])
        if t == "modo":
            return self.estado.ativar_modo(a)
        if t == "chamada":
            return self.estado.acao_chamada(a)
        return {"ok": True}


class Estado:
    def __init__(self, caminho, token, porta):
        self.caminho = caminho
        self.token = token
        self.porta = porta
        self.sistema = criar_sistema()
        self.computador = nome_do_computador()
        self.clientes = {}
        self._trava_celulares = threading.Lock()
        self.celulares = self._ler_celulares()
        self.bloqueados = {}
        self.editor_visto = 0.0
        self.fila = ThreadPoolExecutor(max_workers=1)
        self.executor = Executor(self)
        self._trava_cfg = threading.Lock()
        self._trava_gravar = threading.Lock()
        self._deck = None
        self._bruto = None
        self._assinatura = ()
        self._erro_cfg = None
        self._avisos_vistos = ()
        self._silencio = False
        self._ultimo_log_editor = 0.0
        self._copia_feita = False
        self._trava_audio = threading.Lock()
        self._audio = (0.0, None)
        self._rede = (0.0, None)
        self._mudanca = threading.Condition()
        self.icones = Icones(self.sistema, pasta_do_usuario("cache"), self.notificar)
        self.player = Player(self.sistema, os.path.join(pasta_do_usuario("cache"), "capas"))
        self._trava_modo = threading.RLock()
        self.modo = None
        self._timer_modo = None
        self.chamada = None
        self._chamada_vista = 0.0
        self._chamada_pausa = 0.0
        self._chamada_rodando = False
        self._chamada_avisou = False
        self._trava_chamada = threading.Lock()

    def notificar(self):
        with self._mudanca:
            self._mudanca.notify_all()

    def deck(self):
        with self._trava_cfg:
            try:
                st = os.stat(self.caminho)
                assinatura = (st.st_mtime_ns, st.st_size)
            except OSError:
                assinatura = None
            if self._deck is not None and assinatura == self._assinatura:
                return self._deck
            self._assinatura = assinatura
            novo, dados, erro = None, None, None
            if assinatura is None:
                erro = tr("Não achei o config.json (%s).") % self.caminho
            else:
                try:
                    novo, dados = ler_config(self.caminho)
                except ErroConfig as e:
                    erro = str(e)
                except OSError as e:
                    erro = tr("Não consegui ler o config.json (%s).") % e
            silencio, self._silencio = self._silencio, False
            if novo is not None:
                if self._deck is not None and not silencio:
                    log(verde(tr("↻ config.json recarregado")) + cinza(tr(" — %d botões") % novo.total))
                self._deck, self._bruto, self._erro_cfg = novo, dados, None
                if tuple(novo.avisos) != self._avisos_vistos:
                    for aviso in novo.avisos:
                        log(amarelo("⚠ " + aviso))
                    self._avisos_vistos = tuple(novo.avisos)
            else:
                log(vermelho("✗ " + erro) + (cinza(tr("  (mantendo a versão anterior)")) if self._deck else ""))
                self._erro_cfg = erro
                if self._deck is None:
                    self._deck = Deck.vazio(erro)
            return self._deck

    def img_do_botao(self, bt):
        if bt["imagem"]:
            return "/icones/" + quote(bt["imagem"]), "pronto", None
        if bt["icone"] or bt["erro"] or bt["fora"]:
            return None, None, None
        pedido = pedido_da_acao(bt["acao"])
        if not pedido:
            return None, None, None
        estado, arquivo = self.icones.consultar(pedido)
        alternativo = None
        if pedido[0] == "site":
            alt = self.icones.arquivo("alt|" + pedido[1])
            alternativo = ("/auto/" + alt) if alt else None
            if not arquivo:
                pequeno = self.icones.arquivo("fav|" + _host(pedido[1]))
                if pequeno:
                    return "/auto/" + pequeno, estado, alternativo
        return ("/auto/" + arquivo if arquivo else None), estado, alternativo

    def imagens(self, d):
        imgs = {}
        for p in d.paginas:
            for bt in p["botoes"]:
                if bt:
                    url, _, alternativo = self.img_do_botao(bt)
                    if url:
                        imgs[(bt["p"], bt["i"])] = (url, alternativo)
        return imgs

    def assinatura_imagens(self, imgs):
        texto = "|".join("%d.%d=%s,%s" % (k[0], k[1], v[0], v[1] or "") for k, v in sorted(imgs.items()))
        return hashlib.sha1(texto.encode()).hexdigest()[:10]

    def deck_publico(self):
        d = self.deck()
        imgs = self.imagens(d)
        pub = d.publico(imgs)
        pub["imgs"] = self.assinatura_imagens(imgs)
        pub["computador"] = self.computador
        pub["sistema"] = NOMES_SISTEMA[SISTEMA]
        pub["app"] = VERSAO
        pub["idioma"] = IDIOMA
        pub["erroConfig"] = self._erro_cfg
        return pub

    def esperar_mudanca(self, versao, imgs, limite=25.0):
        fim = time.time() + limite
        while True:
            d = self.deck()
            atual = self.assinatura_imagens(self.imagens(d))
            if d.versao != versao or atual != imgs:
                return {"versao": d.versao, "imgs": atual, "app": VERSAO, "mudou": True}
            resta = fim - time.time()
            if resta <= 0:
                return {"versao": d.versao, "imgs": atual, "app": VERSAO, "mudou": False}
            with self._mudanca:
                self._mudanca.wait(min(resta, 1.0))

    def config_para_editar(self):
        self.deck()
        if isinstance(self._bruto, dict):
            return json.loads(json.dumps(self._bruto))
        return {"nome": "Deck", "grade": {"colunas": 4, "linhas": 2}, "paginas": [{"nome": "Apps", "botoes": []}]}

    def visao(self, d):
        paginas = []
        for p in d.paginas:
            botoes = []
            for bt in p["botoes"]:
                if not bt:
                    botoes.append(None)
                    continue
                url, estado, alternativo = self.img_do_botao(bt)
                v = {"titulo": bt["titulo"], "tipo": (bt["acao"] or {}).get("tipo"),
                     "pedido": texto_do_pedido(pedido_da_acao(bt["acao"]))}
                for k in ("icone", "cor", "erro", "fora"):
                    if bt.get(k):
                        v[k] = bt[k]
                if url:
                    v["img"] = url
                if alternativo:
                    v["img2"] = alternativo
                if estado == "pendente":
                    v["pendente"] = True
                botoes.append(v)
            paginas.append({"nome": p["nome"], "icone": p.get("icone"), "tipo": p.get("tipo", "botoes"), "botoes": botoes})
        return {"paginas": paginas, "avisos": list(d.avisos)}

    def editor_dados(self):
        d = self.deck()
        return {
            "ok": True, "base": d.versao, "config": self.config_para_editar(), "erroConfig": self._erro_cfg,
            "sistema": SISTEMA, "nomeSistema": NOMES_SISTEMA[SISTEMA], "computador": self.computador,
            "tipos": TIPOS, "chavesSistema": CHAVES_SISTEMA, "cores": CORES, "visao": self.visao(d),
            "app": VERSAO, "geracao": self.icones.geracao, "navegadores": self.navegadores_publicos()[0],
            "iconesPagina": list(ICONES_PAGINA), "idioma": IDIOMA,
        }

    def editor_status(self):
        d = self.deck()
        info = self.info_parear()
        info.update({"base": d.versao, "geracao": self.icones.geracao, "app": VERSAO, "idioma": IDIOMA})
        return info

    def editor_visao(self):
        d = self.deck()
        return {"base": d.versao, "visao": self.visao(d), "geracao": self.icones.geracao}

    def editor_apps(self):
        lista, carregando = self.icones.catalogo()
        apps = [{"nome": a["nome"], "valor": a["valor"], "img": ("/auto/" + a["arquivo"]) if a["arquivo"] else None}
                for a in lista]
        return {"apps": apps, "carregando": carregando, "sistema": SISTEMA}

    def navegadores_publicos(self):
        try:
            lista = self.sistema.navegadores()
            padrao = self.sistema.navegador_padrao()
        except Exception:
            lista, padrao = [], None
        return [{"nome": n["nome"], "padrao": n["chave"] == padrao} for n in lista], padrao

    def _decorar_sites(self, itens, pedir):
        saida = []
        for item in itens:
            img, grande, img2 = self.icones.img_de_site(item["url"])
            d = {"url": item["url"], "titulo": item["titulo"], "navegador": item.get("navegador"), "img": img, "img2": img2}
            if not grande and pedir is not None:
                pedir.append(item["url"])
            saida.append(d)
        return saida

    def editor_sites(self, quer_abas):
        navegadores, padrao = self.navegadores_publicos()
        try:
            abas = self.sistema.abas_abertas() if quer_abas else []
        except Exception:
            abas = []
        vistos = set()
        lista_abas = []
        for a in abas:
            if not _site_vale(a["url"]):
                continue
            k = _chave_url(a["url"])
            if k in vistos:
                continue
            vistos.add(k)
            lista_abas.append({"url": a["url"], "titulo": titulo_curto(a["titulo"], a["url"], pagina=True), "navegador": a["navegador"]})
        dados, carregando = self.icones.sites(padrao)
        dados = dados or {"favoritos": [], "visitados": []}
        pedir = []
        r = {
            "abas": self._decorar_sites(lista_abas, pedir),
            "favoritos": self._decorar_sites(dados["favoritos"], pedir),
            "visitados": self._decorar_sites(dados["visitados"], pedir),
            "carregando": carregando, "navegadores": navegadores, "sistema": SISTEMA, "geracao": self.icones.geracao,
        }
        self.icones.pedir_sites(pedir, 16)
        return r

    def editor_site(self, url, titulo_pedido=None):
        if not isinstance(url, str) or not url.strip() or len(url) > 2000:
            return {"ok": False, "mensagem": tr("Escreva o endereço do site.")}, 400
        bruto = url.strip()
        url = bruto if tem_esquema(bruto) else "https://" + bruto
        try:
            host = urlparse(url).hostname
        except ValueError:
            host = None
        if url.lower().startswith(("http://", "https://")) and not host:
            return {"ok": False, "mensagem": tr("Esse endereço não parece um site.")}, 400
        if url.lower().startswith(("http://", "https://")):
            info = self.icones.site_agora(url)
            if info["falhou"] and not tem_esquema(bruto):
                outra = self.icones.site_agora("http://" + bruto)
                if not outra["falhou"]:
                    url, info = "http://" + bruto, outra
        else:
            info = {"titulo": url.split(":")[0].capitalize(), "arquivo": None, "alternativo": None, "falhou": False}
        titulo = info["titulo"]
        if isinstance(titulo_pedido, str) and titulo_pedido.strip():
            titulo = titulo_pedido.strip()[:40]
        return {"ok": True, "url": url, "titulo": titulo, "pedido": "site:" + url,
                "img": ("/auto/" + info["arquivo"]) if info["arquivo"] else None,
                "img2": ("/auto/" + info["alternativo"]) if info.get("alternativo") else None,
                "semInternet": info["falhou"] and not info["arquivo"]}, 200

    def editor_imagem(self, nome, dados):
        if not isinstance(dados, str) or not dados:
            return {"ok": False, "mensagem": tr("Nenhuma imagem recebida.")}, 400
        try:
            conteudo = base64.b64decode(dados.split(",", 1)[-1], validate=False)
        except (ValueError, TypeError):
            return {"ok": False, "mensagem": tr("Imagem inválida.")}, 400
        if len(conteudo) > 4 * 1024 * 1024:
            return {"ok": False, "mensagem": tr("Imagem grande demais (máximo 4 MB).")}, 413
        ext = tipo_imagem(conteudo)
        if ext not in IMAGENS:
            return {"ok": False, "mensagem": tr("Use uma imagem PNG, JPG, GIF, WEBP ou SVG.")}, 400
        base = simples(os.path.splitext(os.path.basename(str(nome or "imagem")))[0]).replace("_", "-")
        base = re.sub(r"[^a-z0-9-]+", "", base).strip("-")[:40] or "imagem"
        os.makedirs(PASTA_ICONES, exist_ok=True)
        final = base + ext
        n = 2
        while os.path.exists(os.path.join(PASTA_ICONES, final)):
            with open(os.path.join(PASTA_ICONES, final), "rb") as f:
                if f.read() == conteudo:
                    break
            final = "%s-%d%s" % (base, n, ext)
            n += 1
        caminho = os.path.join(PASTA_ICONES, final)
        if not os.path.exists(caminho):
            with open(caminho, "wb") as f:
                f.write(conteudo)
        return {"ok": True, "imagem": final, "img": "/icones/" + quote(final)}, 200

    def salvar_config(self, base, dados):
        if not isinstance(dados, dict) or not isinstance(dados.get("paginas"), list):
            return {"ok": False, "mensagem": tr("Configuração inválida.")}, 400
        if len(dados["paginas"]) > 60 or any(not isinstance(p, dict) or len(p.get("botoes") or []) > 128
                                             for p in dados["paginas"]):
            return {"ok": False, "mensagem": tr("Páginas ou botões demais.")}, 400
        try:
            montar_deck(dados, "teste")
        except (ErroConfig, TypeError, ValueError, AttributeError) as e:
            return {"ok": False, "mensagem": tr("Não salvei: %s") % e}, 400
        definir_idioma(dados.get("idioma"))
        traduzir_nomes_padrao(dados)
        texto = formatar_config(dados)
        with self._trava_gravar:
            d = self.deck()
            if base != d.versao:
                definir_idioma(self._bruto.get("idioma") if isinstance(self._bruto, dict) else None)
                r = self.editor_dados()
                r.update({"ok": False, "conflito": True,
                          "mensagem": tr("O config.json mudou fora do editor — carreguei a versão nova.")})
                return r, 409
            try:
                if not self._copia_feita and os.path.exists(self.caminho):
                    shutil.copy2(self.caminho, os.path.join(os.path.dirname(self.caminho), ".config-anterior.json"))
                    self._copia_feita = True
                gravar_atomico(self.caminho, texto)
            except OSError as e:
                return {"ok": False, "mensagem": tr("Não consegui salvar o config.json (%s).") % (e.strerror or e)}, 500
            with self._trava_cfg:
                self._assinatura = ()
                self._silencio = True
            d = self.deck()
        agora = time.time()
        if agora - self._ultimo_log_editor > 8:
            log(verde(tr("✎ Botões salvos pelo editor")) + cinza(tr(" — %d botões") % d.total))
            self._ultimo_log_editor = agora
        self.notificar()
        return {"ok": True, "base": d.versao, "visao": self.visao(d), "erroConfig": self._erro_cfg,
                "geracao": self.icones.geracao, "idioma": IDIOMA}, 200

    def invalidar(self):
        self._audio = (0.0, None)

    def audio(self, idade=1.2):
        with self._trava_audio:
            t, v = self._audio
            if v is not None and time.time() - t < idade:
                return v
            try:
                v = self.sistema.audio()
            except ErroAcao:
                v = None
            self._audio = (time.time(), v)
            return v

    def estado_publico(self, p):
        d = self.deck()
        if any(b and b["acao"] and b["acao"]["tipo"] == "chamada" for pg in d.paginas if not pg.get("oculta") for b in pg["botoes"]):
            self.vigiar_chamadas()
        modo = self.modo_publico()
        chamada = self.chamada
        r = {"versao": d.versao, "app": VERSAO, "erroConfig": self._erro_cfg, "ativos": [], "indisponiveis": [],
             "imgs": self.assinatura_imagens(self.imagens(d)), "modo": modo,
             "chamada": {"quem": chamada.get("quem"), "detalhe": chamada.get("detalhe"),
                         "recusar": bool(chamada.get("recusar"))} if chamada else None}
        if modo and not modo.get("concluido"):
            r["ativos"].append(modo["id"])
        if not 0 <= p < len(d.paginas):
            return r
        botoes = [b for b in d.paginas[p]["botoes"] if b]
        precisa_audio = any(tipos_em(b["acao"]) & {"volume", "microfone"} for b in botoes if b["acao"] and not b["fora"])
        audio = self.audio() if precisa_audio else None
        for b in botoes:
            bid = "%d.%d" % (b["p"], b["i"])
            a = b["acao"]
            if b["fora"]:
                r["indisponiveis"].append(bid)
                continue
            if not a:
                continue
            if any(self.sistema.motivo({"tipo": t}) for t in tipos_em(a)):
                r["indisponiveis"].append(bid)
                continue
            k = b["chave"]
            if audio and k and ((k[0] == "mic" and audio.get("mic_mudo")) or (k[0] == "vol_mudo" and audio.get("som_mudo"))):
                r["ativos"].append(bid)
            if audio and ((a["tipo"] == "microfone" and not audio.get("tem_mic"))
                          or (a["tipo"] == "volume" and not audio.get("tem_som"))):
                r["indisponiveis"].append(bid)
        return r

    def tocando_publico(self):
        r = self.player.estado()
        a = self.audio(3.0)
        if a:
            r["volume"] = a.get("volume")
            r["mudo"] = a.get("som_mudo")
        return r

    def controlar_tocando(self, acao, valor):
        if acao not in ("alternar", "proxima", "anterior", "posicao", "volume", "mudo"):
            return {"ok": False, "mensagem": tr("Ação desconhecida.")}, 400
        try:
            if acao == "volume":
                n = max(0, min(100, int(float(valor))))
                r = self.sistema.volume(str(n))
                self.invalidar()
                return dict(r, ok=True), 200
            if acao == "mudo":
                r = self.sistema.volume("mudo")
                self.invalidar()
                return dict(r, ok=True), 200
            atual = self.player.atual()
            if not atual.get("tem"):
                if acao in MIDIA_DO_PLAYER:
                    r = self.sistema.midia(MIDIA_DO_PLAYER[acao])
                    self.player.esquecer()
                    return dict(r or {}, ok=True), 200
                return {"ok": False, "mensagem": tr("Nada tocando no computador agora.")}, 200
            if acao == "posicao":
                valor = max(0.0, float(valor))
            r = self.sistema.controlar_tocando(acao, valor, atual)
        except (TypeError, ValueError):
            return {"ok": False, "mensagem": tr("Valor inválido.")}, 400
        except ErroAcao as e:
            return {"ok": False, "mensagem": str(e)}, 200
        self.player.esquecer()
        return dict(r or {}, ok=True), 200

    def _abrir_item(self, item):
        s = self.sistema
        if tem_esquema(item) or re.match(r"^[\w.-]+\.[a-z]{2,}(/|$)", item, re.I):
            url = item if tem_esquema(item) else "https://" + item
            if url.lower().startswith(ESQUEMAS_SITE) and s.focar_aba(url, None):
                return
            s.abrir_site(url, None)
        else:
            s.app([item])

    def _passo_do_modo(self, avisos, funcao, *args):
        try:
            r = funcao(*args)
        except ErroAcao as e:
            avisos.append(str(e))
            return
        except Exception as e:
            log(vermelho(tr("Erro inesperado:\n") + traceback.format_exc()))
            avisos.append(tr("Erro inesperado no computador: %s") % e)
            return
        if isinstance(r, dict) and r.get("mensagem"):
            avisos.append(r["mensagem"])

    def _sair_do_modo(self, modo, proximo=None):
        if self._timer_modo:
            self._timer_modo.cancel()
            self._timer_modo = None
        if modo and modo.get("nao_perturbe") is True and not modo.get("dnd_desligado") and (proximo is None or proximo.get("nao_perturbe") is None):
            modo["dnd_desligado"] = True
            avisos = []
            self._passo_do_modo(avisos, self.sistema.nao_perturbe, False)
            for aviso in avisos:
                log(amarelo("⚠ " + aviso))

    def _agendar_fim(self):
        if self._timer_modo:
            self._timer_modo.cancel()
            self._timer_modo = None
        m = self.modo
        if not m or not m.get("fim") or m.get("pausado") or m.get("concluido"):
            return
        t = threading.Timer(max(0.0, m["fim"] - time.time()) + 0.05, self._fim_do_timer, args=(m["inicio"],))
        t.daemon = True
        self._timer_modo = t
        t.start()

    def _fim_do_timer(self, inicio):
        with self._trava_modo:
            m = self.modo
            if not m or m["inicio"] != inicio or m.get("pausado") or m.get("concluido"):
                return
            if time.time() < m["fim"] - 0.2:
                self._agendar_fim()
                return
            m["concluido"] = True
            m["concluido_em"] = time.time()
            self._timer_modo = None
            log(verde(tr("⏱ %s: tempo encerrado") % m.get("titulo")))
            self._sair_do_modo(m)
        self.notificar()

    def ativar_modo(self, a):
        with self._trava_modo:
            atual = self.modo
            if atual and atual["id"] == a["id"] and not atual.get("concluido"):
                self._sair_do_modo(atual)
                self.modo = None
                return {"ok": True, "ativo": False, "info": tr("Desligado"), "modo": None}
            if atual and not atual.get("concluido"):
                self._sair_do_modo(atual, a)
        avisos = []
        s = self.sistema
        if a.get("nao_perturbe") is not None:
            self._passo_do_modo(avisos, s.nao_perturbe, a["nao_perturbe"])
        if a.get("fechar"):
            self._passo_do_modo(avisos, s.fechar_apps, a["fechar"])
        for item in a.get("abrir") or []:
            self._passo_do_modo(avisos, self._abrir_item, item)
        if a.get("volume") is not None:
            self._passo_do_modo(avisos, s.volume, str(a["volume"]))
        agora = time.time()
        with self._trava_modo:
            self.modo = {"id": a["id"], "titulo": a.get("titulo") or tr("Modo"), "icone": a.get("icone"), "cor": a.get("cor"),
                         "inicio": agora, "minutos": a.get("minutos"),
                         "fim": agora + a["minutos"] * 60 if a.get("minutos") else None,
                         "pausado": None, "nao_perturbe": a.get("nao_perturbe"), "concluido": False}
            self._agendar_fim()
            publico = self.modo_publico()
        self.invalidar()
        r = {"ok": True, "ativo": True, "info": a.get("titulo") or tr("Modo"), "modo": publico}
        if avisos:
            r["mensagem"] = avisos[0]
        return r

    def modo_publico(self):
        with self._trava_modo:
            m = self.modo
            if not m:
                return None
            if m.get("concluido") and time.time() - m.get("concluido_em", 0) > 900:
                self.modo = None
                return None
            r = {"id": m["id"], "titulo": m["titulo"], "icone": m.get("icone"), "cor": m.get("cor"),
                 "concluido": bool(m.get("concluido")), "pausado": bool(m.get("pausado"))}
            if m.get("fim"):
                agora = m["pausado"] or time.time()
                r["total"] = int(round((m["fim"] - m["inicio"]) - (m.get("pausa_total") or 0)))
                r["restante"] = 0 if m.get("concluido") else max(0.0, round(m["fim"] - agora, 2))
            return r

    def comando_modo(self, acao):
        with self._trava_modo:
            m = self.modo
            if not m:
                return {"ok": True, "modo": None}, 200
            agora = time.time()
            if acao == "pausar" and m.get("fim") and not m.get("pausado") and not m.get("concluido"):
                m["pausado"] = agora
                self._agendar_fim()
            elif acao == "retomar" and m.get("pausado"):
                parado = agora - m["pausado"]
                m["fim"] += parado
                m["pausa_total"] = (m.get("pausa_total") or 0) + parado
                m["pausado"] = None
                self._agendar_fim()
            elif acao == "mais5":
                if m.get("concluido") or not m.get("fim"):
                    m.update({"concluido": False, "fim": agora + 300, "inicio": agora, "pausado": None, "pausa_total": 0,
                              "dnd_desligado": False})
                    if m.get("nao_perturbe") is True:
                        avisos = []
                        self._passo_do_modo(avisos, self.sistema.nao_perturbe, True)
                        for aviso in avisos:
                            log(amarelo("⚠ " + aviso))
                else:
                    m["fim"] += 300
                self._agendar_fim()
            elif acao in ("encerrar", "fechar"):
                if not m.get("concluido"):
                    self._sair_do_modo(m)
                self.modo = None
            else:
                return {"ok": False, "mensagem": tr("Ação desconhecida.")}, 400
            publico = self.modo_publico()
        self.notificar()
        return {"ok": True, "modo": publico}, 200

    def app_de_chamada(self):
        s = self.sistema
        rodando = s.processos()
        for k in ORDEM_CHAMADA:
            if k == "meet":
                try:
                    if s.tem_reuniao_meet():
                        return k
                except ErroAcao:
                    pass
                continue
            if any(n.lower() in rodando for n in APPS_CHAMADA[k].get(SISTEMA, [])):
                return k
        return None

    def acao_chamada(self, a):
        s = self.sistema
        acao = a["chamada"]
        if acao in ("atender", "recusar"):
            recebida = self.chamada
            rotulo = recebida and recebida.get("aceitar" if acao == "atender" else "recusar")
            if rotulo:
                s.responder_chamada(rotulo)
                self.chamada = None
                return {"ok": True}
        app = a.get("app") or "auto"
        if app == "auto":
            app = self.app_de_chamada()
            if not app:
                if acao == "mudo":
                    return s.microfone()
                raise ErroAcao(tr("Não achei nenhuma reunião aberta (Meet, Zoom, Teams, Webex ou FaceTime). Para Discord e Slack, escolha o app no botão."))
        combo = ATALHOS_CHAMADA.get(app, {}).get("mac" if SISTEMA == "mac" else "outros", {}).get(acao)
        nome = APPS_CHAMADA[app]["nome"]
        if not combo:
            if acao == "mudo":
                return s.microfone()
            raise ErroAcao(tr("O %s não tem atalho para “%s”.") % (nome, tr(NOMES_CHAMADA[acao])))
        trouxe = s.focar_reuniao_meet() if app == "meet" else s.ativar_processo(APPS_CHAMADA[app].get(SISTEMA, []))
        if not trouxe:
            raise ErroAcao(tr("Não achei a janela do %s para mandar o atalho.") % nome)
        s.teclas([ler_combinacao(combo, nome)], None, 0.08)
        return {"ok": True}

    def vigiar_chamadas(self):
        if SISTEMA != "mac":
            return
        self._chamada_vista = time.time()
        with self._trava_chamada:
            if self._chamada_rodando:
                return
            self._chamada_rodando = True
        threading.Thread(target=self._laco_chamadas, daemon=True).start()

    def _laco_chamadas(self):
        try:
            while time.time() - self._chamada_vista < 20:
                if time.time() >= self._chamada_pausa:
                    try:
                        achada = self.sistema.chamada_recebida()
                    except ErroAcao as e:
                        achada = None
                        self._chamada_pausa = time.time() + 300
                        if not self._chamada_avisou:
                            self._chamada_avisou = True
                            log(amarelo(tr("⚠ Não consegui ver chamadas chegando (%s). Tento de novo em 5 minutos.") % str(e)[:160]))
                    antes = self.chamada
                    if achada and not antes:
                        log(verde(tr("📞 Chamada chegando: %s") % (achada.get("quem") or "?")))
                    self.chamada = dict(achada, desde=(antes or {}).get("desde") or time.time()) if achada else None
                    if bool(antes) != bool(achada):
                        self.notificar()
                time.sleep(2.0)
        finally:
            with self._trava_chamada:
                self._chamada_rodando = False
            self.chamada = None

    def comando_chamada(self, acao):
        if acao not in ("atender", "recusar"):
            return {"ok": False, "mensagem": tr("Ação desconhecida.")}, 400
        recebida = self.chamada
        rotulo = recebida and recebida.get("aceitar" if acao == "atender" else "recusar")
        if not rotulo:
            return {"ok": False, "mensagem": tr("A chamada não está mais tocando.")}, 200
        try:
            self.sistema.responder_chamada(rotulo)
        except ErroAcao as e:
            return {"ok": False, "mensagem": str(e)}, 200
        self.chamada = None
        return {"ok": True}, 200

    def apertar(self, dados):
        d = self.deck()
        if dados.get("versao") != d.versao:
            return {"ok": False, "recarregar": True,
                    "mensagem": tr("Os botões mudaram no computador — já atualizei aqui. Toque de novo.")}
        bt = d.botao(_int(dados.get("p"), -1), _int(dados.get("i"), -1))
        if not bt:
            return {"ok": False, "recarregar": True, "mensagem": tr("Esse botão não existe mais.")}
        futuro = self.fila.submit(self.executor.apertar, bt)
        try:
            return futuro.result(timeout=4.0)
        except TempoEsgotado:
            return {"ok": True, "pendente": True, "mensagem": tr("Rodando no computador…")}

    def visto(self, ip, agente, host=None):
        if "iPhone" in agente:
            aparelho = "iPhone"
        elif "iPad" in agente:
            aparelho = "iPad"
        elif "SamsungBrowser" in agente or re.search(r"\bSM-[A-Z]", agente):
            aparelho = "Samsung"
        elif "Android" in agente:
            aparelho = "Android"
        elif "Windows" in agente:
            aparelho = tr("PC com Windows")
        elif "Macintosh" in agente:
            aparelho = "Mac"
        elif "Linux" in agente:
            aparelho = tr("PC com Linux")
        else:
            aparelho = "Aparelho"
        if ip not in self.clientes:
            log(verde(tr("📱 %s conectado") % aparelho) + cinza(" (%s)" % ip))
        self.clientes[ip] = (time.time(), aparelho)
        if host:
            self._lembrar_celular(host, aparelho)

    def _arq_celulares(self):
        return os.path.join(pasta_do_usuario("dados"), "celulares.json")

    def _ler_celulares(self):
        try:
            with open(self._arq_celulares(), encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, ValueError):
            return {}
        return {str(k): v for k, v in dados.items() if isinstance(v, dict)} if isinstance(dados, dict) else {}

    def _lembrar_celular(self, host, aparelho):
        h = host.strip().lower()
        if h.startswith("["):
            h = h[1:h.find("]")] if "]" in h else h
        else:
            h = h.rsplit(":", 1)[0] if h.count(":") == 1 else h
        if not h or h in HOSTS_LOCAIS:
            return
        with self._trava_celulares:
            atual = self.celulares.get(h)
            agora = time.time()
            if atual and agora - atual.get("quando", 0) < 60 and atual.get("aparelho") == aparelho:
                return
            self.celulares[h] = {"aparelho": aparelho, "quando": agora}
            try:
                gravar_atomico(self._arq_celulares(), json.dumps(self.celulares, ensure_ascii=False, indent=2))
            except OSError:
                pass

    def bloqueado(self, ip):
        with self._trava_celulares:
            return ip in self.bloqueados

    def editor_celulares(self, acao, ip):
        if acao == "novo-link":
            novo = secrets.token_urlsafe(16)
            try:
                _gravar_token(os.path.join(pasta_do_usuario("dados"), "token"), novo)
            except OSError as e:
                return {"ok": False, "mensagem": tr("Não consegui gravar o link novo (%s).") % (e.strerror or e)}, 500
            self.token = novo
            with self._trava_celulares:
                self.clientes.clear()
                self.bloqueados.clear()
                self.celulares.clear()
                try:
                    gravar_atomico(self._arq_celulares(), "{}")
                except OSError:
                    pass
            log(amarelo(tr("Link novo gerado pelo editor: os celulares precisam escanear o QR code de novo.")))
            self.notificar()
            return {"ok": True, "token": novo}, 200
        ip = str(ip or "").strip()
        if not ip or len(ip) > 64:
            return {"ok": False, "mensagem": tr("Diga qual aparelho.")}, 400
        with self._trava_celulares:
            if acao == "desconectar":
                aparelho = (self.clientes.get(ip) or (0, "Aparelho"))[1]
                self.bloqueados[ip] = aparelho
                log(amarelo(tr("📱 %s (%s) desconectado pelo editor") % (aparelho, ip)))
            elif acao == "permitir":
                self.bloqueados.pop(ip, None)
                self.clientes.pop(ip, None)
            else:
                return {"ok": False, "mensagem": tr("Ação desconhecida.")}, 400
        self.notificar()
        return {"ok": True}, 200

    def rede(self):
        t, v = self._rede
        if v is None or time.time() - t > 10:
            v = (host_local(), enderecos_locais())
            self._rede = (time.time(), v)
        return v

    def avisos_conexao(self, host, enderecos, recentes):
        avisos = []
        if firewall_bloqueando():
            avisos.append({"tipo": "firewall", "texto": tr("O Firewall do Mac está bloqueando o deck. Em Ajustes do Sistema › Rede › "
                           "Firewall › Opções, mude o Python para \"Permitir conexões de entrada\" (ou clique em Permitir quando o aviso aparecer).")})
        if recentes:
            return avisos
        ips = {e["ip"] for e in enderecos}
        with self._trava_celulares:
            lembrados = sorted(self.celulares.items(), key=lambda kv: -kv[1].get("quando", 0))
        for h, info in lembrados[:3]:
            ap = info.get("aparelho") or tr("O celular")
            if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", h):
                if h not in ips:
                    avisos.append({"tipo": "ip-mudou", "texto": tr("%s estava usando o endereço %s, que este computador não tem mais — o link salvo "
                                   "nele não abre. Escaneie o QR code de novo (e prefira o link pelo nome, que não muda).") % (ap, h)})
            elif h.endswith(".local") and host and h != host.lower():
                avisos.append({"tipo": "nome-mudou", "texto": tr("O nome deste computador na rede mudou de %s para %s (o Mac faz isso quando acha "
                               "outro com o mesmo nome). Escaneie o QR code de novo, ou volte o nome em Ajustes do Sistema › Geral › "
                               "Compartilhamento › Nome local.") % (h, host)})
        return avisos

    def info_parear(self):
        host, enderecos = self.rede()
        sufixo = ":%d/?k=%s" % (self.porta, self.token)
        agora = time.time()
        with self._trava_celulares:
            bloqueados = dict(self.bloqueados)
            clientes = [{"ip": ip, "aparelho": ap, "segundos": int(agora - t), "bloqueado": ip in bloqueados}
                        for ip, (t, ap) in sorted(self.clientes.items(), key=lambda kv: -kv[1][0])]
        for ip, ap in bloqueados.items():
            if not any(c["ip"] == ip for c in clientes):
                clientes.append({"ip": ip, "aparelho": ap, "segundos": 999999, "bloqueado": True})
        ips = [e["ip"] for e in enderecos]
        lista = [dict(e, url="http://" + e["ip"] + sufixo, nome=tr(NOMES_VIA.get(e["tipo"], e["tipo"]))) for e in enderecos]
        recentes = [c for c in clientes if c["segundos"] < 30 and not c["bloqueado"]]
        with self._trava_celulares:
            lembrados = [{"host": h, "aparelho": v.get("aparelho")} for h, v in
                         sorted(self.celulares.items(), key=lambda kv: -kv[1].get("quando", 0))]
        return {
            "computador": self.computador, "sistema": NOMES_SISTEMA[SISTEMA], "porta": self.porta,
            "urlIp": ("http://" + ips[0] + sufixo) if ips else None,
            "urlNome": ("http://" + host + sufixo) if host else None,
            "nome": host, "enderecos": lista, "padrao": "nome" if SISTEMA == "mac" and host else "ip",
            "ips": ips, "clientes": clientes, "lembrados": lembrados, "erroConfig": self._erro_cfg,
            "avisos": self.avisos_conexao(host, enderecos, recentes),
        }


def pagina_no_idioma(corpo):
    if IDIOMA != "en":
        return corpo
    texto = corpo.decode("utf-8")
    texto = texto.replace('<html lang="pt-BR"', '<html lang="en"', 1)
    texto = re.sub(r"<title>(.*?)</title>", lambda m: "<title>" + tr(m.group(1)) + "</title>", texto, count=1)
    return texto.encode("utf-8")


TIPOS_ARQ = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".webmanifest": "application/manifest+json; charset=utf-8",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
    ".webp": "image/webp", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".woff2": "font/woff2",
    ".zip": "application/zip", ".json": "application/json; charset=utf-8", ".txt": "text/plain; charset=utf-8",
    ".sh": "text/plain; charset=utf-8", ".ps1": "text/plain; charset=utf-8",
}
PUBLICOS = {
    "/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/style.css": "style.css",
    "/manifest.webmanifest": "manifest.webmanifest", "/icon-180.png": "icon-180.png",
    "/icon-192.png": "icon-192.png", "/icon-512.png": "icon-512.png", "/icon-512-maskable.png": "icon-512-maskable.png",
    "/icon-32.png": "icon-32.png",
    "/teclas.css": "teclas.css", "/tom.js": "tom.js", "/icones.js": "icones.js",
    "/idioma.js": "idioma.js",
}
SO_NO_COMPUTADOR = {"/parear": "parear.html", "/parear.js": "parear.js", "/qrcode.js": "qrcode.js",
                    "/editar": "editar.html", "/editar.js": "editar.js", "/editar.css": "editar.css",
                    "/conectar.js": "conectar.js", "/conectar.css": "conectar.css", "/guia": "guia.html"}
CSP = ("default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
       "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
HOSTS_LOCAIS = {"127.0.0.1", "localhost", "::1"}
LIMITES_POST = {"/api/apertar": 65536, "/api/editor": 2 * 1024 * 1024, "/api/editor/site": 8192,
                "/api/editor/imagem": 6 * 1024 * 1024, "/api/editor/celulares": 4096,
                "/api/tocando": 4096, "/api/modo": 4096, "/api/chamada": 4096}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Deck/" + VERSAO
    sys_version = ""
    timeout = 120

    def log_message(self, *args):
        pass

    @property
    def estado(self):
        return self.server.estado

    def ip(self):
        ip = self.client_address[0]
        return ip[7:] if ip.startswith("::ffff:") else ip

    def local(self):
        return self.ip() in ("127.0.0.1", "::1")

    def host_pedido(self):
        h = (self.headers.get("Host") or "").strip().lower()
        if h.startswith("["):
            return h[1:h.find("]")] if "]" in h else ""
        return h.rsplit(":", 1)[0] if h.count(":") == 1 else h

    def local_seguro(self):
        if not self.local() or self.host_pedido() not in HOSTS_LOCAIS:
            return False
        origem = self.headers.get("Origin")
        if origem is not None:
            try:
                o = urlparse(origem)
            except ValueError:
                return False
            if o.scheme != "http" or (o.hostname or "") not in HOSTS_LOCAIS:
                return False
        return self.headers.get("Sec-Fetch-Site", "same-origin") in ("same-origin", "none")

    def editor_liberado(self):
        t = self.headers.get("X-Deck-Token") or ""
        ok = self.local_seguro() and bool(t) and hmac.compare_digest(t.encode(), self.estado.token.encode())
        if ok:
            self.estado.editor_visto = time.time()
        return ok

    def autorizado(self, q):
        t = self.headers.get("X-Deck-Token") or (q.get("k") or [""])[0]
        ok = bool(t) and hmac.compare_digest(t.encode(), self.estado.token.encode())
        if ok and not self.local():
            if self.estado.bloqueado(self.ip()):
                self.motivo_401 = "bloqueado"
                return False
            self.estado.visto(self.ip(), self.headers.get("User-Agent", ""), self.headers.get("Host", ""))
        return ok

    def manifesto(self, q):
        t = (q.get("k") or [""])[0]
        caminho = os.path.join(PASTA_WEB, "manifest.webmanifest")
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except (OSError, ValueError):
            return self.arquivo("manifest.webmanifest")
        if t and hmac.compare_digest(t.encode(), self.estado.token.encode()):
            dados["id"] = "/"
            dados["scope"] = "/"
            dados["start_url"] = "/?k=" + t
        return self._enviar(200, json.dumps(dados, ensure_ascii=False).encode("utf-8"), TIPOS_ARQ[".webmanifest"])

    def do_GET(self):
        self._tratar("GET")

    def do_POST(self):
        self._tratar("POST")

    def so_no_computador(self):
        msg = tr("Esta página só abre no próprio computador: http://localhost:%d/editar") % self.estado.porta
        return self.json({"ok": False, "erro": "so-no-computador", "mensagem": msg}, 403)

    def _tratar(self, metodo):
        try:
            u = urlparse(self.path)
            q = parse_qs(u.query)
            rota = u.path
            if metodo == "POST":
                limite = LIMITES_POST.get(rota, 65536)
                tamanho = _int(self.headers.get("Content-Length"), 0)
                if tamanho > limite:
                    self.close_connection = True
                    return self.json({"ok": False, "mensagem": tr("Pedido grande demais.")}, 413)
                corpo = self.rfile.read(tamanho) if tamanho > 0 else b""
                if rota not in LIMITES_POST:
                    return self.texto(404, tr("Não encontrado."))
                if rota.startswith("/api/editor"):
                    if not self.editor_liberado():
                        return self.so_no_computador()
                elif not self.autorizado(q):
                    return self.nao_autorizado()
                try:
                    dados = json.loads(corpo.decode("utf-8") or "{}")
                except ValueError:
                    return self.json({"ok": False, "mensagem": tr("Pedido inválido.")}, 400)
                if not isinstance(dados, dict):
                    return self.json({"ok": False, "mensagem": tr("Pedido inválido.")}, 400)
                e = self.estado
                if rota == "/api/apertar":
                    return self.json(e.apertar(dados))
                if rota == "/api/editor":
                    return self.json(*e.salvar_config(dados.get("base"), dados.get("config")))
                if rota == "/api/editor/site":
                    return self.json(*e.editor_site(dados.get("url"), dados.get("titulo")))
                if rota == "/api/editor/celulares":
                    return self.json(*e.editor_celulares(dados.get("acao"), dados.get("ip")))
                if rota == "/api/tocando":
                    return self.json(*e.controlar_tocando(dados.get("acao"), dados.get("valor")))
                if rota == "/api/modo":
                    return self.json(*e.comando_modo(dados.get("acao")))
                if rota == "/api/chamada":
                    return self.json(*e.comando_chamada(dados.get("acao")))
                return self.json(*e.editor_imagem(dados.get("nome"), dados.get("dados")))

            if rota == "/manifest.webmanifest":
                return self.manifesto(q)
            if rota in PUBLICOS:
                return self.arquivo(PUBLICOS[rota])
            if rota == "/site" or rota.startswith("/site/"):
                if not self.local_seguro():
                    return self.texto(403, tr("Esta página só abre no próprio computador."))
                if rota == "/site":
                    self.send_response(302)
                    self.send_header("Location", "/site/")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None
                return self.site(unquote(rota[len("/site"):]))
            if rota in SO_NO_COMPUTADOR:
                if not self.local_seguro():
                    return self.texto(403, tr("Esta página só abre no próprio computador: http://localhost:%d%s")
                                      % (self.estado.porta, "/editar" if rota.startswith("/editar") else "/parear"))
                if rota == "/guia":
                    pedido = idioma_pedido((q.get("idioma") or [""])[0])
                    return self.arquivo("guia-en.html" if (pedido if pedido != "auto" else IDIOMA) == "en" else "guia.html")
                return self.arquivo(SO_NO_COMPUTADOR[rota])
            if rota in ("/api/parear", "/api/editor/sessao"):
                if not self.local_seguro():
                    return self.so_no_computador()
                if rota == "/api/editor/sessao":
                    return self.json({"ok": True, "token": self.estado.token})
                return self.json(self.estado.info_parear())
            if rota.startswith("/api/editor"):
                if not self.editor_liberado():
                    return self.so_no_computador()
                if rota == "/api/editor":
                    return self.json(self.estado.editor_dados())
                if rota == "/api/editor/status":
                    return self.json(self.estado.editor_status())
                if rota == "/api/editor/visao":
                    return self.json(self.estado.editor_visao())
                if rota == "/api/editor/apps":
                    return self.json(self.estado.editor_apps())
                if rota == "/api/editor/sites":
                    return self.json(self.estado.editor_sites((q.get("abas") or ["1"])[0] != "0"))
                if rota == "/api/editor/tocando":
                    return self.json(self.estado.tocando_publico())
                return self.texto(404, tr("Não encontrado."))
            if rota.startswith(("/api/", "/icones/", "/auto/", "/capa/")):
                if not self.autorizado(q):
                    return self.nao_autorizado()
                if rota == "/api/deck":
                    return self.json(self.estado.deck_publico())
                if rota == "/api/estado":
                    return self.json(self.estado.estado_publico(_int((q.get("p") or ["-1"])[0], -1)))
                if rota == "/api/tocando":
                    return self.json(self.estado.tocando_publico())
                if rota.startswith("/capa/"):
                    nome = rota[len("/capa/"):]
                    if not re.fullmatch(r"[0-9a-f]{20}\.(png|jpg|gif|webp)", nome):
                        return self.texto(404, tr("Não encontrado."))
                    return self.icone(self.estado.player.pasta, nome, "private, max-age=31536000, immutable")
                if rota == "/api/espera":
                    v = (q.get("v") or [""])[0]
                    s = (q.get("s") or [""])[0]
                    return self.json(self.estado.esperar_mudanca(v, s, 25.0))
                if rota.startswith("/icones/"):
                    return self.icone(PASTA_ICONES, unquote(rota[len("/icones/"):]), "private, max-age=300")
                if rota.startswith("/auto/"):
                    nome = rota[len("/auto/"):]
                    if not re.fullmatch(r"[0-9a-f]{20}\.(png|svg|ico|jpg|gif|webp)", nome):
                        return self.texto(404, tr("Ícone não encontrado."))
                    return self.icone(self.estado.icones.pasta, nome, "private, max-age=31536000, immutable")
            return self.texto(404, tr("Não encontrado."))
        except (BrokenPipeError, ConnectionResetError, socket.timeout):
            self.close_connection = True
        except Exception:
            log(vermelho(tr("Erro interno:\n") + traceback.format_exc()))
            try:
                self.json({"ok": False, "mensagem": tr("Erro interno no computador (detalhes no terminal).")}, 500)
            except Exception:
                self.close_connection = True

    def _enviar(self, status, corpo, tipo, cache="no-store", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(corpo)

    def json(self, obj, status=200):
        corpo = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._enviar(status, corpo, "application/json; charset=utf-8")

    def texto(self, status, msg):
        self._enviar(status, msg.encode("utf-8"), "text/plain; charset=utf-8")

    def nao_autorizado(self):
        if getattr(self, "motivo_401", None) == "bloqueado":
            return self.json({"ok": False, "erro": "bloqueado",
                              "mensagem": tr("Este aparelho foi desconectado pelo computador.")}, 401)
        self.json({"ok": False, "erro": "nao-autorizado",
                   "mensagem": tr("Link antigo ou inválido. Escaneie o QR code de novo.")}, 401)

    def site(self, caminho):
        if not os.path.isdir(PASTA_SITE):
            return self.texto(404, tr("A pasta site/ não está ao lado da pasta do deck (ela existe só no repositório)."))
        partes = [p for p in caminho.split("/") if p]
        if any(p in ("..", ".") or p.startswith(".") for p in partes):
            return self.texto(404, tr("Não encontrado."))
        alvo = os.path.join(PASTA_SITE, *partes) if partes else PASTA_SITE
        if os.path.isdir(alvo):
            alvo = os.path.join(alvo, "index.html")
        elif not os.path.exists(alvo) and os.path.isfile(alvo + ".html"):
            alvo += ".html"
        try:
            with open(alvo, "rb") as f:
                corpo = f.read()
        except OSError:
            return self.texto(404, tr("Não encontrado."))
        tipo = TIPOS_ARQ.get(os.path.splitext(alvo)[1].lower(), "application/octet-stream")
        extra = {"Content-Disposition": 'attachment; filename="deck.zip"'} if alvo.endswith(".zip") else None
        self._enviar(200, corpo, tipo, cache="no-cache", extra=extra)

    def arquivo(self, nome):
        try:
            with open(os.path.join(PASTA_WEB, nome), "rb") as f:
                corpo = f.read()
        except OSError:
            return self.texto(404, tr("Faltou o arquivo web/%s — descompacte a pasta inteira.") % nome)
        tipo = TIPOS_ARQ.get(os.path.splitext(nome)[1].lower(), "application/octet-stream")
        extra = {"Content-Security-Policy": CSP} if nome.endswith(".html") else None
        if nome in ("index.html", "editar.html", "parear.html"):
            corpo = pagina_no_idioma(corpo)
        self._enviar(200, corpo, tipo, cache="no-cache", extra=extra)

    def icone(self, pasta, nome, cache):
        nome = os.path.basename(nome)
        ext = os.path.splitext(nome)[1].lower()
        if not nome or ext not in TIPOS_ARQ or not TIPOS_ARQ[ext].startswith("image/"):
            return self.texto(404, tr("Ícone não encontrado."))
        try:
            with open(os.path.join(pasta, nome), "rb") as f:
                corpo = f.read()
        except OSError:
            return self.texto(404, tr("Ícone não encontrado."))
        extra = {"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'"} if ext == ".svg" else None
        self._enviar(200, corpo, TIPOS_ARQ[ext], cache=cache, extra=extra)


class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, porta, estado):
        self.estado = estado
        try:
            self.address_family = socket.AF_INET6
            ThreadingHTTPServer.__init__(self, ("::", porta), Handler)
        except OSError as e:
            if e.errno in (errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", -1)):
                raise
            self.address_family = socket.AF_INET
            ThreadingHTTPServer.__init__(self, ("0.0.0.0", porta), Handler)

    def server_bind(self):
        if self.address_family == socket.AF_INET6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, OSError):
                pass
        socketserver.TCPServer.server_bind(self)
        self.server_name = "deck"
        self.server_port = self.server_address[1]


def anunciar_na_rede(porta):
    if SISTEMA != "mac" or os.environ.get("DECK_SISTEMA") or not shutil.which("dns-sd"):
        return None
    try:
        return subprocess.Popen(["dns-sd", "-R", "Deck", "_deck._tcp", "local", str(porta)],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None


def abrir_no_navegador(estado, porta, pagina, sempre):
    if not sempre:
        time.sleep(3.0)
        if time.time() - estado.editor_visto < 6:
            log(cinza(tr("O editor já estava aberto no navegador — não abri outra aba.")))
            return
    try:
        webbrowser.open("http://localhost:%d%s" % (porta, pagina))
    except Exception:
        pass


def banner(estado):
    info = estado.info_parear()
    linha = cinza("─" * 66)
    print()
    print("  " + negrito(tr("Deck ligado ✓")) + cinza("   v%s · %s · %s" % (VERSAO, estado.computador,
                                                                       NOMES_SISTEMA[SISTEMA])))
    print("  " + linha)
    print(tr("  Escolher os botões:  ") + negrito("http://localhost:%d/editar" % estado.porta))
    print(tr("  Conectar o celular:  http://localhost:%d/parear") % estado.porta + cinza("  (QR code)"))
    if info["urlIp"]:
        print(tr("  Link (IP):           ") + info["urlIp"])
    if info["urlNome"]:
        print(tr("  Link (nome):         ") + info["urlNome"])
    print("  " + linha)
    print("  " + cinza(tr("O que você muda no editor aparece no celular na hora. Deixe esta janela aberta; Ctrl+C desliga.")))
    if SISTEMA == "windows":
        print("  " + amarelo(tr("Se o Windows perguntar sobre o Firewall, marque Redes privadas e clique em Permitir.")))
    print()


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--audio-windows":
        print(json.dumps(audio_windows(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")))
        return
    if len(sys.argv) >= 3 and sys.argv[1] == "--icones-windows":
        print(json.dumps(icones_windows(sys.argv[2])))
        return

    ap = argparse.ArgumentParser(description=tr("Deck — o celular vira um painel de botões do computador."))
    ap.add_argument("--porta", type=int, default=_int(os.environ.get("DECK_PORTA"), PORTA_PADRAO))
    ap.add_argument("--parear", action="store_true", help=tr("abre a página com o QR code"))
    ap.add_argument("--novo-link", action="store_true", help=tr("troca o link secreto (desconecta os celulares)"))
    ap.add_argument("--sem-navegador", action="store_true", help=tr("não abre o editor no navegador ao ligar"))
    ap.add_argument("--idioma", default="", help=tr("idioma da interface: auto, pt ou en"))
    ap.add_argument("--config", default=ARQ_CONFIG_LOCAL if os.path.isfile(ARQ_CONFIG_LOCAL) else ARQ_CONFIG,
                    help=tr("caminho do config.json (se existir config.local.json, ele é usado)"))
    args = ap.parse_args()
    if idioma_pedido(args.idioma) != "auto":
        global IDIOMA_FORCADO
        IDIOMA_FORCADO = idioma_pedido(args.idioma)
        definir_idioma(None)

    if sys.version_info < (3, 8):
        sys.exit(tr("Precisa do Python 3.8 ou mais novo (você tem %d.%d).") % sys.version_info[:2])

    token, token_novo = carregar_token(args.novo_link)
    estado = Estado(os.path.abspath(args.config), token, args.porta)
    estado.deck()
    try:
        srv = Servidor(args.porta, estado)
    except OSError as e:
        if e.errno in (errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", -1)):
            sys.exit(vermelho(tr("A porta %d já está em uso — o deck já está aberto em outra janela?") % args.porta)
                     + tr("\nFeche a outra janela ou use:  --porta %d") % (args.porta + 1))
        raise

    banner(estado)
    estado.imagens(estado.deck())
    if SISTEMA == "windows":
        threading.Thread(target=estado.sistema.apps_iniciar, daemon=True).start()
    if token_novo and args.novo_link:
        log(amarelo(tr("Link novo gerado: os celulares precisam escanear o QR code de novo.")))
    tem_tela = SISTEMA != "linux" or os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    if tem_tela and not os.environ.get("DECK_SISTEMA") and (args.parear or token_novo or not args.sem_navegador):
        if args.parear:
            pagina = "/parear"
        else:
            pagina = "/editar#conectar" if token_novo else "/editar"
        threading.Thread(target=abrir_no_navegador, args=(estado, args.porta, pagina, args.parear or token_novo), daemon=True).start()
    anuncio = anunciar_na_rede(args.porta)
    try:
        srv.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print(tr("\n  Deck desligado. Até a próxima!\n"))
    finally:
        srv.server_close()
        estado.fila.shutdown(wait=False)
        if anuncio:
            try:
                anuncio.terminate()
            except OSError:
                pass


if __name__ == "__main__":
    main()
