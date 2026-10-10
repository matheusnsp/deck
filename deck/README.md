# Deck

🇺🇸 [English version](README.en.md)

Painel de botões no celular para controlar o computador.
O computador pode ser **Mac, Windows ou Linux**; o painel abre em **qualquer celular** (iPhone, Samsung e outros Android) ou no navegador de outro computador/tablet.

Você monta os botões **num editor visual no computador**; o celular só espelha, na hora. Vem pronto com páginas de **favoritos, DJ (o que está tocando), modos, apps, sites, mídia, produtividade, chamadas e sistema**, em 4×2, pensado para usar o celular **deitado**.

A interface é em **português ou inglês**: segue o idioma do computador, e dá para trocar em **Configurações › Idioma** no editor (vale para o editor, o celular e o guia).

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

- **Clique num espaço vazio (+)** e escolha o que o botão faz: app, site, atalho de teclado, texto, mídia, volume, microfone, energia, modo, chamada ou ir para outra página.
- **App:** escolha na lista dos apps instalados (no Mac, os da pasta Aplicativos e os que estão em outras pastas suas, como Downloads) — o botão ganha **o mesmo ícone do app no computador**. A busca também acha pelas iniciais: “vs code” encontra o Visual Studio Code. Se o app não estiver instalado e tiver versão web (Spotify, WhatsApp, Discord, Slack, Notion, Teams…), o botão abre o site e avisa no celular.
- **Energia:** desligar, reiniciar, suspender ou bloquear o computador. Desligar, reiniciar e suspender pedem um **segundo toque** no celular por padrão. Ligar um computador desligado pelo celular não é possível (não há nada rodando nele para receber o pedido): prefira **Suspender** — ele acorda com qualquer tecla e, no Mac com "Despertar para acesso à rede" ligado e um Apple TV, HomePod ou roteador Apple na rede, acorda sozinho quando o Deck abre no celular (o deck se anuncia na rede para isso). **Apagar tela** e **Ligar tela** apagam e acendem só a tela: o computador continua ligado e o deck segue respondendo — é o par certo para apagar e acender de volta pelo celular (depois de Suspender, o computador inteiro dorme e não ouve o celular). Na tomada, com o deck aberto, o computador não dorme sozinho, só a tela apaga; dá para mudar em **Configurações › Computador na tomada**.
- **Site:** digite um endereço ou escolha entre as **abas abertas agora** (Mac), os **favoritos** e os **sites mais visitados** dos navegadores do computador. O botão ganha **o ícone do próprio site** — e, quando o site tem um app oficial (WhatsApp, YouTube, Notion…), o deck busca também **o ícone oficial do app** e usa ele no lugar de ícones brancos ou pequenos demais. Dá para escolher em qual navegador abrir e, no Mac e no Windows, o que fazer em **Se o site já estiver aberto**: **Trazer a aba para frente** (o padrão, sem abas repetidas) ou **Abrir outra aba** a cada toque. No Windows o deck reconhece a aba pelo título (Gmail, YouTube, WhatsApp…) e isso vale para o endereço principal do site; se não reconhecer, abre uma aba nova.
- **Atalho de teclado:** clique no campo e aperte as teclas.
- **Arraste** os botões para mudar a ordem; solte numa aba lá em cima para levar para outra página. **+ Página** cria mais páginas — no celular, deslize para o lado.
- **Páginas:** arraste na lateral (ou nas abas lá em cima) para mudar a ordem — pelo teclado, ⌥/Alt+↑/↓. O **olho** ao lado do nome esconde a página do celular sem apagar (clique de novo para mostrar); no `config.json`, `"oculta": true` na página.
- Nome, emoji ou imagem própria, cor e confirmação (segundo toque) ficam no painel da direita.
- **Luz da borda** (Configurações, tema Preto): **Parada**, **Correndo** (a luz dá a volta na borda de cada botão) ou **Desligada**. Com Reduzir movimento ligado no celular, ela fica parada.
- A **versão** do deck aparece no alto do editor (ex.: v3.2.6) e em Configurações. Se ela não mudar depois de atualizar, o deck antigo ainda está aberto: feche a janela dele e abra de novo.

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
| Energia | desligar, reiniciar, suspender, bloquear (com segundo toque), apagar e ligar a tela | ✓ | ✓ | ✓⁵ |
| Ir para página | troca a página no celular | ✓ | ✓ | ✓ |
| Modo | Não perturbe, abre e fecha apps, volume e cronômetro no celular (seção 5) | ✓⁶ | ✓⁶ | ✓⁶ |
| Chamada | atender, recusar, mudo, câmera e encerrar no app da reunião (seção 5) | ✓ | ✓ | ✓⁷ |

¹ no Mac, com Safari, Chrome, Edge, Brave, Arc, Vivaldi ou Opera; no Windows, com Chrome, Edge, Firefox, Brave, Vivaldi ou Opera (pelo título da aba); no Linux abre uma aba nova ·
² precisa do `xdotool` (ou `wtype` no Wayland) · ³ `playerctl` · ⁴ `pactl` ou `wpctl` (já vêm na maioria das distros) · ⁵ `systemctl`/`loginctl` (systemd) ·
⁶ o Não perturbe liga no Mac pelo app Atalhos, no Windows direto (Não incomodar) e no Linux pelo GNOME · ⁷ precisa do `xdotool` (X11)

Quem prefere editar o `config.json` na mão ainda pode (o editor e o celular acompanham): há também `comando`, `sequencia`, `esperar`, e no Mac `atalho` (app Atalhos) e `applescript`. Valores por sistema: `"app": { "mac": "Safari", "windows": "Microsoft Edge", "linux": "Firefox" }`.

**Conferir tudo de uma vez.** Dê dois cliques em `Testar no Windows.bat` ou `Testar no Mac.command` (ou rode `python3 server.py --autoteste`; no Windows, `py server.py --autoteste`). O autoteste confere cada botão **sem apertar nenhum**: se o app existe e qual vai abrir, qual atalho de teclado sai naquele sistema (⌘ vira Ctrl no Windows), se o volume, o microfone e o “tocando agora” respondem e se falta alguma permissão. No Windows, ele liga e desliga o Não incomodar uma vez, para conferir que os modos conseguem. O resultado fica salvo em `autoteste.txt`, pronto para mandar para quem te ajuda.

---

## 5 · DJ, modos e chamadas

**DJ (mini player).** A página **DJ** mostra em tela cheia o que está tocando no computador — Spotify, Música, YouTube no navegador ou qualquer outro player — com capa, tempo, voltar, tocar/pausar, pular e volume; toque na barra para ir a outro ponto. Músicas mostram a capa do álbum e vídeos do YouTube, a miniatura do vídeo inteira (16:9). Nas outras páginas aparece um mini player no canto (toque nele para abrir o DJ). Qualquer página vira player no editor: **Página › Tipo da página › Player**.

**Com o celular bloqueado.** Toque no **cadeado** ao lado dos controles do DJ: a música do computador aparece na tela de bloqueio (e na cortina de notificações do Android) com capa, tocar/pausar, voltar, pular e a barra de tempo — os fones Bluetooth do celular também passam a controlar o computador. Para isso o deck toca um som inaudível no celular, então a música do próprio celular pausa enquanto ele estiver ligado; toque no cadeado de novo para desligar. A escolha fica salva no celular e volta no primeiro toque depois de abrir o deck. Funciona melhor no Chrome do Android; no iPhone, o iOS às vezes corta o som de apps da Tela de Início em segundo plano — se os controles sumirem, abra o deck e toque em qualquer lugar. O volume do computador continua sendo pelo deck: os botões de volume do celular mexem só no celular.

| Sistema | De onde o DJ lê |
|---|---|
| Mac | o mesmo "Tocando agora" da Central de Controle; se o macOS esconder, lê o Spotify e o Música direto. A miniatura do YouTube vem da aba aberta (Safari, Chrome, Edge, Brave, Arc, Vivaldi ou Opera) |
| Windows | os controles de mídia do Windows 10/11 (o mesmo do volume na barra de tarefas) |
| Linux | `playerctl` (qualquer player MPRIS); a miniatura do YouTube vem do endereço do vídeo |

**Modos.** Um toque deixa o computador pronto para o momento: liga o **Não perturbe**, abre apps e sites, fecha o que distrai, ajusta o volume, troca de página e mostra um **cronômetro** grande no celular (pausar, +5 min, encerrar, minimizar). Outro toque desliga e desfaz o Não perturbe; só um modo fica ligado por vez. Vêm prontos Foco (25 min), Trabalho, Estudos (50 min), Casa e Pausa (5 min).

| Sistema | Não perturbe |
|---|---|
| Mac | pelo app **Atalhos** (macOS 12+): crie uma vez os atalhos `Deck Foco Ligar` e `Deck Foco Desligar`, com a ação **Definir Foco** › Não Perturbe › Ligado / Desligado. Sem eles, o modo faz o resto e explica no celular |
| Windows | o deck liga o **Não incomodar** sozinho (no Windows 10, o Assistente de foco). Se o Windows não deixar, o modo faz o resto e lembra no celular de ligar em Win+N; o autoteste confere |
| Linux | no GNOME, sozinho |

**Chamadas.** Atender, recusar, mudo, câmera e encerrar: o deck traz a janela da reunião para frente e aperta o atalho do próprio app — Zoom, Teams, Meet, Webex, Discord e Slack. No automático ele usa a reunião aberta (Meet, Zoom, Teams, Webex ou FaceTime); para Discord e Slack, escolha o app no botão. Sem reunião aberta, o mudo silencia o microfone do computador. No Mac, ligações do FaceTime e do iPhone chegam no celular com **Atender** e **Recusar** quando o deck tem algum botão de Chamada (ele lê o aviso da Central de Notificações — experimental, pode parar se o macOS mudar esse aviso).

No `config.json`: `{"tipo": "modo", "nao_perturbe": true, "minutos": 25, "volume": 30, "abrir": ["Notion", "gmail.com"], "fechar": ["WhatsApp"], "pagina": "DJ"}`, `{"tipo": "chamada", "chamada": "mudo", "app": "zoom"}` e, numa página, `"tipo": "player"` ou `"oculta": true`.

---

## 6 · Permissões (só na primeira vez)

| Sistema | O que aparece | O que fazer |
|---|---|---|
| Mac | "Terminal quer controlar System Events" | Permitir |
| Mac | "Terminal quer controlar o Safari/Chrome" | Permitir — é o que lista as abas abertas e traz a aba para frente |
| Mac | "Terminal quer controlar o Spotify/Música" | Permitir — o DJ usa para ler e controlar esses apps |
| Mac | o modo não liga o Não perturbe | crie os atalhos `Deck Foco Ligar` e `Deck Foco Desligar` no app Atalhos (seção 5) |
| Mac | teclas/texto/mídia não funcionam | Ajustes do Sistema › Privacidade e Segurança › **Acessibilidade** → ativar o Terminal, fechar e abrir o Terminal |
| Windows | alerta do Firewall para o Python | marcar **Redes privadas** › Permitir (o Wi-Fi precisa estar como rede privada) |
| Linux | firewall `ufw` ativo | `sudo ufw allow 8787/tcp` |

---

## 7 · Se não conectar

- **O app abre com a tela preta** (ou "não foi possível conectar"): o celular não está achando o computador no endereço salvo. Feche o app no celular (deslize para cima) e abra de novo com o deck ligado. Se continuar, o endereço mudou — abra **Conectar celular** no editor: ele avisa quando o IP ou o nome do computador mudou e mostra o QR code novo. Para isso não acontecer mais, use o link **pelo nome** (padrão no Mac) ou o cabo USB.
- Confira se o celular e o computador estão **no mesmo Wi-Fi**. Wi-Fi de visitantes e redes de empresa costumam bloquear aparelhos entre si — nesse caso, use o **cabo USB** ou o **Bluetooth** (seção 2).
- No Mac, se o **Firewall** estiver bloqueando o Python, a janela Conectar celular avisa: Ajustes do Sistema › Rede › Firewall › Opções › Python › **Permitir conexões de entrada** (ou clique em Permitir no aviso que aparece ao ligar o deck).
- Para a tela do celular não apagar, aumente o **bloqueio automático** enquanto usa.

---

## 8 · Segurança e privacidade

- O editor e a página do QR code só abrem no próprio computador (`localhost`).
- Só quem tem o link do celular (com a chave secreta) aperta os botões, e mesmo assim só os botões que você criou — o celular nunca manda comandos livres. A chave fica na pasta de dados do seu usuário; para trocar e desconectar todos: `--novo-link`.
- As sugestões de sites vêm dos favoritos e do histórico dos navegadores **deste** computador e não saem dele. Ícones de sites são baixados do próprio site; para achar o ícone oficial do app, o deck consulta a busca pública da App Store (só o nome do site) e, se precisar, o serviço de ícones do Google (só o domínio). Nada sobre você é enviado; os ícones ficam guardados na pasta de dados por 7 dias.
- O deck guarda na pasta de dados do seu usuário só o endereço que cada celular usou para abrir (para avisar quando o IP ou o nome do computador mudar); nada disso sai do computador.
- O DJ guarda as capas das últimas músicas na pasta de dados; quando o player só informa um link da capa (Spotify lido direto no Mac, alguns players no Linux), o deck baixa a imagem desse link. O que está tocando não é enviado para lugar nenhum.
- Use em rede de confiança (casa/escritório): a conexão local não é criptografada.

**Opções:** `--porta 9000` · `--parear` · `--novo-link` · `--sem-navegador` · `--idioma en` (auto, pt ou en) · `--config outro.json`

Créditos: gerador de QR code [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) (MIT).
