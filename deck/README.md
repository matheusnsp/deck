# Deck

Painel de botões no celular para controlar o computador.
O computador pode ser **Mac, Windows ou Linux**; o painel abre em **qualquer celular** (iPhone, Samsung e outros Android) ou no navegador de outro computador/tablet.

Você monta os botões **num editor visual no computador**; o celular só espelha, na hora. Vem pronto com páginas de **favoritos, apps, sites, mídia, produtividade e sistema**, em 4×2, pensado para usar o celular **deitado**.

**Comece aqui:** no Mac e no Linux, cole a linha do Terminal que está no site do Deck (ela baixa, libera e liga); ou baixe o `deck.zip`, descompacte e dê duplo clique no arquivo de iniciar do seu sistema (seção 1). Depois escaneie o QR code com o celular (seção 2) e monte os botões (seção 3). O guia completo, do download ao uso em qualquer aparelho, está dentro do próprio deck: **Como usar**, na lateral do editor (`http://localhost:8787/guia`).

---

## 1 · Ligar no computador

| Sistema | Precisa | Como ligar |
|---|---|---|
| **Mac** | nada (se pedir "ferramentas de linha de comando", aceite) | duplo clique em `Iniciar no Mac.command` (ou Terminal na pasta → `python3 server.py`, que nunca mostra aviso) |
| **Windows** | Python 3 — [python.org](https://www.python.org/downloads/), marque **Add python.exe to PATH** | duplo clique em `Iniciar no Windows.bat` |
| **Linux** | Python 3 (já vem) | `./iniciar-linux.sh` ou `python3 server.py` |

**Aviso de segurança na primeira vez** (só com o zip baixado pelo navegador; a linha do Terminal do site não passa por isso):

- **Mac:** "A Apple não pôde verificar se o item está livre de malware", com os botões Mover para o Lixo / OK. Clique em **OK**, vá em **Ajustes do Sistema › Privacidade e Segurança**, role até o fim e clique em **Abrir Mesmo Assim** (aparece por cerca de uma hora depois da tentativa). É uma vez só. No macOS 14 ou anterior, basta botão direito › **Abrir**.
- **Windows:** "Não é possível verificar o editor" ou "O Windows protegeu o computador": desmarque **Sempre perguntar antes de abrir este arquivo** e clique em **Executar** (ou **Mais informações › Executar assim mesmo**). Se continuar perguntando, botão direito no `.bat` › Propriedades › **Desbloquear**.
- **Linux:** nenhum aviso. Se o `./iniciar-linux.sh` não rodar, `chmod +x iniciar-linux.sh`.

Ao ligar, abre o **editor** no navegador (`http://localhost:8787/editar`) — se ele já estiver aberto em alguma aba, o deck não abre outra. Deixe a janela do terminal aberta enquanto usa.

Para o editor virar um app com janela própria (sem abas nem barra de endereço): no Safari, **Arquivo › Adicionar ao Dock**; no Chrome/Edge, menu **⋮ › Transmitir, salvar e compartilhar › Instalar página como app**.

---

## 2 · Conectar o celular

No editor, clique em **Conectar celular** (ou abra `http://localhost:8787/parear`).

1. Celular no **mesmo Wi-Fi** do computador.
2. Abra a **câmera**, aponte para o QR code e toque no link.
3. Salve na tela inicial para abrir como app:
   - **iPhone:** Compartilhar › Adicionar à Tela de Início
   - **Android/Samsung:** menu ⋮ › Adicionar à tela inicial — e use o botão de **tela cheia** no canto (esconde as barras e deixa deitado)

No Mac, o QR code vem **pelo nome** (`SeuMac.local`): esse link continua valendo mesmo que o IP do computador mude. Android não abre por nome — nele, toque em **Pelo IP**.

### Quatro formas de conectar

A janela **Conectar celular** tem quatro abas. O deck funciona por qualquer uma: ele só precisa de um caminho de rede entre o celular e o computador.

| Aba | Quando usar | Como |
|---|---|---|
| **Wi-Fi** | os dois na mesma rede | é o normal; só escanear |
| **Cabo USB** | na mesa, sem depender de roteador (zero atraso e carrega o celular) | iPhone: Ajustes › **Hotspot Pessoal** › Permitir que Outros se Conectem, e ligue o cabo. Android: **Ancoragem USB** (no Mac, só Android 14+) |
| **Bluetooth** | sem cabo e sem roteador (mais lento, mas sobra) | Hotspot Pessoal (ou Ancoragem Bluetooth) ligado, pareie os dois e, no Mac, menu Bluetooth › celular › **Conectar à Rede** |
| **Rede do computador** | não há Wi-Fi nenhum, ou o plano do celular não tem hotspot | Mac: **Compartilhamento de Internet** por Bluetooth PAN. Windows: **Ponto de acesso móvel**. Linux: ponto de acesso Wi-Fi |

A mesma janela lista os celulares conectados: **Desconectar** tira um aparelho na hora (ele vê o aviso e só volta quando você clicar em **Permitir de novo**), e **Gerar link novo** desconecta todos de uma vez — os que você quiser de volta escaneiam o QR code de novo.

Em cada aba o deck detecta sozinho quando o celular aparece por aquele caminho e mostra o QR code certo. Cabo USB e Bluetooth usam o **Hotspot Pessoal** do celular, que precisa estar liberado no plano da operadora (quase todos liberam). Com o cabo ligado, o computador pode passar a usar a internet do celular — no Mac, Ajustes do Sistema › Rede › ⋯ › **Definir Ordem de Serviço** e deixe o Wi-Fi acima de "iPhone USB".

---

## 3 · Escolher os botões (editor)

Tudo no `http://localhost:8787/editar`, que só abre no próprio computador:

- **Clique num espaço vazio (+)** e escolha o que o botão faz: app, site, atalho de teclado, texto, mídia, volume, microfone ou ir para outra página.
- **App:** escolha na lista dos apps instalados — o botão ganha **o mesmo ícone do app no computador**.
- **Energia:** desligar, reiniciar, suspender ou bloquear o computador. Desligar, reiniciar e suspender pedem um **segundo toque** no celular por padrão. Ligar um computador desligado pelo celular não é possível (não há nada rodando nele para receber o pedido): prefira **Suspender** — ele acorda com qualquer tecla e, no Mac com "Despertar para acesso à rede" ligado e um Apple TV, HomePod ou roteador Apple na rede, acorda sozinho quando o Deck abre no celular (o deck se anuncia na rede para isso).
- **Site:** digite um endereço ou escolha entre as **abas abertas agora** (Mac), os **favoritos** e os **sites mais visitados** dos navegadores do computador. O botão ganha **o ícone do próprio site** — e, quando o site tem um app oficial (WhatsApp, YouTube, Notion…), o deck busca também **o ícone oficial do app** e usa ele no lugar de ícones brancos ou pequenos demais. Dá para escolher em qual navegador abrir e, no Mac, se a aba já estiver aberta o botão só **traz ela para frente** em vez de abrir outra.
- **Atalho de teclado:** clique no campo e aperte as teclas.
- **Arraste** os botões para mudar a ordem; solte numa aba lá em cima para levar para outra página. **+ Página** cria mais páginas — no celular, deslize para o lado.
- Nome, emoji ou imagem própria, cor e confirmação (segundo toque) ficam no painel da direita.

Tudo salva sozinho no `config.json` (uma cópia do anterior fica em `.config-anterior.json`). Ctrl/⌘+Z desfaz. Se existir um `config.local.json` na pasta, o deck usa ele no lugar — útil para manter seus botões fora do Git enquanto o `config.json` continua sendo o exemplo.

---

## 4 · Tipos de botão

| Tipo | Faz | Mac | Windows | Linux |
|---|---|:-:|:-:|:-:|
| App | abre um programa | ✓ | ✓ | ✓ |
| Site | abre uma aba no navegador (ou traz a aba já aberta¹) | ✓ | ✓ | ✓ |
| Atalho de teclado | aperta teclas, ex. `ctrl+shift+t` | ✓ | ✓ | ✓² |
| Texto | digita uma frase pronta | ✓ | ✓ | ✓² |
| Mídia | tocar/pausar, próxima, anterior | ✓ | ✓ | ✓³ |
| Volume | subir, baixar, mudo ou um valor | ✓ | ✓ | ✓⁴ |
| Microfone | liga/desliga o mudo (acende a luz MUDO) | ✓ | ✓ | ✓⁴ |
| Energia | desligar, reiniciar, suspender, bloquear (com segundo toque) | ✓ | ✓ | ✓⁵ |
| Ir para página | troca a página no celular | ✓ | ✓ | ✓ |

¹ no Mac, com Safari, Chrome, Edge, Brave, Arc, Vivaldi ou Opera; no Windows e no Linux abre uma aba nova ·
² precisa do `xdotool` (ou `wtype` no Wayland) · ³ `playerctl` · ⁴ `pactl` ou `wpctl` (já vêm na maioria das distros) · ⁵ `systemctl`/`loginctl` (systemd)

Quem prefere editar o `config.json` na mão ainda pode (o editor e o celular acompanham): há também `comando`, `sequencia`, `esperar`, e no Mac `atalho` (app Atalhos) e `applescript`. Valores por sistema: `"app": { "mac": "Safari", "windows": "Microsoft Edge", "linux": "Firefox" }`.

---

## 5 · Permissões (só na primeira vez)

| Sistema | O que aparece | O que fazer |
|---|---|---|
| Mac | "Terminal quer controlar System Events" | Permitir |
| Mac | "Terminal quer controlar o Safari/Chrome" | Permitir — é o que lista as abas abertas e traz a aba para frente |
| Mac | teclas/texto/mídia não funcionam | Ajustes do Sistema › Privacidade e Segurança › **Acessibilidade** → ativar o Terminal, fechar e abrir o Terminal |
| Windows | alerta do Firewall para o Python | marcar **Redes privadas** › Permitir (o Wi-Fi precisa estar como rede privada) |
| Linux | firewall `ufw` ativo | `sudo ufw allow 8787/tcp` |

---

## 6 · Se não conectar

- **O app abre com a tela preta** (ou "não foi possível conectar"): o celular não está achando o computador no endereço salvo. Feche o app no celular (deslize para cima) e abra de novo com o deck ligado. Se continuar, o endereço mudou — abra **Conectar celular** no editor: ele avisa quando o IP ou o nome do computador mudou e mostra o QR code novo. Para isso não acontecer mais, use o link **pelo nome** (padrão no Mac) ou o cabo USB.
- Confira se o celular e o computador estão **no mesmo Wi-Fi**. Wi-Fi de visitantes e redes de empresa costumam bloquear aparelhos entre si — nesse caso, use o **cabo USB** ou o **Bluetooth** (seção 2).
- No Mac, se o **Firewall** estiver bloqueando o Python, a janela Conectar celular avisa: Ajustes do Sistema › Rede › Firewall › Opções › Python › **Permitir conexões de entrada** (ou clique em Permitir no aviso que aparece ao ligar o deck).
- Para a tela do celular não apagar, aumente o **bloqueio automático** enquanto usa.

---

## 7 · Segurança e privacidade

- O editor e a página do QR code só abrem no próprio computador (`localhost`).
- Só quem tem o link do celular (com a chave secreta) aperta os botões, e mesmo assim só os botões que você criou — o celular nunca manda comandos livres. A chave fica na pasta de dados do seu usuário; para trocar e desconectar todos: `--novo-link`.
- As sugestões de sites vêm dos favoritos e do histórico dos navegadores **deste** computador e não saem dele. Ícones de sites são baixados do próprio site; para achar o ícone oficial do app, o deck consulta a busca pública da App Store (só o nome do site) e, se precisar, o serviço de ícones do Google (só o domínio). Nada sobre você é enviado; os ícones ficam guardados na pasta de dados por 7 dias.
- O deck guarda na pasta de dados do seu usuário só o endereço que cada celular usou para abrir (para avisar quando o IP ou o nome do computador mudar); nada disso sai do computador.
- Use em rede de confiança (casa/escritório): a conexão local não é criptografada.

**Opções:** `--porta 9000` · `--parear` · `--novo-link` · `--sem-navegador` · `--config outro.json`

Créditos: gerador de QR code [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) (MIT).
