# Site do Deck

Site estático: página inicial com o download, o passo a passo e as linhas de instalação pelo terminal.

- `index.html` — a página em português (as linhas de instalação se montam sozinhas com o endereço do site)
- `en.html` — a mesma página em inglês, em `/en`. Na primeira visita, quem tem o navegador em outro idioma vai para o inglês; o link PT/EN no topo troca e a escolha fica lembrada
- `deck.zip` — o programa (troque este arquivo a cada versão nova)
- `instalar.sh` — o que a linha do Terminal do Mac e do Linux roda: baixa o `deck.zip`, descompacta em `~/Deck`, tira a quarentena do macOS e liga (mensagens em português ou inglês, conforme o sistema)
- `instalar-windows.ps1` — o mesmo para o PowerShell do Windows
- `img/` — imagens da página
- `vercel.json` — faz o `deck.zip` baixar em vez de abrir e serve os instaladores como texto

Para publicar na Vercel, veja o passo a passo que acompanha este pacote.
