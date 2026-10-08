# Deck

Seu celular vira um painel de botões para o computador.

| Pasta | O que é |
|---|---|
| `deck/` | o programa (Mac, Windows e Linux) — é o que as pessoas baixam |
| `site/` | o site com o download, o passo a passo e as linhas de instalação pelo terminal — publicado na Vercel |

## Rodar o programa

Entre em `deck/` e dê duplo clique no arquivo de iniciar do seu sistema (ou `python3 server.py`). O manual completo está em `deck/README.md` e, com o deck ligado, em **Como usar** na lateral do editor.

Seus botões pessoais ficam em `deck/config.local.json` (fora do Git); o `deck/config.json` é o exemplo que vai no download.

## Instalação pelo terminal

O site monta sozinho, com o próprio endereço, a linha que as pessoas colam no Terminal (Mac e Linux) ou no PowerShell (Windows). Ela roda `site/instalar.sh` ou `site/instalar-windows.ps1`: baixa o `deck.zip`, descompacta em `~/Deck`, tira a quarentena (no Mac, o que evita o aviso "A Apple não pôde verificar…") e liga o deck. Rodar de novo atualiza sem perder os botões. Com o deck ligado, dá para testar em `http://localhost:8787/site/`.

## Publicar o site

O site é estático. Na Vercel: **Add New › Project › Import** este repositório, **Root Directory: `site`**, Framework **Other**, sem build. Cada push republica.

## Lançar uma versão nova

1. Mude `VERSAO` em `deck/server.py` e o "versão 3.0" em `site/index.html`.
2. Rode `site/atualizar-zip.sh` — ele gera `site/deck.zip` a partir de `deck/`, sem seus botões pessoais.
3. Commit e push.
# deco
