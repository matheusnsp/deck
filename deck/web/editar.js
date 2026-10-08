(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };

  function h(tag, props) {
    var e = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'class') e.className = v;
        else if (k === 'text') e.textContent = v;
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') e.addEventListener(k.slice(2), v);
        else if (k === 'value' || k === 'checked' || k === 'disabled' || k === 'selected') e[k] = v;
        else e.setAttribute(k, v === true ? '' : v);
      });
    }
    for (var n = 2; n < arguments.length; n++) anexar(e, arguments[n]);
    return e;
  }
  function anexar(e, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { anexar(e, x); }); return; }
    e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }

  var ICONES = {
    desfazer: '<svg viewBox="0 0 24 24"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg>',
    refazer: '<svg viewBox="0 0 24 24"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/></svg>',
    mais: '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
    fechar: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    busca: '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg>',
    app: '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg>',
    site: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
    teclas: '<svg viewBox="0 0 24 24"><rect x="2.5" y="6" width="19" height="12" rx="2.5"/><path d="M6.5 10h.01M10 10h.01M14 10h.01M17.5 10h.01M7.5 14h9"/></svg>',
    texto: '<svg viewBox="0 0 24 24"><path d="M5 6.5V5h14v1.5M12 5v14M9 19h6"/></svg>',
    midia: '<svg viewBox="0 0 24 24"><path d="M5 5.5v13l8.5-6.5z"/><path d="M17 6v12M20.5 6v12"/></svg>',
    volume: '<svg viewBox="0 0 24 24"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/></svg>',
    microfone: '<svg viewBox="0 0 24 24"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/></svg>',
    pagina: '<svg viewBox="0 0 24 24"><rect x="3.5" y="5" width="17" height="14" rx="2.5"/><path d="M10 9.5 13 12l-3 2.5"/></svg>',
    energia: '<svg viewBox="0 0 24 24"><path d="M12 3.5v8"/><path d="M7.2 6.6a7 7 0 1 0 9.6 0"/></svg>',
    modo: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.6"/><circle cx="12" cy="12" r="1.2"/></svg>',
    chamada: '<svg viewBox="0 0 24 24"><path d="M5.2 4h3l1.7 4.3-2.2 1.4a11 11 0 0 0 6.6 6.6l1.4-2.2L20 15.8v3a1.6 1.6 0 0 1-1.7 1.6A16 16 0 0 1 3.6 5.7 1.6 1.6 0 0 1 5.2 4z"/></svg>',
    musica: '<svg viewBox="0 0 24 24"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>',
    livro: '<svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 18V5.5M8 7h8M8 10.5h5"/></svg>',
    outro: '<svg viewBox="0 0 24 24"><path d="M8 4H6.5A2.5 2.5 0 0 0 4 6.5v3L2.5 12 4 14.5v3A2.5 2.5 0 0 0 6.5 20H8M16 4h1.5A2.5 2.5 0 0 1 20 6.5v3l1.5 2.5-1.5 2.5v3a2.5 2.5 0 0 1-2.5 2.5H16"/></svg>',
    voltar: '<svg viewBox="0 0 24 24"><path d="M15 18 9 12l6-6"/></svg>',
    usuario: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="3.2"/><path d="M6.2 18.2a6.5 6.5 0 0 1 11.6 0"/></svg>',
    engrenagem: '<svg viewBox="0 0 24 24"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    lapis: '<svg viewBox="0 0 24 24"><path d="M4 20h4.5L19 9.5a2.1 2.1 0 0 0-3-3L5.5 17z"/><path d="m13.5 8 3 3"/></svg>',
    telefone: '<svg viewBox="0 0 24 24"><rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg>',
    grade: '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="6.5" height="6.5" rx="1.8"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.8"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.8"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.8"/></svg>',
    olho: '<svg viewBox="0 0 24 24"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    olhoFechado: '<svg viewBox="0 0 24 24"><path d="M10.6 5.6A9.7 9.7 0 0 1 12 5.5c6 0 9.5 6.5 9.5 6.5a17 17 0 0 1-2.4 3.2M6.6 6.6C3.9 8.3 2.5 12 2.5 12s3.5 6.5 9.5 6.5a9 9 0 0 0 5.4-1.8"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2M3.5 3.5l17 17"/></svg>',
  };
  function icone(nome) {
    var t = document.createElement('template');
    t.innerHTML = ICONES[nome];
    return t.content.firstChild;
  }

  var TIPOS_INFO = {
    app: { nome: 'App', desc: tr('Abre um programa'), icone: 'app' },
    site: { nome: 'Site', desc: tr('Abre uma aba no navegador'), icone: 'site' },
    teclas: { nome: tr('Atalho de teclado'), desc: tr('Aperta teclas, ex.: copiar'), icone: 'teclas' },
    texto: { nome: tr('Texto'), desc: tr('Digita uma frase pronta'), icone: 'texto' },
    midia: { nome: tr('Mídia'), desc: tr('Tocar, pausar e pular'), icone: 'midia' },
    volume: { nome: 'Volume', desc: tr('Subir, baixar ou mudo'), icone: 'volume' },
    microfone: { nome: tr('Microfone'), desc: tr('Liga e desliga o mudo'), icone: 'microfone' },
    energia: { nome: tr('Energia'), desc: tr('Desligar, reiniciar, suspender, bloquear'), icone: 'energia' },
    modo: { nome: tr('Modo'), desc: tr('Foco, trabalho, estudo: abre, fecha e silencia'), icone: 'modo' },
    chamada: { nome: tr('Chamada'), desc: tr('Atender, mudo, câmera, encerrar'), icone: 'chamada' },
    pagina: { nome: tr('Ir para página'), desc: tr('Troca a página no celular'), icone: 'pagina' },
  };
  var ORDEM_TIPOS = ['app', 'site', 'teclas', 'texto', 'midia', 'volume', 'microfone', 'modo', 'chamada', 'energia', 'pagina'];
  var CHAMADA = [['atender', tr('Atender'), '📞'], ['recusar', tr('Recusar'), '📵'], ['mudo', tr('Mudo'), '🔇'], ['camera', tr('Câmera'), '📷'], ['encerrar', tr('Encerrar'), '☎️']];
  var ALIAS_CHAMADA = { atender: 'atender', aceitar: 'atender', answer: 'atender', accept: 'atender', recusar: 'recusar', rejeitar: 'recusar',
    decline: 'recusar', reject: 'recusar', mudo: 'mudo', mutar: 'mudo', mute: 'mudo', unmute: 'mudo', desmutar: 'mudo', silenciar: 'mudo',
    microfone: 'mudo', camera: 'camera', video: 'camera', webcam: 'camera', cam: 'camera', encerrar: 'encerrar', desligar: 'encerrar',
    sair: 'encerrar', end: 'encerrar', leave: 'encerrar', hangup: 'encerrar', endcall: 'encerrar', leavecall: 'encerrar' };
  var APPS_CHAMADA = [['auto', tr('Automático (a reunião aberta)')], ['zoom', 'Zoom'], ['teams', 'Microsoft Teams'], ['meet', 'Google Meet'],
    ['facetime', 'FaceTime'], ['webex', 'Webex'], ['discord', 'Discord'], ['slack', 'Slack']];
  function chamadaDe(b) { var c = ALIAS_CHAMADA[simples(ler(b, 'chamada') || '').replace(/[^a-z]/g, '')]; return CHAMADA.filter(function (x) { return x[0] === c; })[0] || CHAMADA[2]; }
  var ROTULO_PADRAO = { teclas: tr('Teclas'), texto: tr('Texto'), app: 'App', link: 'Link', atalho: tr('Atalho'), comando: tr('Comando'),
    applescript: 'Script', midia: tr('Mídia'), volume: 'Volume', microfone: tr('Microfone'), energia: tr('Energia'), pagina: tr('Página'), sequencia: tr('Sequência'), esperar: tr('Esperar') };
  var NOMES_OUTROS = { comando: tr('comando do terminal'), applescript: 'AppleScript', atalho: tr('atalho do app Atalhos'),
    sequencia: tr('sequência de ações'), esperar: tr('espera') };
  var MIDIA = [['anterior', tr('Anterior'), '⏮️'], ['play', tr('Tocar/Pausar'), '⏯️'], ['proxima', tr('Próxima'), '⏭️']];
  var ALIAS_MIDIA = { play: 'play', pause: 'play', playpause: 'play', 'play/pause': 'play', play_pause: 'play', tocar: 'play', pausar: 'play',
    tocar_pausar: 'play', 'tocar/pausar': 'play', proxima: 'proxima', proximo: 'proxima', next: 'proxima', avancar: 'proxima', seguinte: 'proxima',
    anterior: 'anterior', previous: 'anterior', prev: 'anterior', voltar: 'anterior' };
  var VOLUME = [['subir', tr('Subir'), '🔊', 'Volume +'], ['descer', tr('Baixar'), '🔉', 'Volume −'], ['mudo', tr('Mudo'), '🔇', tr('Mudo')]];
  var ENERGIA = [['desligar', tr('Desligar'), '⏻'], ['reiniciar', tr('Reiniciar'), '🔄'], ['suspender', tr('Suspender'), '🌙'], ['bloquear', tr('Bloquear'), '🔒']];
  var ALIAS_ENERGIA = { desligar: 'desligar', shutdown: 'desligar', poweroff: 'desligar', apagar: 'desligar', off: 'desligar',
    reiniciar: 'reiniciar', restart: 'reiniciar', reboot: 'reiniciar', suspender: 'suspender', dormir: 'suspender', sleep: 'suspender',
    repouso: 'suspender', hibernar: 'suspender', bloquear: 'bloquear', lock: 'bloquear', travar: 'bloquear', tela: 'bloquear', bloquear_tela: 'bloquear' };
  function energiaDe(b) { var x = ENERGIA.filter(function (e) { return e[0] === ALIAS_ENERGIA[simples(ler(b, 'energia') || 'desligar')]; })[0]; return x || ENERGIA[0]; }
  var ALIAS_VOLUME = { subir: 'subir', aumentar: 'subir', mais: 'subir', '+': 'subir', up: 'subir', descer: 'descer', baixar: 'descer',
    diminuir: 'descer', menos: 'descer', '-': 'descer', down: 'descer', mudo: 'mudo', mute: 'mudo', silenciar: 'mudo' };
  var CAMPOS = {
    titulo: ['titulo', 'título', 'nome', 'label'],
    icone: ['icone', 'ícone', 'emoji', 'icon'],
    imagem: ['imagem', 'image'],
    cor: ['cor', 'color'],
    confirmar: ['confirmar', 'confirm'],
    app: ['app', 'nome', 'programa'],
    url: ['url', 'link'],
    teclas: ['teclas'],
    texto: ['texto', 'text'],
    midia: ['midia', 'mídia', 'acao', 'ação'],
    volume: ['volume', 'acao', 'ação'],
    pagina: ['pagina', 'página', 'destino'],
    navegador: ['navegador', 'browser'],
    aba: ['aba', 'reaproveitar'],
    tipo: ['tipo'],
    abrir: ['abrir', 'open'],
    fechar: ['fechar', 'close'],
    nao_perturbe: ['nao_perturbe', 'não_perturbe', 'naoPerturbe', 'dnd'],
    minutos: ['minutos', 'timer', 'cronometro', 'cronômetro'],
    chamada: ['chamada'],
  };
  var GRADES = [[3, 2], [4, 2], [5, 2], [6, 2], [3, 3], [4, 3], [5, 3], [6, 3], [4, 4], [5, 4]];
  var CORES_ORDEM = ['vermelho', 'laranja', 'amarelo', 'verde', 'menta', 'ciano', 'azul', 'anil', 'roxo', 'rosa', 'marrom', 'cinza', 'preto', 'branco'];

  var S = {
    token: null, sistema: 'mac', nomeSistema: 'Mac', computador: '', tipos: {}, chaves: {}, cores: {},
    cfg: null, base: null, erroConfig: null, appVersao: null, geracao: -1,
    visao: null, mapaImg: {}, mapaImg2: {}, titulosSites: {},
    pag: 0, sel: null, tipoNovo: null,
    undo: [], redo: [], grupo: null,
    sujo: false, salvando: false, deNovo: false, timerSalvar: null, erroSalvar: null,
    apps: null, appsCarregando: false, appsPedindo: false, busca: '', seletor: null,
    sites: null, sitesCarregando: false, sitesPedindo: false, buscaSite: '', seletorSite: null, navegadores: [],
    online: true, status: null, tela: null, filtro: '', iconesPagina: [], ultimoAdd: 'app',
  };
  var SUBTITULOS = {
    estrela: tr('Seus atalhos mais usados, sempre à mão.'),
    grade: tr('Os programas que você mais abre.'),
    globo: tr('Suas abas e sites, com o ícone de cada um.'),
    play: tr('Tocar, pausar e controlar o som.'),
    raio: tr('Atalhos que aceleram o seu dia.'),
    musica: tr('Suas músicas e players, num toque.'),
    chat: tr('Conversas e reuniões, sem procurar a aba.'),
    maleta: tr('O que você usa no trabalho.'),
    camera: tr('Captura, câmera e transmissão.'),
    codigo: tr('Ferramentas de quem programa.'),
    jogo: tr('Jogos e lançadores.'),
    casa: tr('Suas coisas de casa.'),
    lua: tr('Um toque deixa o computador do jeito certo para cada momento.'),
    video: tr('Atender, mutar e sair das chamadas sem procurar a janela.'),
  };

  function api(caminho, opcoes) {
    opcoes = opcoes || {};
    var temCorpo = opcoes.corpo !== undefined;
    var cab = { 'X-Deck-Token': S.token || '' };
    if (temCorpo) cab['Content-Type'] = 'application/json';
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, opcoes.limite || 15000);
    return fetch(caminho, {
      method: temCorpo ? 'POST' : 'GET', headers: cab, cache: 'no-store', signal: ctl.signal,
      body: temCorpo ? JSON.stringify(opcoes.corpo) : undefined,
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) {
          var e = new Error(d.mensagem || ('Erro ' + r.status));
          e.status = r.status;
          e.dados = d;
          throw e;
        }
        return d;
      });
    }).finally(function () { clearTimeout(timer); });
  }

  function comToken(url) {
    return url + (url.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(S.token || '');
  }

  function semAcento(s) {
    return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }
  function simples(s) {
    return String(s).normalize('NFD').replace(/[^\x00-\x7f]/g, '').trim().toLowerCase().replace(/\s+/g, '_');
  }
  function ehObjeto(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
  function ehPorSistema(v) {
    if (!ehObjeto(v)) return false;
    var ks = Object.keys(v);
    return ks.length > 0 && ks.every(function (k) { return !!S.chaves[simples(k)]; });
  }
  var FALTA = {};
  function porSistema(v) {
    if (!ehPorSistema(v)) return v;
    var mapa = {};
    Object.keys(v).forEach(function (k) { mapa[S.chaves[simples(k)]] = v[k]; });
    if (Object.prototype.hasOwnProperty.call(mapa, S.sistema)) return mapa[S.sistema];
    return Object.prototype.hasOwnProperty.call(mapa, 'padrao') ? mapa.padrao : FALTA;
  }
  function chaveUsada(b, campo) {
    var lista = CAMPOS[campo] || [campo];
    for (var n = 0; n < lista.length; n++) {
      if (b[lista[n]] !== undefined && b[lista[n]] !== null) return lista[n];
    }
    return null;
  }
  function ler(b, campo) {
    if (!ehObjeto(b)) return undefined;
    var k = chaveUsada(b, campo);
    if (!k) return undefined;
    var v = porSistema(b[k]);
    return v === FALTA ? undefined : v;
  }
  function escrever(b, campo, valor) {
    var k = chaveUsada(b, campo);
    var vazio = valor === undefined || valor === null || valor === '' || (valor === false && campo !== 'aba' && campo !== 'confirmar');
    if (k && ehPorSistema(b[k])) {
      var obj = b[k];
      var alvo = null;
      Object.keys(obj).forEach(function (kk) { if (S.chaves[simples(kk)] === S.sistema) alvo = kk; });
      if (vazio) {
        if (alvo) delete obj[alvo];
        if (!Object.keys(obj).length) delete b[k];
      } else {
        obj[alvo || S.sistema] = valor;
      }
      return;
    }
    (CAMPOS[campo] || [campo]).forEach(function (kk) { if (kk !== 'nome' || campo === 'nome') delete b[kk]; });
    if (!vazio) b[campo] = valor;
  }
  function tipoCanon(b) {
    var t = ler(b, 'tipo');
    return typeof t === 'string' ? (S.tipos[simples(t)] || null) : null;
  }
  function tipoEditor(b) {
    var t = tipoCanon(b);
    if (t === 'link') return 'site';
    return TIPOS_INFO[t] ? t : 'outro';
  }
  function temEsquema(u) { return /^[a-zA-Z][\w+.-]*:/.test(u) && !/^[\w.-]+:\d+(\/|$)/.test(u); }
  function normalizarUrl(u) {
    u = String(u || '').trim();
    if (!u) return '';
    return temEsquema(u) ? u : 'https://' + u;
  }
  function listaApps(b) {
    var v = ler(b, 'app');
    return (Array.isArray(v) ? v : [v]).filter(function (x) { return typeof x === 'string' && x.trim(); })
      .map(function (x) { return x.trim(); });
  }
  function pedidoDe(b) {
    var t = tipoCanon(b);
    if (t === 'app') {
      var lista = listaApps(b);
      return lista.length ? 'app:' + lista.join('\n') : null;
    }
    if (t === 'link') {
      var u = ler(b, 'url');
      if (typeof u !== 'string' || !u.trim()) return null;
      u = normalizarUrl(u);
      return /^https?:/i.test(u) ? 'site:' + u : null;
    }
    return null;
  }
  function limitar(v, min, max, padrao) {
    var n = parseInt(v, 10);
    if (isNaN(n)) n = padrao;
    return Math.max(min, Math.min(max, n));
  }
  function grade() {
    var g = ehObjeto(S.cfg.grade) ? S.cfg.grade : {};
    return { c: limitar(g.colunas, 1, 8, 4), l: limitar(g.linhas, 1, 8, 2) };
  }
  function cap() { var g = grade(); return g.c * g.l; }
  function paginas() { return S.cfg.paginas; }
  function botoes(p) { return paginas()[p].botoes; }
  function vazioB(b) { return !ehObjeto(b) || !Object.keys(b).length; }
  function botaoEm(p, i) {
    if (!paginas()[p]) return null;
    var b = botoes(p)[i];
    return vazioB(b) ? null : b;
  }
  function colocar(p, i, b) {
    var arr = botoes(p);
    while (arr.length <= i) arr.push(null);
    arr[i] = b || null;
  }
  function nomePagina(p) {
    var pg = paginas()[p];
    return (pg && pg.nome !== undefined && pg.nome !== null && String(pg.nome).trim()) ? String(pg.nome) : 'Página ' + (p + 1);
  }

  function normalizarCfg(c) {
    if (!ehObjeto(c)) c = {};
    if (!Array.isArray(c.paginas) && Array.isArray(c['páginas'])) { c.paginas = c['páginas']; delete c['páginas']; }
    if (!Array.isArray(c.paginas)) c.paginas = [];
    c.paginas = c.paginas.map(function (pg, n) {
      if (!ehObjeto(pg)) pg = { nome: 'Página ' + (n + 1), botoes: [] };
      if (!Array.isArray(pg.botoes) && Array.isArray(pg['botões'])) { pg.botoes = pg['botões']; delete pg['botões']; }
      if (!Array.isArray(pg.botoes)) pg.botoes = [];
      return pg;
    });
    if (!c.paginas.length) c.paginas.push({ nome: 'Apps', botoes: [] });
    return c;
  }

  function limparFim() {
    paginas().forEach(function (pg) {
      while (pg.botoes.length && vazioB(pg.botoes[pg.botoes.length - 1])) pg.botoes.pop();
      for (var i = 0; i < pg.botoes.length; i++) if (vazioB(pg.botoes[i])) pg.botoes[i] = null;
    });
  }

  function nomeUnico(desejado, ignorar) {
    var base = String(desejado || '').trim().slice(0, 24) || 'Página';
    var usados = {};
    paginas().forEach(function (pg, p) { if (p !== ignorar) usados[simples(nomePagina(p))] = true; });
    if (!usados[simples(base)]) return base;
    for (var n = 2; n < 100; n++) {
      var c = base.slice(0, 21) + ' ' + n;
      if (!usados[simples(c)]) return c;
    }
    return base;
  }

  var CORES_HEX = /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i;
  function corDe(v) {
    if (v === undefined || v === null || v === '') return null;
    var s = String(v).trim();
    if (S.cores[s.toLowerCase()]) return S.cores[s.toLowerCase()];
    if (S.cores[simples(s)]) return S.cores[simples(s)];
    var m = CORES_HEX.exec(s);
    if (!m) return null;
    var x = m[1];
    if (x.length === 3) x = x.split('').map(function (c) { return c + c; }).join('');
    return '#' + x.toLowerCase();
  }
  function corClara(hex) {
    var m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
    if (!m) return false;
    var v = parseInt(m[1], 16);
    var lin = [(v >> 16) & 255, (v >> 8) & 255, v & 255].map(function (c) {
      c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2] > 0.42;
  }
  function matiz(s) {
    var n = 0;
    String(s || '').split('').forEach(function (c) { n = (n * 31 + c.charCodeAt(0)) % 3600; });
    return n % 360;
  }
  var segmentador = (typeof Intl !== 'undefined' && Intl.Segmenter) ? new Intl.Segmenter('pt', { granularity: 'grapheme' }) : null;
  function letras(s) {
    s = String(s || '');
    return segmentador ? Array.from(segmentador.segment(s)).map(function (x) { return x.segment; }) : Array.from(s);
  }
  var reEmoji = /\p{Extended_Pictographic}|⃣|️|\p{Regional_Indicator}/u;

  function imgDe(b) {
    var imagem = ler(b, 'imagem');
    if (typeof imagem === 'string' && imagem) return '/icones/' + encodeURIComponent(imagem);
    if (ler(b, 'icone')) return null;
    var p = pedidoDe(b);
    return p ? (S.mapaImg[p] || null) : null;
  }

  function tituloDe(b) {
    var t = ler(b, 'titulo');
    return (t === undefined || t === null) ? '' : String(t).slice(0, 40);
  }

  function teclaEl(b, info) {
    info = info || {};
    var t = h('div', { class: 'tecla' });
    var cor = corDe(ler(b, 'cor'));
    if (cor) {
      t.style.setProperty('--c', cor);
      if (window.triplaDoHex && triplaDoHex(cor)) t.style.setProperty('--tom', triplaDoHex(cor));
      t.classList.add(corClara(cor) ? 'clara' : 'colorida');
    }
    var tipo = tipoCanon(b);
    var titulo = tituloDe(b);
    var ic = ler(b, 'icone');
    ic = (ic === undefined || ic === null || ic === '') ? '' : String(ic).slice(0, 16);
    var img = info.img;
    var auto = tipo === 'app' || tipo === 'link';
    if (!titulo && !ic && !ler(b, 'imagem')) titulo = ROTULO_PADRAO[tipo] || tr('Botão');
    var ico = null;
    if (img) {
      var figura = h('img', { src: comToken(img), alt: '', draggable: 'false' });
      ico = h('span', { class: 'ico figura' }, figura);
      t.classList.add('com-figura');
      var pintar = function () { if (window.tomDaImagem && !cor) tomDaImagem(figura, function (tom) { t.style.setProperty('--tom', tripla(tom)); }); };
      pintar();
      if (info.img2 && window.escolherFigura) escolherFigura(figura, comToken(info.img2), function () { figura.addEventListener('load', pintar, { once: true }); });
    } else if (ic) {
      ico = h('span', { class: 'ico', text: ic });
      if (!reEmoji.test(ic) || letras(ic).length > 2) ico.classList.add('txt');
    } else if (auto) {
      var base = titulo || (listaApps(b)[0] || '') || ROTULO_PADRAO[tipo];
      ico = h('span', { class: 'ico letra', text: (letras(base.trim())[0] || '?').toUpperCase() });
      ico.style.setProperty('--matiz', matiz(base));
      if (window.triplaDoMatiz && !cor) t.style.setProperty('--tom', triplaDoMatiz(matiz(base)));
      t.classList.add('com-figura');
    }
    if (ico) t.appendChild(ico);
    if (titulo) t.appendChild(h('span', { class: 'rot', text: titulo }));
    if (!ico) t.classList.add('so-texto');
    if (info.erro) t.appendChild(h('span', { class: 'alerta', text: '!', title: info.erro }));
    if (info.pendente) t.appendChild(h('span', { class: 'carregando-ico' }));
    if (info.fora) t.classList.add('fora');
    if (info.card) {
      var pontos = h('span', { class: 'pontos', role: 'button', 'aria-label': 'Opções', title: 'Opções' });
      pontos.innerHTML = window.SVG_PONTOS || '';
      t.appendChild(pontos);
    }
    if (window.SVG_SETA) {
      var seta = h('span', { class: 'seta' });
      seta.innerHTML = SVG_SETA;
      t.appendChild(seta);
    }
    return t;
  }

  function visaoDe(p, i) {
    if (S.sujo || !S.visao || !S.visao.paginas[p]) return null;
    return S.visao.paginas[p].botoes[i] || null;
  }
  function infoDe(p, i, b) {
    var info = { img: imgDe(b) };
    var v = visaoDe(p, i);
    if (v) {
      if (v.erro) info.erro = v.erro;
      if (v.fora) info.fora = v.fora;
      if (v.pendente && !info.img) info.pendente = true;
      if (v.img2 && info.img === v.img) info.img2 = v.img2;
    }
    if (!info.img2) {
      var ped = pedidoDe(b);
      if (ped && S.mapaImg2[ped] && S.mapaImg[ped] === info.img) info.img2 = S.mapaImg2[ped];
    }
    return info;
  }

  function aplicarVisao(v) {
    S.visao = v;
    var pendente = false;
    (v && v.paginas || []).forEach(function (pg) {
      (pg.botoes || []).forEach(function (b) {
        if (!b) return;
        if (b.pedido && b.img) { S.mapaImg[b.pedido] = b.img; S.mapaImg2[b.pedido] = b.img2 || null; }
        if (b.pendente) pendente = true;
      });
    });
    clearTimeout(S.timerVisao);
    if (pendente) S.timerVisao = setTimeout(atualizarVisao, 1300);
  }
  function atualizarVisao() {
    if (S.sujo || S.salvando) { S.timerVisao = setTimeout(atualizarVisao, 900); return; }
    api('/api/editor/visao', { limite: 8000 }).then(function (r) {
      if (r.base !== S.base || S.sujo) return;
      S.geracao = r.geracao;
      aplicarVisao(r.visao);
      redesenharTeclas();
    }).catch(function () { return null; });
  }

  function mostrarSalvo(estado, msg) {
    var e = $('#salvo');
    e.className = 'salvo' + (estado === 'salvo' ? ' ok' : estado === 'erro' ? ' erro' : '');
    e.textContent = estado === 'salvando' ? tr('Salvando…') : estado === 'salvo' ? tr('Salvo') : estado === 'erro' ? (msg || tr('Não salvou')) : '';
  }

  function agendarSalvar() {
    S.sujo = true;
    mostrarSalvo('salvando');
    clearTimeout(S.timerSalvar);
    S.timerSalvar = setTimeout(salvar, 320);
  }

  function salvar() {
    if (S.salvando) { S.deNovo = true; return; }
    limparFim();
    var enviado = JSON.stringify(S.cfg);
    S.salvando = true;
    api('/api/editor', { corpo: { base: S.base, config: JSON.parse(enviado) }, limite: 20000 }).then(function (r) {
      S.base = r.base;
      S.geracao = r.geracao;
      S.erroConfig = r.erroConfig || null;
      S.erroSalvar = null;
      if (JSON.stringify(S.cfg) === enviado && !S.deNovo) {
        S.sujo = false;
        mostrarSalvo('salvo');
        if (r.idioma && window.IDIOMA && r.idioma !== window.IDIOMA) { location.reload(); return; }
      }
      aplicarVisao(r.visao);
      mostrarFaixa();
      redesenharTeclas();
    }).catch(function (e) {
      if (e.status === 409 && e.dados && e.dados.config) {
        S.sujo = false;
        S.undo = [];
        S.redo = [];
        aplicarDados(e.dados);
        toast(e.dados.mensagem || tr('O config.json mudou fora do editor — carreguei a versão nova.'));
        return;
      }
      S.erroSalvar = e.message;
      mostrarSalvo('erro', e.status === 400 ? tr('Não salvou') : tr('Sem conexão'));
      if (e.status === 400) toast(e.message, null, null, 'erro');
      else setTimeout(function () { if (S.sujo) salvar(); }, 2500);
    }).finally(function () {
      S.salvando = false;
      if (S.deNovo) { S.deNovo = false; salvar(); }
    });
  }

  function mudar(fn, op) {
    op = op || {};
    var g = op.grupo || null;
    if (!g || g !== S.grupo) {
      S.undo.push(JSON.stringify(S.cfg));
      if (S.undo.length > 150) S.undo.shift();
      S.redo = [];
    }
    S.grupo = g;
    fn();
    agendarSalvar();
    if (op.painel === false) {
      aplicarTema();
      desenharAbas();
      desenharCabecalho();
      desenharPalco();
      desenharPilulas();
      atualizarPrevia();
      atualizarUndo();
    } else {
      desenhar();
    }
  }

  function trocarEstado(json) {
    S.cfg = normalizarCfg(JSON.parse(json));
    S.grupo = null;
    corrigirSelecao();
    $('#nome-deck').value = S.cfg.nome || 'Deck';
    agendarSalvar();
    desenhar();
  }
  function desfazer() {
    if (!S.undo.length) return;
    S.redo.push(JSON.stringify(S.cfg));
    trocarEstado(S.undo.pop());
  }
  function refazer() {
    if (!S.redo.length) return;
    S.undo.push(JSON.stringify(S.cfg));
    trocarEstado(S.redo.pop());
  }
  function atualizarUndo() {
    var d = $('#desfazer'), r = $('#refazer');
    if (d) d.disabled = !S.undo.length;
    if (r) r.disabled = !S.redo.length;
  }
  function corrigirSelecao() {
    if (S.pag >= paginas().length) S.pag = paginas().length - 1;
    if (S.pag < 0) S.pag = 0;
    if (S.sel && (S.sel.p >= paginas().length || (!S.sel.novo && !botaoEm(S.sel.p, S.sel.i)) || (S.sel.novo && botaoEm(S.sel.p, S.sel.i)))) {
      S.sel = null;
      S.tipoNovo = null;
    }
  }

  var timerToast = null;
  function toast(msg, acao, fn, tipo) {
    var t = $('#toast');
    $('#toast-txt').textContent = msg;
    var b = $('#toast-acao');
    b.hidden = !acao;
    b.textContent = acao || '';
    b.onclick = function () { esconderToast(); if (fn) fn(); };
    t.className = 'toast mostra' + (tipo === 'erro' ? ' erro' : '');
    clearTimeout(timerToast);
    timerToast = setTimeout(esconderToast, acao ? 6500 : tipo === 'erro' ? 6000 : 3800);
  }
  function esconderToast() { $('#toast').className = 'toast'; }

  function mostrarFaixa() {
    var f = $('#faixa');
    if (!S.online) {
      f.className = 'faixa grave';
      f.textContent = tr('Sem conexão com o deck. Ele foi desligado? Ligue de novo no computador — o que você mudar aqui é salvo quando ele voltar.');
      f.hidden = false;
    } else if (S.erroConfig) {
      f.className = 'faixa';
      f.textContent = tr('O config.json tem um erro ({e}). Aqui aparece a última versão que funcionava; se você mudar algo no editor, o arquivo é corrigido.', { e: S.erroConfig.replace(/^config\.json\s*/, '') });
      f.hidden = false;
    } else {
      f.hidden = true;
    }
  }

  function desenhar() {
    if (!S.cfg) return;
    aplicarTema();
    desenharAbas();
    desenharCabecalho();
    desenharPalco();
    desenharPilulas();
    desenharPainel();
    atualizarUndo();
  }

  function aplicarTema() {
    var t = S.cfg && S.cfg.tema === 'normal' ? 'normal' : 'preto';
    document.documentElement.setAttribute('data-tema', t);
  }

  function iconeDaPagina(p) {
    var pg = paginas()[p] || {};
    var chave = typeof pg.icone === 'string' && window.ICONES_PAGINA && ICONES_PAGINA[pg.icone] ? pg.icone : null;
    if (!chave && window.sugerirIconePagina) chave = sugerirIconePagina(nomePagina(p), p);
    return chave || 'pasta';
  }

  function usadosNa(p) {
    if (ehPlayer(p)) return 0;
    return botoes(p).filter(function (b) { return !vazioB(b); }).length;
  }

  function ehOculta(p) {
    var pg = paginas()[p];
    return !!pg && pg.oculta === true;
  }

  function alternarOculta(p) {
    var ocultar = !ehOculta(p);
    var nome = nomePagina(p);
    mudar(function () {
      if (ocultar) paginas()[p].oculta = true;
      else delete paginas()[p].oculta;
    });
    var visiveis = paginas().filter(function (pg) { return pg.oculta !== true; }).length;
    var msg = !ocultar ? tr('“{p}” voltou para o celular.', { p: nome })
      : visiveis ? tr('“{p}” não aparece mais no celular. Continua aqui no editor.', { p: nome })
        : tr('Todas as páginas estão ocultas: o celular fica vazio.');
    toast(msg, tr('Desfazer'), desfazer);
  }

  function ehPlayer(p) {
    var pg = paginas()[p];
    return !!pg && typeof pg.tipo === 'string' && ['player', 'dj', 'musica', 'tocando'].indexOf(simples(pg.tipo)) >= 0;
  }

  function arrastandoPagina() {
    return !!(arraste && arraste.ativo && (arraste.tipo === 'aba' || arraste.tipo === 'pilula'));
  }

  function desenharAbas() {
    var c = $('#abas');
    if (S.renomeando !== undefined && S.renomeando !== null) return;
    if (arrastandoPagina()) { S.redesenharDepois = true; return; }
    c.textContent = '';
    paginas().forEach(function (pg, p) {
      var oculta = ehOculta(p);
      var a = h('button', { type: 'button', class: 'aba' + (oculta ? ' oculta' : ''), role: 'tab', 'aria-selected': String(p === S.pag),
        title: oculta ? tr('Oculta no celular · arraste para mudar a ordem') : tr('Arraste para mudar a ordem · clique duas vezes para renomear') },
        window.iconePagina ? iconePagina(iconeDaPagina(p)) : null,
        h('span', { class: 'nome', text: nomePagina(p) }),
        h('span', { class: 'qtd', text: String(usadosNa(p)) }));
      a.dataset.p = p;
      var rotulo = oculta ? tr('Mostrar “{p}” no celular', { p: nomePagina(p) }) : tr('Ocultar “{p}” do celular', { p: nomePagina(p) });
      var olho = h('button', { type: 'button', class: 'olho', title: rotulo, 'aria-label': rotulo, 'aria-pressed': String(oculta) }, icone(oculta ? 'olhoFechado' : 'olho'));
      olho.dataset.p = p;
      var linha = h('div', { class: 'aba-linha' + (oculta ? ' oculta' : ''), role: 'presentation' }, a, olho);
      linha.dataset.p = p;
      c.appendChild(linha);
    });
  }

  function desenharCabecalho() {
    var p = S.pag;
    var tile = $('#pagina-tile');
    tile.textContent = '';
    var chave = iconeDaPagina(p);
    if (window.iconePagina) {
      var ic = iconePagina(chave);
      if (chave !== 'estrela' && chave !== 'coracao') ic.classList.add('vazado');
      tile.appendChild(ic);
    }
    $('#titulo-pagina').textContent = nomePagina(p);
    var selo = $('#pagina-oculta');
    if (selo) selo.hidden = !ehOculta(p);
    document.querySelectorAll('.segmentos-add button').forEach(function (b) {
      b.disabled = ehPlayer(p);
      if (b.disabled) b.setAttribute('aria-pressed', 'false');
    });
    if (ehPlayer(p)) {
      $('#sub-pagina').textContent = tr('Player (modo DJ): mostra o que está tocando no computador, com capa e controles.');
      document.title = S.cfg.nome || 'Deck';
      return;
    }
    var usados = usadosNa(p);
    var livres = Math.max(0, cap() - usados);
    $('#sub-pagina').textContent = SUBTITULOS[chave] || (usados === 0
      ? tr('Página vazia — adicione um app ou um site.')
      : (usados === 1 ? tr('1 botão') : tr('{n} botões', { n: usados })) + ' · ' + (livres ? (livres === 1 ? tr('1 espaço livre') : tr('{n} espaços livres', { n: livres })) : tr('página cheia')));
    document.title = S.cfg.nome || 'Deck';
    document.querySelectorAll('.segmentos-add button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.add === S.ultimoAdd)); });
  }

  function desenharPilulas() {
    if (arrastandoPagina()) { S.redesenharDepois = true; return; }
    var capacidade = cap();
    ['#pilulas', '#pilulas-topo'].forEach(function (id) {
      var c = $(id);
      c.textContent = '';
      paginas().forEach(function (pg, p) {
        var partes = ehPlayer(p) ? 1 : Math.max(1, Math.ceil(botoes(p).length / capacidade));
        for (var k = 0; k < partes; k++) {
          var b = h('button', { type: 'button', role: 'tab', class: ehOculta(p) ? 'oculta' : null, 'aria-selected': String(p === S.pag && k === 0),
            title: ehOculta(p) ? tr('Oculta no celular · arraste para mudar a ordem') : tr('Arraste para mudar a ordem') },
            window.iconePagina ? iconePagina(iconeDaPagina(p)) : null,
            h('span', { text: partes > 1 ? nomePagina(p) + ' ' + (k + 1) : nomePagina(p) }));
          b.dataset.p = p;
          c.appendChild(b);
        }
      });
    });
    $('#pilulas').parentNode.hidden = $('#pilulas').children.length < 2;
  }

  function redesenharTeclas() {
    if (arraste && arraste.ativo) { S.redesenharDepois = true; return; }
    desenharPalco();
    atualizarPrevia();
  }

  function bate(b, termo) {
    if (!termo) return true;
    var alvo = semAcento(tituloDe(b) + ' ' + (ler(b, 'url') || '') + ' ' + listaApps(b).join(' '));
    return alvo.indexOf(termo) >= 0;
  }

  function desenharPalco() {
    var cont = $('#aparelhos');
    if (ehPlayer(S.pag)) { desenharPrevisaoPlayer(cont); return; }
    var g = grade();
    var capacidade = g.c * g.l;
    var arr = botoes(S.pag);
    var telas = Math.max(1, Math.ceil(arr.length / capacidade));
    var termo = semAcento(S.filtro.trim());
    cont.textContent = '';
    for (var tl = 0; tl < telas; tl++) {
      var grid = h('div', { class: 'teclas' });
      grid.style.setProperty('--cols', g.c);
      var cheia = true;
      for (var n = 0; n < capacidade; n++) {
        var i = tl * capacidade + n;
        var b = botaoEm(S.pag, i);
        if (!b) cheia = false;
        var slot = slotEl(S.pag, i);
        if (b && termo && !bate(b, termo)) slot.classList.add('escondido');
        grid.appendChild(slot);
      }
      if (cheia) grid.classList.add('cheia');
      if (tl > 0) {
        cont.appendChild(h('p', { class: 'continua-nota', text: tr('Continuação — no celular vira a página “{p}” (tem mais botões do que cabem na grade).', { p: nomePagina(S.pag) + ' ' + (tl + 1) }) }));
      }
      cont.appendChild(grid);
    }
    if (termo) {
      var fora = [];
      paginas().forEach(function (pg, p) {
        if (p === S.pag) return;
        botoes(p).forEach(function (b, i) { if (!vazioB(b) && bate(b, termo)) fora.push({ p: p, i: i, b: b }); });
      });
      if (fora.length) {
        var lista = h('div', { class: 'achados' }, h('span', { class: 'rotulo', style: 'margin:0 6px 0 0', text: tr('Em outras páginas') }));
        fora.slice(0, 12).forEach(function (x) {
          var chip = h('button', { type: 'button', class: 'achado' }, h('b', { text: tituloDe(x.b) || tr('Botão') }), h('span', { text: nomePagina(x.p) }));
          chip.addEventListener('click', function () { S.pag = x.p; S.sel = { p: x.p, i: x.i }; S.tela = null; S.tipoNovo = null; desenhar(); });
          lista.appendChild(chip);
        });
        cont.appendChild(lista);
      }
    }
    medirTeclas();
  }

  var previa = { el: null, timer: null, dados: null, em: 0 };
  function desenharPrevisaoPlayer(cont) {
    cont.textContent = '';
    var capa = h('div', { class: 'pp-capa' }, icone('musica'));
    var app = h('div', { class: 'pp-app' });
    var titulo = h('div', { class: 'pp-titulo' });
    var artista = h('div', { class: 'pp-artista' });
    var cheio = h('div', { class: 'pp-cheio' });
    var barra = h('div', { class: 'pp-barra' }, cheio);
    var tempos = h('div', { class: 'pp-tempos' }, h('span'), h('span'));
    var caixa = h('div', { class: 'previa-player' },
      h('div', { class: 'pp-fundo' }), capa,
      h('div', { class: 'pp-info' }, app, titulo, artista, barra, tempos));
    var nota = h('p', { class: 'continua-nota', text: tr('No celular, esta página vira um player em tela cheia com capa, tempo, pular, voltar e volume. Ela aparece quando você desliza até ela ou toca no mini player do canto.') });
    cont.append(caixa, nota);
    previa.el = { caixa: caixa, capa: capa, app: app, titulo: titulo, artista: artista, cheio: cheio, tempos: tempos };
    pintarPrevia();
    pedirPrevia();
  }

  function pintarPrevia() {
    var e = previa.el;
    if (!e || !document.body.contains(e.caixa)) return;
    var t = previa.dados || {};
    e.caixa.classList.toggle('sem-midia', !t.tem);
    e.app.textContent = t.tem ? (t.app || '') : tr('Nada tocando agora');
    e.titulo.textContent = t.tem ? (t.titulo || '') : tr('Dê play em qualquer player do computador para ver aqui.');
    e.artista.textContent = t.tem ? [t.artista, t.album].filter(Boolean).join(' · ') : '';
    var url = t.tem && t.capa ? comToken(t.capa) : null;
    var img = e.capa.querySelector('img');
    if (url) {
      if (!img) {
        img = h('img', { alt: '' });
        img.addEventListener('load', function () { e.capa.classList.toggle('larga', img.naturalWidth > img.naturalHeight * 1.3); });
        e.capa.appendChild(img);
      }
      if (img.getAttribute('src') !== url) img.src = url;
      e.caixa.querySelector('.pp-fundo').style.backgroundImage = 'url("' + url + '")';
    } else if (img) {
      e.capa.classList.remove('larga');
      img.remove();
      e.caixa.querySelector('.pp-fundo').style.backgroundImage = '';
    }
    var pos = t.posicao !== null && t.posicao !== undefined ? t.posicao + (t.tocando ? (performance.now() - previa.em) / 1000 : 0) : null;
    var dur = t.duracao || 0;
    e.cheio.style.transform = 'scaleX(' + (dur && pos !== null ? Math.min(1, pos / dur) : 0) + ')';
    var spans = e.tempos.querySelectorAll('span');
    spans[0].textContent = pos !== null && t.tem ? relogioEd(pos) : '';
    spans[1].textContent = dur ? relogioEd(dur) : '';
  }

  function relogioEd(seg) {
    seg = Math.max(0, Math.floor(seg));
    return Math.floor(seg / 60) + ':' + ('0' + (seg % 60)).slice(-2);
  }

  function pedirPrevia() {
    clearTimeout(previa.timer);
    if (!ehPlayer(S.pag) || document.hidden) return;
    api('/api/editor/tocando', { limite: 8000 }).then(function (r) {
      previa.dados = r;
      previa.em = performance.now();
      pintarPrevia();
    }).catch(function () { return null; }).finally(function () {
      previa.timer = setTimeout(function () { if (ehPlayer(S.pag)) pedirPrevia(); }, 2000);
    });
  }
  setInterval(function () { if (previa.dados && previa.dados.tocando) pintarPrevia(); }, 500);

  function slotEl(p, i) {
    var b = botaoEm(p, i);
    var sel = S.sel && S.sel.p === p && S.sel.i === i;
    var s;
    if (!b) {
      s = h('button', { type: 'button', class: 'slot vazio' + (sel && S.sel.novo ? ' novo' : ''), 'aria-label': tr('Espaço vazio {n}: adicionar botão', { n: i + 1 }) }, icone('mais'));
    } else {
      var info = infoDe(p, i, b);
      info.card = true;
      s = h('button', { type: 'button', class: 'slot' + (sel && !S.sel.novo ? ' selecionado' : ''), 'aria-label': (tituloDe(b) || tr('Botão')) + tr(' — editar') }, teclaEl(b, info));
    }
    s.dataset.p = p;
    s.dataset.i = i;
    return s;
  }

  function medirTeclas() {
    var g = grade();
    var cont = $('#aparelhos');
    if (!cont) return;
    var w = cont.clientWidth;
    if (!w) return;
    var gap = 32;
    var k = Math.floor((w - gap * (g.c - 1)) / g.c);
    k = Math.max(96, Math.min(k, 244));
    var area = $('.conteudo');
    var cs = getComputedStyle(area);
    var ocupado = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
    Array.prototype.forEach.call(area.children, function (el) {
      if (el === cont || el.hidden) return;
      var st = getComputedStyle(el);
      if (st.display === 'none' || st.position === 'absolute' || st.position === 'fixed') return;
      ocupado += el.offsetHeight + parseFloat(st.marginBottom) + (el.classList.contains('rodape-paginas') ? 0 : parseFloat(st.marginTop));
    });
    var kAltura = Math.floor((area.clientHeight - ocupado - gap * (g.l - 1)) / g.l);
    k = Math.max(96, Math.min(k, kAltura));
    if (g.c * (k + gap) - gap > w) gap = Math.max(12, Math.floor((w - g.c * k) / Math.max(1, g.c - 1)));
    Array.prototype.forEach.call(document.querySelectorAll('.aparelhos .teclas'), function (grid) {
      grid.style.setProperty('--k', k + 'px');
      grid.style.setProperty('--gap', gap + 'px');
    });
  }

  function abrirGaveta(titulo) {
    $('#gaveta').hidden = false;
    $('#gaveta-titulo').textContent = titulo;
    $('.corpo').classList.add('com-gaveta');
    setTimeout(medirTeclas, 240);
  }

  function fecharGaveta() {
    $('#gaveta').hidden = true;
    $('.corpo').classList.remove('com-gaveta');
    setTimeout(medirTeclas, 240);
  }

  function desenharPainel() {
    var pn = $('#painel');
    montarPainel(pn);
    var chave = S.sel ? (S.sel.novo ? 'novo:' : 'botao:') + S.sel.p + '.' + S.sel.i : (S.tela || '') + ':' + S.pag;
    if (chave !== S.chavePainel) {
      S.chavePainel = chave;
      pn.scrollTop = 0;
    }
  }

  function montarPainel(pn) {
    pn.textContent = '';
    S.seletor = null;
    if (!S.cfg) return;
    corrigirSelecao();
    if (S.sel) {
      if (S.sel.novo) { abrirGaveta(tr('Novo botão')); painelNovo(pn); return; }
      abrirGaveta(tr('Botão'));
      painelBotao(pn, botaoEm(S.sel.p, S.sel.i));
      return;
    }
    if (S.tela === 'pagina') { abrirGaveta(tr('Página')); painelPagina(pn); return; }
    if (S.tela === 'config') { abrirGaveta(tr('Configurações')); painelConfig(pn); return; }
    fecharGaveta();
  }

  function atualizarPrevia() {
    var pv = $('#painel .previa');
    if (!pv || !S.sel || S.sel.novo) return;
    if ($('#gaveta').hidden) return;
    var b = botaoEm(S.sel.p, S.sel.i);
    if (!b) return;
    pv.textContent = '';
    pv.appendChild(teclaEl(b, infoDe(S.sel.p, S.sel.i, b)));
    var t = $('#painel .cabeca h2');
    if (t) t.textContent = tituloDe(b) || TIPOS_INFO[tipoEditor(b)] && TIPOS_INFO[tipoEditor(b)].nome || tr('Botão');
    var erro = $('#painel .erro-botao');
    var v = visaoDe(S.sel.p, S.sel.i);
    if (erro) {
      erro.hidden = !(v && v.erro);
      erro.textContent = v && v.erro ? v.erro.replace(/^Página "[^"]*", botão \d+: /, '') : '';
    }
  }

  function secao(rotulo) {
    var s = h('div', { class: 'secao' });
    if (rotulo) s.appendChild(h('span', { class: 'rotulo', text: rotulo }));
    for (var n = 1; n < arguments.length; n++) anexar(s, arguments[n]);
    return s;
  }

  function painelPagina(pn) {
    var p = S.pag;
    var usados = usadosNa(p);
    var nome = h('input', { class: 'campo', id: 'nome-pagina', maxlength: '24', value: nomePagina(p), spellcheck: 'false', autocomplete: 'off' });
    nome.addEventListener('change', function () { renomearPagina(p, nome.value); });
    nome.addEventListener('keydown', function (e) { if (e.key === 'Enter') nome.blur(); });
    var icones = h('div', { class: 'icones-pagina', role: 'group', 'aria-label': tr('Ícone da página') });
    var atual = iconeDaPagina(p);
    (S.iconesPagina.length ? S.iconesPagina : Object.keys(window.ICONES_PAGINA || {})).forEach(function (chave) {
      var b = h('button', { type: 'button', 'aria-pressed': String(chave === atual), title: chave }, window.iconePagina ? iconePagina(chave) : chave);
      b.addEventListener('click', function () { mudar(function () { paginas()[p].icone = chave; }); });
      icones.appendChild(b);
    });
    var tipoSeg = segmentos([['botoes', tr('Botões')], ['player', tr('Player (modo DJ)')]], ehPlayer(p) ? 'player' : 'botoes', function (v) {
      mudar(function () {
        if (v === 'player') { paginas()[p].tipo = 'player'; if (!paginas()[p].icone) paginas()[p].icone = 'musica'; }
        else delete paginas()[p].tipo;
      });
    });
    var mostrar = h('input', { type: 'checkbox', checked: !ehOculta(p) });
    mostrar.addEventListener('change', function () { if (mostrar.checked === ehOculta(p)) alternarOculta(p); });
    var ordem = h('div', { class: 'ordem-pagina' },
      h('button', { type: 'button', class: 'botao', disabled: p === 0, onclick: function () { moverPagina(p, p - 1); } }, '↑ ' + tr('Subir')),
      h('button', { type: 'button', class: 'botao', disabled: p === paginas().length - 1, onclick: function () { moverPagina(p, p + 1); } }, '↓ ' + tr('Descer')));
    pn.appendChild(h('div', { class: 'vazio-painel' },
      h('h2', { text: nomePagina(p) }),
      h('p', { class: 'onde', text: ehPlayer(p) ? tr('Esta é a página {p} de {t}', { p: p + 1, t: paginas().length }) : tr('{u} de {c} espaços usados · esta é a página {p} de {t}', { u: usados, c: cap(), p: p + 1, t: paginas().length }) }),
      secao(tr('Nome da página'), nome),
      secao(tr('Tipo da página'), tipoSeg, h('p', { class: 'nota', text: ehPlayer(p)
        ? tr('O player mostra o que está tocando no computador (Spotify, YouTube, Apple Music…). Os botões que a página tinha ficam guardados se você voltar para Botões.')
        : tr('Player (modo DJ) troca os botões por um mini player do que estiver tocando no computador.') })),
      secao(tr('Ícone'), icones),
      secao(tr('No celular'), h('label', { class: 'chave' }, mostrar, h('span', { class: 'trilho' }), h('span', { text: tr('Mostrar esta página no celular') })),
        h('p', { class: 'nota', text: ehOculta(p) ? tr('Oculta: o celular pula esta página, mas ela continua aqui no editor com os botões.') : tr('Desligue para esconder a página do celular sem apagar. Também dá pelo olho ao lado do nome, na lateral.') })),
      secao(tr('Ordem'), ordem, h('p', { class: 'nota', text: tr('Ou arraste a página na lateral (ou na barra de páginas) para o lugar que quiser. No celular, a ordem muda junto.') })),
      h('div', { class: 'rodape-painel' },
        h('button', { type: 'button', class: 'botao perigo', disabled: paginas().length < 2, onclick: function () { apagarPagina(p); } },
          paginas().length < 2 ? tr('É a única página') : tr('Apagar esta página')))));
  }

  function painelConfig(pn) {
    var g = grade();
    var sel = h('select', { class: 'campo', id: 'grade', 'aria-label': tr('Grade') });
    var lista = GRADES.slice();
    if (!lista.some(function (x) { return x[0] === g.c && x[1] === g.l; })) lista.push([g.c, g.l]);
    lista.forEach(function (x) {
      sel.appendChild(h('option', { value: x[0] + 'x' + x[1], text: x[0] + ' × ' + x[1] + '  ' + tr('({n} botões por página)', { n: x[0] * x[1] }), selected: x[0] === g.c && x[1] === g.l }));
    });
    sel.addEventListener('change', function () {
      var v = sel.value.split('x');
      var c = parseInt(v[0], 10), l = parseInt(v[1], 10);
      mudar(function () { S.cfg.grade = { colunas: c, linhas: l }; });
    });
    var temaAtual = S.cfg.tema === 'normal' ? 'normal' : 'preto';
    var temas = h('div', { class: 'temas', role: 'group', 'aria-label': tr('Tema') });
    [['preto', tr('Preto'), tr('Fundo OLED, bordas e brilho na cor de cada ícone.')], ['normal', tr('Normal'), tr('Grafite azulado, mais discreto.')]].forEach(function (t) {
      var b = h('button', { type: 'button', class: 'tema-opcao ' + t[0], 'aria-pressed': String(temaAtual === t[0]), 'data-tema-opcao': t[0] },
        h('div', { class: 'amostra' }, h('span'), h('span')), h('b', { text: t[1] }), h('small', { text: t[2] }));
      b.addEventListener('click', function () { mudar(function () { S.cfg.tema = t[0]; }); });
      temas.appendChild(b);
    });
    var conectar = h('button', { type: 'button', class: 'botao', onclick: abrirConectar }, tr('Mostrar QR code'));
    var idiomaSel = h('select', { class: 'campo', id: 'idioma', 'aria-label': tr('Idioma') });
    [['auto', tr('Automático (idioma do computador)')], ['pt', 'Português'], ['en', 'English']].forEach(function (o) {
      idiomaSel.appendChild(h('option', { value: o[0], text: o[1], selected: (S.cfg.idioma || 'auto') === o[0] }));
    });
    idiomaSel.addEventListener('change', function () {
      mudar(function () { if (idiomaSel.value === 'auto') delete S.cfg.idioma; else S.cfg.idioma = idiomaSel.value; });
    });
    pn.appendChild(h('div', { class: 'vazio-painel' },
      h('h2', { text: tr('Configurações') }),
      h('p', { class: 'onde', text: (S.computador || tr('Este computador')) + ' · ' + (S.nomeSistema || '') }),
      secao(tr('Tema (no computador e no celular)'), temas),
      secao(tr('Grade (celular deitado)'), sel, h('p', { class: 'nota', text: tr('Em pé, as colunas viram linhas. Páginas com mais botões do que a grade viram telas extras.') })),
      secao(tr('Idioma'), idiomaSel, h('p', { class: 'nota', text: tr('Vale para o editor, o celular e o guia. Automático segue o idioma do computador.') })),
      secao(tr('Celular'), conectar, h('p', { class: 'nota', text: tr('Os botões aparecem no celular na hora, sem precisar reconectar.') }))));
  }

  function cabecalho(previaConteudo, titulo, onde) {
    var pv = h('div', { class: 'previa' }, previaConteudo);
    pv.style.setProperty('--k', '96px');
    return h('div', { class: 'cabeca' }, pv, h('div', null, h('h2', { text: titulo }), h('p', { class: 'onde', text: onde })));
  }

  function textoOnde(p, i) { return tr('Página “{p}” · espaço {n}', { p: nomePagina(p), n: i + 1 }); }

  function painelNovo(pn) {
    var vazioEl = h('div', { class: 'slot vazio novo' }, icone('mais'));
    vazioEl.style.setProperty('--k', '96px');
    pn.appendChild(cabecalho(vazioEl, S.tipoNovo ? tr('Novo: ') + TIPOS_INFO[S.tipoNovo].nome : tr('Novo botão'), textoOnde(S.sel.p, S.sel.i)));
    if (!S.tipoNovo) {
      var grid = h('div', { class: 'tipos' });
      ORDEM_TIPOS.forEach(function (t) {
        var info = TIPOS_INFO[t];
        var b = h('button', { type: 'button', class: 'tipo' + (t === 'app' || t === 'site' ? ' destaque' : ''), 'data-tipo': t },
          icone(info.icone), h('b', { text: info.nome }), h('small', { text: info.desc }));
        b.addEventListener('click', function () { escolherTipoNovo(t); });
        grid.appendChild(b);
      });
      pn.appendChild(secao(tr('O que o botão faz?'), grid));
      pn.appendChild(h('div', { class: 'rodape-painel' }, h('button', { type: 'button', class: 'botao fraco', onclick: function () { S.sel = null; desenhar(); } }, tr('Cancelar'))));
      return;
    }
    pn.appendChild(formTipo(S.tipoNovo, null, function (dados, sug) { criarBotao(dados, sug); }));
    pn.appendChild(h('div', { class: 'rodape-painel' }, h('button', { type: 'button', class: 'botao fraco', onclick: function () { S.tipoNovo = null; desenharPainel(); } }, tr('← Outros tipos'))));
    focarPrimeiro(pn);
  }

  function focarPrimeiro(pn) {
    setTimeout(function () {
      var alvo = pn.querySelector('[data-foco]');
      if (alvo) alvo.focus();
    }, 30);
  }

  function padraoDoTipo(t) {
    if (t === 'midia') return [{ tipo: 'midia', midia: 'play' }, { titulo: tr('Tocar/Pausar'), icone: '⏯️' }];
    if (t === 'volume') return [{ tipo: 'volume', volume: 'subir' }, { titulo: 'Volume +', icone: '🔊' }];
    if (t === 'microfone') return [{ tipo: 'microfone' }, { titulo: tr('Microfone'), icone: '🎙️' }];
    if (t === 'energia') return [{ tipo: 'energia', energia: 'desligar', confirmar: true }, { titulo: tr('Desligar'), icone: '⏻' }];
    if (t === 'modo') return [{ tipo: 'modo', nao_perturbe: true, minutos: 25 }, { titulo: tr('Foco'), icone: '🎯' }];
    if (t === 'chamada') return [{ tipo: 'chamada', chamada: 'mudo', app: 'auto' }, { titulo: tr('Mudo na chamada'), icone: '🔇' }];
    if (t === 'pagina') {
      var outra = paginas().length > 1 ? (S.sel && S.sel.p === 0 ? 1 : 0) : 0;
      return [{ tipo: 'pagina', pagina: nomePagina(outra) }, { titulo: nomePagina(outra), icone: '➡️' }];
    }
    return null;
  }

  function escolherTipoNovo(t) {
    var padrao = padraoDoTipo(t);
    if (padrao) { criarBotao(padrao[0], padrao[1]); return; }
    S.tipoNovo = t;
    desenharPainel();
  }

  function montarBotao(dados, sug, base) {
    var b = {};
    if (sug && sug.titulo) b.titulo = sug.titulo;
    b.tipo = dados.tipo;
    Object.keys(dados).forEach(function (k) { if (k !== 'tipo') b[k] = dados[k]; });
    if (sug && sug.icone) b.icone = sug.icone;
    if (base) {
      ['cor', 'confirmar', 'imagem'].forEach(function (k) { var v = ler(base, k); if (v) b[k] = v; });
    }
    return b;
  }

  function criarBotao(dados, sug) {
    var p = S.sel.p, i = S.sel.i;
    if (sug && sug.pedido && sug.img) S.mapaImg[sug.pedido] = sug.img;
    S.sel = { p: p, i: i };
    S.tipoNovo = null;
    mudar(function () { colocar(p, i, montarBotao(dados, sug)); });
  }

  function tituloPadrao(b) {
    var t = tipoCanon(b);
    if (t === 'app') {
      var v = listaApps(b)[0];
      var achado = (S.apps || []).filter(function (a) { return a.valor === v; })[0];
      return achado ? achado.nome : v;
    }
    if (t === 'link') return S.titulosSites[normalizarUrl(ler(b, 'url'))] || null;
    if (t === 'teclas') { var k = ler(b, 'teclas'); return typeof k === 'string' ? bonitoCombo(k) : null; }
    if (t === 'texto') return resumo(ler(b, 'texto'));
    if (t === 'midia') { var m = MIDIA.filter(function (x) { return x[0] === ALIAS_MIDIA[simples(ler(b, 'midia') || 'play')]; })[0]; return m ? m[1] : null; }
    if (t === 'volume') { var vv = VOLUME.filter(function (x) { return x[0] === ALIAS_VOLUME[simples(ler(b, 'volume') || '')]; })[0]; return vv ? vv[3] : 'Volume ' + ler(b, 'volume') + '%'; }
    if (t === 'microfone') return tr('Microfone');
    if (t === 'energia') return energiaDe(b)[1];
    if (t === 'pagina') return String(ler(b, 'pagina') || '');
    if (t === 'chamada') return chamadaDe(b)[0] === 'mudo' ? tr('Mudo na chamada') : chamadaDe(b)[1];
    return null;
  }

  function iconePadrao(b) {
    var t = tipoCanon(b);
    if (t === 'teclas') return '⌨️';
    if (t === 'texto') return '💬';
    if (t === 'midia') { var m = MIDIA.filter(function (x) { return x[0] === ALIAS_MIDIA[simples(ler(b, 'midia') || 'play')]; })[0]; return m ? m[2] : '⏯️'; }
    if (t === 'volume') { var v = VOLUME.filter(function (x) { return x[0] === ALIAS_VOLUME[simples(ler(b, 'volume') || '')]; })[0]; return v ? v[2] : '🔈'; }
    if (t === 'microfone') return '🎙️';
    if (t === 'energia') return energiaDe(b)[2];
    if (t === 'pagina') return '➡️';
    if (t === 'chamada') return chamadaDe(b)[2];
    return null;
  }

  function aplicarTipo(dados, sug) {
    var p = S.sel.p, i = S.sel.i;
    var velho = botaoEm(p, i);
    if (sug && sug.pedido && sug.img) S.mapaImg[sug.pedido] = sug.img;
    var titulo = tituloDe(velho);
    var tituloAuto = !titulo || titulo === tituloPadrao(velho);
    var icVelho = ler(velho, 'icone');
    var iconeAuto = !icVelho || icVelho === iconePadrao(velho);
    var novoSug = {
      titulo: tituloAuto ? (sug && sug.titulo) : titulo,
      icone: (dados.tipo === 'app' || dados.tipo === 'site') ? (iconeAuto ? null : icVelho) : (iconeAuto ? sug && sug.icone : icVelho),
    };
    S.tipoNovo = null;
    mudar(function () { colocar(p, i, montarBotao(dados, novoSug, velho)); });
  }

  function formTipo(t, b, aoConcluir) {
    if (t === 'app') {
      return secao(tr('Escolha o app'), seletorApps(b ? listaApps(b)[0] : null, function (a) {
        aoConcluir({ tipo: 'app', app: a.valor }, { titulo: a.nome, pedido: 'app:' + a.valor, img: a.img });
      }));
    }
    if (t === 'site') {
      return secao(tr('Qual site?'), seletorSites(b ? ler(b, 'url') : '', b ? tr('Salvar') : tr('Adicionar'), aoConcluir));
    }
    if (t === 'teclas') {
      var atual = b ? ler(b, 'teclas') : null;
      var usar = h('button', { type: 'button', class: 'botao primario', disabled: true }, b ? tr('Salvar') : tr('Adicionar'));
      var combo = typeof atual === 'string' ? atual : '';
      var campo = h('input', { class: 'campo', value: combo, placeholder: S.sistema === 'mac' ? tr('ex.: cmd+shift+4') : tr('ex.: ctrl+c'), spellcheck: 'false', autocomplete: 'off' });
      var grav = gravadorTeclas(combo, function (c) { combo = c; campo.value = c; usar.disabled = false; });
      grav.setAttribute('data-foco', '');
      campo.addEventListener('input', function () { combo = campo.value.trim(); usar.disabled = !combo; });
      usar.addEventListener('click', function () {
        if (!combo) return;
        aoConcluir({ tipo: 'teclas', teclas: combo }, { titulo: bonitoCombo(combo), icone: '⌨️' });
      });
      return h('div', null, secao(tr('Aperte o atalho'), grav), secao(tr('Ou escreva'), h('div', { class: 'linha-campo' }, campo, usar)),
        h('p', { class: 'nota', text: tr('Atalhos que o navegador não deixa gravar (como {k}) podem ser escritos à mão.', { k: S.sistema === 'mac' ? '⌘Q' : 'Alt+F4' }) }));
    }
    if (t === 'texto') {
      var area = h('textarea', { class: 'campo', placeholder: tr('ex.: Já te respondo!'), 'data-foco': '' });
      var add = h('button', { type: 'button', class: 'botao primario', disabled: true }, b ? tr('Salvar') : tr('Adicionar'));
      area.addEventListener('input', function () { add.disabled = !area.value; });
      add.addEventListener('click', function () {
        if (!area.value) return;
        aoConcluir({ tipo: 'texto', texto: area.value }, { titulo: resumo(area.value), icone: '💬' });
      });
      return h('div', null, secao(tr('O que digitar'), area), h('div', { class: 'secao' }, add));
    }
    var padrao = padraoDoTipo(t);
    if (padrao) {
      var ok = h('button', { type: 'button', class: 'botao primario' }, tr('Usar ') + TIPOS_INFO[t].nome);
      ok.addEventListener('click', function () { aoConcluir(padrao[0], padrao[1]); });
      return secao(null, ok);
    }
    return h('div');
  }

  function resumo(txt) {
    var s = String(txt || '').replace(/\s+/g, ' ').trim();
    return s.length > 18 ? s.slice(0, 17).trim() + '…' : s;
  }

  function painelBotao(pn, b) {
    var p = S.sel.p, i = S.sel.i;
    var tipo = tipoEditor(b);
    var info = TIPOS_INFO[tipo];
    var titulo = tituloDe(b) || (info ? info.nome : tr('Botão'));
    pn.appendChild(cabecalho(teclaEl(b, infoDe(p, i, b)), titulo, (info ? info.nome : tr('Feito no config.json')) + ' · ' + textoOnde(p, i)));
    var erro = h('p', { class: 'erro-campo erro-botao', hidden: true });
    pn.appendChild(erro);

    if (S.tipoNovo) {
      pn.appendChild(formTipo(S.tipoNovo, null, aplicarTipo));
      pn.appendChild(h('div', { class: 'rodape-painel' }, h('button', { type: 'button', class: 'botao fraco', onclick: function () { S.tipoNovo = null; desenharPainel(); } }, tr('← Cancelar troca'))));
      focarPrimeiro(pn);
      atualizarPrevia();
      return;
    }

    var seletorTipo = h('select', { class: 'campo', 'aria-label': tr('Tipo do botão') });
    ORDEM_TIPOS.forEach(function (t) { seletorTipo.appendChild(h('option', { value: t, text: TIPOS_INFO[t].nome, selected: t === tipo })); });
    if (tipo === 'outro') seletorTipo.insertBefore(h('option', { value: 'outro', text: tr('Outro (config.json)'), selected: true }), seletorTipo.firstChild);
    seletorTipo.addEventListener('change', function () {
      var t = seletorTipo.value;
      var padrao = padraoDoTipo(t);
      if (padrao) { aplicarTipo(padrao[0], padrao[1]); return; }
      S.tipoNovo = t;
      desenharPainel();
    });
    pn.appendChild(secao(tr('Tipo'), seletorTipo));

    var campos = camposDoTipo(b, tipo, p, i);
    if (!campos.classList.contains('secao')) campos.classList.add('campos-tipo');
    pn.appendChild(campos);

    var campoTitulo = h('input', { class: 'campo', value: tituloDe(b), maxlength: '40', placeholder: titulo, spellcheck: 'false', autocomplete: 'off' });
    campoTitulo.addEventListener('input', function () {
      mudar(function () { escrever(b, 'titulo', campoTitulo.value); }, { painel: false, grupo: 'titulo:' + p + '.' + i });
    });
    campoTitulo.addEventListener('blur', function () { S.grupo = null; });
    pn.appendChild(secao(tr('Nome no botão'), campoTitulo));
    pn.appendChild(secaoIcone(b, p, i));
    pn.appendChild(secaoCor(b, p, i));

    var conf = h('input', { type: 'checkbox', checked: tipo === 'energia' ? ler(b, 'confirmar') !== false : !!ler(b, 'confirmar') });
    conf.addEventListener('change', function () { mudar(function () { escrever(b, 'confirmar', conf.checked ? true : (tipo === 'energia' ? false : null)); }, { painel: false }); });
    pn.appendChild(secao(null, h('label', { class: 'chave' }, conf, h('span', { class: 'trilho' }), h('span', { text: tr('Pedir um segundo toque antes de executar') }))));

    var rodape = h('div', { class: 'rodape-painel' });
    if (paginas().length > 1) {
      var mover = h('select', { 'aria-label': tr('Mover para outra página') });
      mover.appendChild(h('option', { value: '', text: tr('Mover para…'), selected: true }));
      paginas().forEach(function (pg, q) { if (q !== p && !ehPlayer(q)) mover.appendChild(h('option', { value: String(q), text: nomePagina(q) })); });
      mover.addEventListener('change', function () { if (mover.value !== '') moverParaPagina(p, i, parseInt(mover.value, 10)); });
      rodape.appendChild(h('label', { class: 'mover' }, h('span', { text: tr('Página') }), mover));
    }
    rodape.appendChild(h('button', { type: 'button', class: 'botao perigo', onclick: function () { removerBotao(p, i); } }, tr('Remover botão')));
    pn.appendChild(rodape);
    atualizarPrevia();
  }

  function camposDoTipo(b, tipo, p, i) {
    if (tipo === 'app') {
      return secao('App', seletorApps(listaApps(b)[0], function (a) {
        if (a.img) S.mapaImg['app:' + a.valor] = a.img;
        var auto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        mudar(function () {
          escrever(b, 'app', a.valor);
          if (auto) escrever(b, 'titulo', a.nome);
        });
      }));
    }
    if (tipo === 'site') {
      var navSel = h('select', { class: 'campo', 'aria-label': tr('Abrir em') });
      var navAtual = String(ler(b, 'navegador') || '');
      navSel.appendChild(h('option', { value: '', text: tr('Navegador padrão') + padraoNome(), selected: !navAtual }));
      var achou = !navAtual;
      S.navegadores.forEach(function (n) {
        var sel = navAtual && semAcento(n.nome) === semAcento(navAtual);
        if (sel) achou = true;
        navSel.appendChild(h('option', { value: n.nome, text: n.nome, selected: sel }));
      });
      if (!achou) navSel.appendChild(h('option', { value: navAtual, text: navAtual + tr(' (não achei aqui)'), selected: true }));
      navSel.addEventListener('change', function () { mudar(function () { escrever(b, 'navegador', navSel.value || null); }, { painel: false }); });
      var partes = [secao(tr('Endereço'), seletorSites(ler(b, 'url'), tr('Salvar'), function (dados, sug) {
        if (sug.pedido && sug.img) S.mapaImg[sug.pedido] = sug.img;
        var auto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        mudar(function () {
          escrever(b, 'url', dados.url);
          if (auto && sug.titulo) escrever(b, 'titulo', sug.titulo);
        });
      }, true)), secao(tr('Abrir em'), navSel)];
      if (S.sistema === 'mac') {
        var reusar = h('input', { type: 'checkbox', checked: ler(b, 'aba') !== false });
        reusar.addEventListener('change', function () { mudar(function () { escrever(b, 'aba', reusar.checked ? null : false); }, { painel: false }); });
        partes.push(secao(null, h('label', { class: 'chave' }, reusar, h('span', { class: 'trilho' }), h('span', { text: tr('Se a aba já estiver aberta, só trazer para frente') }))));
      }
      return h('div', null, partes);
    }
    if (tipo === 'teclas') {
      var atual = ler(b, 'teclas');
      if (Array.isArray(atual)) {
        return secao(tr('Teclas'), h('p', { class: 'nota', text: tr('Sequência de {n} atalhos: {s}. Grave um novo para trocar.', { n: atual.length, s: atual.join(' → ') }) }),
          gravadorTeclas('', function (c) { trocarTeclas(b, c); }));
      }
      var campo = h('input', { class: 'campo', value: typeof atual === 'string' ? atual : '', spellcheck: 'false', autocomplete: 'off' });
      var grav = gravadorTeclas(typeof atual === 'string' ? atual : '', function (c) { campo.value = c; trocarTeclas(b, c); });
      campo.addEventListener('change', function () { if (campo.value.trim()) trocarTeclas(b, campo.value.trim()); });
      return h('div', null, secao(tr('Atalho'), grav), secao(tr('Ou escreva'), campo));
    }
    if (tipo === 'texto') {
      var area = h('textarea', { class: 'campo' });
      area.value = String(ler(b, 'texto') || '');
      area.addEventListener('input', function () {
        if (!area.value) return;
        var auto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        mudar(function () {
          escrever(b, 'texto', area.value);
          if (auto) escrever(b, 'titulo', resumo(area.value));
        }, { painel: false, grupo: 'texto:' + p + '.' + i });
      });
      area.addEventListener('blur', function () { S.grupo = null; });
      return secao(tr('O que digitar'), area);
    }
    if (tipo === 'midia') {
      var atualM = ALIAS_MIDIA[simples(ler(b, 'midia') || 'play')] || 'play';
      return secao(tr('Ação'), segmentos(MIDIA.map(function (x) { return [x[0], x[2] + ' ' + x[1]]; }), atualM, function (v) {
        var tAuto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        var iAuto = !ler(b, 'icone') || ler(b, 'icone') === iconePadrao(b);
        var m = MIDIA.filter(function (x) { return x[0] === v; })[0];
        mudar(function () {
          escrever(b, 'midia', v);
          if (tAuto) escrever(b, 'titulo', m[1]);
          if (iAuto && !ler(b, 'imagem')) escrever(b, 'icone', m[2]);
        });
      }));
    }
    if (tipo === 'volume') {
      var bruto = ler(b, 'volume');
      var atualV = ALIAS_VOLUME[simples(bruto === undefined ? '' : bruto)] || (/^\d+$/.test(String(bruto)) ? 'definir' : 'subir');
      var numero = h('input', { class: 'campo', type: 'number', min: '0', max: '100', value: atualV === 'definir' ? String(bruto) : '50', 'aria-label': tr('Volume em %') });
      numero.style.width = '96px';
      numero.addEventListener('change', function () {
        var n = Math.max(0, Math.min(100, parseInt(numero.value, 10) || 0));
        mudar(function () { escrever(b, 'volume', n); }, { painel: false });
      });
      var opcoes = VOLUME.map(function (x) { return [x[0], x[2] + ' ' + x[1]]; }).concat([['definir', '🔈 ' + tr('Definir')]]);
      return h('div', null, secao(tr('Ação'), segmentos(opcoes, atualV, function (v) {
        var tAuto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        var iAuto = !ler(b, 'icone') || ler(b, 'icone') === iconePadrao(b);
        var x = VOLUME.filter(function (y) { return y[0] === v; })[0];
        mudar(function () {
          escrever(b, 'volume', v === 'definir' ? Math.max(0, Math.min(100, parseInt(numero.value, 10) || 50)) : v);
          if (tAuto) escrever(b, 'titulo', x ? x[3] : 'Volume ' + (parseInt(numero.value, 10) || 50) + '%');
          if (iAuto && !ler(b, 'imagem')) escrever(b, 'icone', x ? x[2] : '🔈');
        });
      })), atualV === 'definir' ? secao(tr('Volume (%)'), numero) : null);
    }
    if (tipo === 'microfone') {
      return secao(null, h('p', { class: 'nota', text: tr('Liga e desliga o mudo do microfone do computador. No celular, a luz MUDO acende enquanto ele estiver mudo.') }));
    }
    if (tipo === 'energia') {
      var atualE = energiaDe(b)[0];
      var notaE = h('p', { class: 'nota' });
      var textoE = function (v) {
        if (v === 'suspender') return tr('O computador dorme na hora. Para acordar: qualquer tecla ou o mouse. No Mac com "Despertar para acesso à rede" ligado e um Apple TV, HomePod ou roteador Apple na rede, ele acorda sozinho quando o Deck abre no celular.');
        if (v === 'bloquear') return tr('Vai para a tela de bloqueio; os programas continuam abertos.');
        if (v === 'reiniciar') return tr('Fecha tudo e liga de novo. Programas com trabalho não salvo podem segurar o reinício.');
        return tr('Desliga de verdade. O celular não consegue ligar um computador desligado (não há nada rodando para receber o pedido) — se quiser ligar de longe, prefira Suspender.');
      };
      notaE.textContent = textoE(atualE);
      return h('div', null, secao(tr('Ação'), segmentos(ENERGIA.map(function (x) { return [x[0], x[2] + ' ' + x[1]]; }), atualE, function (v) {
        var tAuto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        var iAuto = !ler(b, 'icone') || ler(b, 'icone') === iconePadrao(b);
        var x = ENERGIA.filter(function (y) { return y[0] === v; })[0];
        mudar(function () {
          escrever(b, 'energia', v);
          if (tAuto) escrever(b, 'titulo', x[1]);
          if (iAuto && !ler(b, 'imagem')) escrever(b, 'icone', x[2]);
        });
      })), secao(null, notaE));
    }
    if (tipo === 'pagina') {
      var sel = h('select', { class: 'campo' });
      var alvo = ler(b, 'pagina');
      var achou = false;
      paginas().forEach(function (pg, q) {
        var igual = typeof alvo === 'number' ? alvo === q + 1 : simples(nomePagina(q)) === simples(alvo || '');
        if (igual) achou = true;
        sel.appendChild(h('option', { value: nomePagina(q), text: nomePagina(q), selected: igual }));
      });
      if (!achou) sel.insertBefore(h('option', { value: '', text: tr('Escolha a página'), selected: true }), sel.firstChild);
      sel.addEventListener('change', function () {
        if (!sel.value) return;
        var auto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
        mudar(function () { escrever(b, 'pagina', sel.value); if (auto) escrever(b, 'titulo', sel.value); });
      });
      return secao(tr('Ir para'), sel);
    }
    if (tipo === 'modo') return camposModo(b, p, i);
    if (tipo === 'chamada') return camposChamada(b);
    var t = tipoCanon(b);
    return secao(null, h('p', { class: 'nota' }, tr('Este botão é um '), h('b', { text: NOMES_OUTROS[t] || tr('tipo especial') }), tr(' feito direto no config.json. Aqui dá para mudar nome, ícone, cor e lugar; o que ele faz continua igual.')));
  }

  function listaDe(b, campo) {
    var v = ler(b, campo);
    if (v === undefined || v === null || v === '') return [];
    return (Array.isArray(v) ? v : [v]).filter(function (x) { return typeof x === 'string' && x.trim(); });
  }

  function editorDeLista(b, campo, dica, comSites) {
    var itens = listaDe(b, campo);
    var caixa = h('div', { class: 'lista-chips' });
    itens.forEach(function (item, n) {
      var x = h('button', { type: 'button', class: 'chip-x', 'aria-label': tr('Tirar {i}', { i: item }) }, '×');
      x.addEventListener('click', function () {
        mudar(function () { var nova = listaDe(b, campo).slice(); nova.splice(n, 1); escrever(b, campo, nova.length ? nova : null); });
      });
      caixa.appendChild(h('span', { class: 'chip' }, h('span', { text: item.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '') }), x));
    });
    var idLista = 'sugestoes-' + campo;
    var campoNovo = h('input', { class: 'campo', placeholder: dica, list: idLista, spellcheck: 'false', autocomplete: 'off' });
    var dl = h('datalist', { id: idLista });
    (S.apps || []).slice(0, 400).forEach(function (a) { dl.appendChild(h('option', { value: a.nome })); });
    if (!S.apps && !S.appsCarregando) carregarApps();
    var add = h('button', { type: 'button', class: 'botao fraco' }, tr('Adicionar'));
    var adicionar = function () {
      var v = campoNovo.value.trim();
      if (!v) return;
      if (comSites && pareceEndereco(v) && !/\s/.test(v)) v = normalizarUrl(v);
      mudar(function () { var nova = listaDe(b, campo).concat([v]).slice(0, 12); escrever(b, campo, nova); });
    };
    add.addEventListener('click', adicionar);
    campoNovo.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); adicionar(); } });
    return h('div', null, caixa, h('div', { class: 'linha-campo' }, campoNovo, add), dl);
  }

  function notaNaoPerturbe() {
    if (S.sistema === 'mac') return tr('No Mac, o deck liga o Foco pelo app Atalhos: crie uma vez os atalhos “Deck Foco Ligar” e “Deck Foco Desligar” com a ação “Definir Foco” (Não Perturbe › Ligado/Desligado).');
    if (S.sistema === 'windows') return tr('No Windows não há como ligar o Não perturbe por programa: o deck avisa no celular para você ligar em Win+N.');
    return tr('No Linux funciona no GNOME (esconde os avisos na tela).');
  }

  function camposModo(b, p, i) {
    var np = ler(b, 'nao_perturbe');
    var npAtual = np === true ? 'ligar' : np === false ? 'desligar' : '';
    var npSeg = segmentos([['', tr('Não mexer')], ['ligar', tr('Ativar')], ['desligar', tr('Desativar')]], npAtual, function (v) {
      mudar(function () { escrever(b, 'nao_perturbe', v === 'ligar' ? true : v === 'desligar' ? false : null); });
    });
    var mins = parseInt(ler(b, 'minutos'), 10) || 0;
    var opcoesMin = [['0', tr('Sem')], ['5', '5 min'], ['15', '15 min'], ['25', '25 min'], ['50', '50 min']];
    var outroMin = mins && !opcoesMin.some(function (o) { return o[0] === String(mins); });
    var campoMin = h('input', { class: 'campo', type: 'number', min: '1', max: '480', value: mins ? String(mins) : '', 'aria-label': tr('Minutos') });
    campoMin.style.width = '96px';
    campoMin.addEventListener('change', function () {
      var n = Math.max(1, Math.min(480, parseInt(campoMin.value, 10) || 25));
      mudar(function () { escrever(b, 'minutos', n); }, { painel: false });
    });
    var minSeg = segmentos(opcoesMin.concat([['outro', tr('Outro')]]), outroMin ? 'outro' : String(mins), function (v) {
      mudar(function () { escrever(b, 'minutos', v === '0' ? null : v === 'outro' ? (mins || 30) : parseInt(v, 10)); });
    });
    var vol = ler(b, 'volume');
    var temVol = typeof vol === 'number' || (typeof vol === 'string' && /^\d+$/.test(vol));
    var faixa = h('input', { type: 'range', min: '0', max: '100', step: '5', value: temVol ? String(vol) : '40', 'aria-label': tr('Volume do modo') });
    var faixaNum = h('span', { class: 'nota', style: 'margin:0;min-width:42px;text-align:right', text: (temVol ? vol : 40) + '%' });
    faixa.addEventListener('input', function () { faixaNum.textContent = faixa.value + '%'; });
    faixa.addEventListener('change', function () { mudar(function () { escrever(b, 'volume', parseInt(faixa.value, 10)); }, { painel: false }); });
    var volSeg = segmentos([['', tr('Não mexer')], ['n', tr('Ajustar')]], temVol ? 'n' : '', function (v) {
      mudar(function () { escrever(b, 'volume', v === 'n' ? 40 : null); });
    });
    var pagSel = h('select', { class: 'campo', 'aria-label': tr('Ir para a página') });
    var pagAtual = String(ler(b, 'pagina') || '');
    var pagAchou = !pagAtual;
    pagSel.appendChild(h('option', { value: '', text: tr('Ficar na página atual'), selected: !pagAtual }));
    paginas().forEach(function (pg, q) {
      if (q === p) return;
      var igual = !!pagAtual && simples(pagAtual) === simples(nomePagina(q));
      if (igual) pagAchou = true;
      pagSel.appendChild(h('option', { value: nomePagina(q), text: nomePagina(q), selected: igual }));
    });
    if (!pagAchou) pagSel.appendChild(h('option', { value: pagAtual, text: tr('{p} (não existe mais)', { p: pagAtual }), selected: true }));
    pagSel.addEventListener('change', function () { mudar(function () { escrever(b, 'pagina', pagSel.value || null); }, { painel: false }); });
    return h('div', null,
      h('p', { class: 'nota', text: tr('Um toque liga o modo; outro toque desliga (e desfaz o Não perturbe). Só um modo fica ligado por vez.') }),
      secao(tr('Não perturbe'), npSeg, npAtual ? h('p', { class: 'nota', text: notaNaoPerturbe() }) : null),
      secao(tr('Cronômetro na tela do celular'), minSeg, outroMin ? h('div', { class: 'linha-campo', style: 'margin-top:8px' }, campoMin, h('span', { class: 'nota', style: 'margin:0', text: tr('minutos') })) : null),
      secao(tr('Abrir'), editorDeLista(b, 'abrir', tr('App ou site (ex.: Notion, gmail.com)'), true)),
      secao(tr('Fechar apps que distraem'), editorDeLista(b, 'fechar', tr('Nome do app (ex.: WhatsApp)'), false)),
      secao(tr('Volume'), volSeg, temVol ? h('div', { class: 'linha-campo', style: 'margin-top:8px;align-items:center' }, faixa, faixaNum) : null),
      secao(tr('Depois, no celular'), pagSel));
  }

  function camposChamada(b) {
    var atual = chamadaDe(b)[0];
    var seg = segmentos(CHAMADA.map(function (x) { return [x[0], x[2] + ' ' + x[1]]; }), atual, function (v) {
      var tAuto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
      var iAuto = !ler(b, 'icone') || ler(b, 'icone') === iconePadrao(b);
      var x = CHAMADA.filter(function (y) { return y[0] === v; })[0];
      mudar(function () {
        escrever(b, 'chamada', v);
        if (tAuto) escrever(b, 'titulo', v === 'mudo' ? tr('Mudo na chamada') : x[1]);
        if (iAuto && !ler(b, 'imagem')) escrever(b, 'icone', x[2]);
      });
    });
    var appAtual = String(ler(b, 'app') || 'auto').toLowerCase().replace(/[^a-z]/g, '');
    if (appAtual === 'microsoftteams' || appAtual === 'msteams') appAtual = 'teams';
    if (appAtual === 'googlemeet') appAtual = 'meet';
    if (!APPS_CHAMADA.some(function (a) { return a[0] === appAtual; })) appAtual = 'auto';
    var appSel = h('select', { class: 'campo', 'aria-label': tr('App da chamada') });
    APPS_CHAMADA.forEach(function (a) { appSel.appendChild(h('option', { value: a[0], text: a[1], selected: a[0] === appAtual })); });
    appSel.addEventListener('change', function () { mudar(function () { escrever(b, 'app', appSel.value === 'auto' ? null : appSel.value); }); });
    var notas = [];
    if (atual === 'atender' || atual === 'recusar') {
      notas.push(S.sistema === 'mac'
        ? tr('No Mac, chamadas do FaceTime e do iPhone (pela Continuidade) aparecem no celular com Atender e Recusar. Nos outros apps, o deck usa o atalho do app.')
        : tr('O deck traz o app para frente e aperta o atalho de atender dele (Zoom, Teams e Discord têm).'));
    }
    if (appAtual === 'auto') notas.push(tr('No automático, o deck usa a reunião aberta: Meet, Zoom, Teams, Webex ou FaceTime. Para Discord e Slack, escolha o app aqui.'));
    if (atual === 'mudo') notas.push(tr('Sem chamada aberta, este botão silencia o microfone do computador.'));
    if (atual === 'encerrar' && (appAtual === 'zoom' || appAtual === 'auto')) notas.push(tr('No Zoom, sair pede confirmação na tela.'));
    if (atual === 'encerrar' && appAtual === 'meet') notas.push(tr('No Meet, encerrar fecha a aba da reunião.'));
    return h('div', null,
      secao(tr('Ação'), seg),
      secao(tr('App da chamada'), appSel, notas.length ? h('p', { class: 'nota', text: notas.join(' ') }) : null));
  }

  function trocarTeclas(b, combo) {
    var auto = !tituloDe(b) || tituloDe(b) === tituloPadrao(b);
    mudar(function () {
      escrever(b, 'teclas', combo);
      if (auto) escrever(b, 'titulo', bonitoCombo(combo));
    }, { painel: false });
  }

  function segmentos(opcoes, atual, aoMudar) {
    var c = h('div', { class: 'segmentos', role: 'group' });
    opcoes.forEach(function (o) {
      var b = h('button', { type: 'button', 'aria-pressed': String(o[0] === atual), 'data-valor': o[0] }, o[1]);
      b.addEventListener('click', function () { if (o[0] !== atual) aoMudar(o[0]); });
      c.appendChild(b);
    });
    return c;
  }

  function secaoIcone(b, p, i) {
    var tipo = tipoCanon(b);
    var auto = tipo === 'app' || tipo === 'link';
    var modo = ler(b, 'imagem') ? 'imagem' : ler(b, 'icone') ? 'emoji' : (auto ? 'auto' : 'nenhum');
    var opcoes = auto
      ? [['auto', tipo === 'app' ? tr('Do computador') : tr('Do site')], ['emoji', 'Emoji'], ['imagem', tr('Imagem')]]
      : [['emoji', 'Emoji'], ['imagem', tr('Imagem')], ['nenhum', tr('Sem ícone')]];
    var arquivo = h('input', { type: 'file', accept: 'image/png,image/jpeg,image/gif,image/webp,image/svg+xml', hidden: true });
    arquivo.addEventListener('change', function () {
      var f = arquivo.files && arquivo.files[0];
      if (f) enviarImagem(b, f);
      arquivo.value = '';
    });
    var s = secao(tr('Ícone'), segmentos(opcoes, modo, function (v) {
      if (v === 'imagem') { arquivo.click(); return; }
      mudar(function () {
        escrever(b, 'imagem', null);
        if (v === 'emoji') escrever(b, 'icone', ler(b, 'icone') || iconePadrao(b) || '⭐');
        else escrever(b, 'icone', null);
      });
      if (v === 'emoji') setTimeout(function () { var e = $('#painel .emoji-campo'); if (e) { e.focus(); e.select(); } }, 30);
    }), arquivo);
    if (modo === 'emoji') {
      var campo = h('input', { class: 'campo emoji-campo', value: String(ler(b, 'icone') || ''), maxlength: '16', 'aria-label': 'Emoji', autocomplete: 'off' });
      campo.addEventListener('input', function () {
        mudar(function () { escrever(b, 'icone', campo.value.trim() || null); }, { painel: false, grupo: 'icone:' + p + '.' + i });
      });
      campo.addEventListener('blur', function () { S.grupo = null; });
      s.appendChild(h('div', { class: 'secao', style: 'margin-top:10px' }, h('div', { class: 'linha-campo', style: 'align-items:center' }, campo,
        h('span', { class: 'nota', style: 'margin:0', text: S.sistema === 'mac' ? tr('Dica: ⌃⌘Espaço abre os emojis do Mac.') : S.sistema === 'windows' ? tr('Dica: Win + . abre os emojis.') : tr('Cole um emoji ou escreva até 2 letras.') }))));
    } else if (modo === 'imagem') {
      s.appendChild(h('p', { class: 'nota' }, tr('Imagem: '), h('b', { text: String(ler(b, 'imagem')) }), tr(' (pasta icones). '),
        h('button', { type: 'button', class: 'botao fraco', style: 'height:auto;padding:0;text-decoration:underline', onclick: function () { arquivo.click(); } }, tr('Trocar'))));
    } else if (modo === 'auto') {
      s.appendChild(h('p', { class: 'nota', text: tipo === 'app' ? tr('O ícone é o mesmo do app no computador.') : tr('O ícone é o do próprio site.') }));
    }
    return s;
  }

  function enviarImagem(b, arquivo) {
    if (arquivo.size > 4 * 1024 * 1024) { toast(tr('Imagem grande demais (máximo 4 MB).'), null, null, 'erro'); return; }
    var leitor = new FileReader();
    leitor.onload = function () {
      api('/api/editor/imagem', { corpo: { nome: arquivo.name, dados: leitor.result }, limite: 30000 }).then(function (r) {
        mudar(function () { escrever(b, 'icone', null); escrever(b, 'imagem', r.imagem); });
      }).catch(function (e) { toast(e.message, null, null, 'erro'); });
    };
    leitor.readAsDataURL(arquivo);
  }

  function secaoCor(b) {
    var atual = corDe(ler(b, 'cor'));
    var c = h('div', { class: 'cores', role: 'group', 'aria-label': tr('Cor do botão') });
    var nenhuma = h('button', { type: 'button', class: 'cor nenhuma', title: tr('Sem cor'), 'aria-label': tr('Sem cor'), 'aria-pressed': String(!atual) });
    nenhuma.addEventListener('click', function () { mudar(function () { escrever(b, 'cor', null); }, { painel: true }); });
    c.appendChild(nenhuma);
    CORES_ORDEM.forEach(function (nome) {
      var hex = S.cores[nome];
      if (!hex) return;
      var bt = h('button', { type: 'button', class: 'cor', title: nome, 'aria-label': nome, 'aria-pressed': String(atual === hex) });
      bt.style.setProperty('--c', hex);
      bt.addEventListener('click', function () { mudar(function () { escrever(b, 'cor', nome); }); });
      c.appendChild(bt);
    });
    return secao(tr('Cor'), c);
  }

  function padraoNome() {
    var p = S.navegadores.filter(function (n) { return n.padrao; })[0];
    return p ? ' (' + p.nome + ')' : '';
  }

  function pareceEndereco(v) {
    return /^[a-zA-Z][\w+.-]*:/.test(v) || /^[\w.-]+\.[a-zA-Z]{2,}([\/:?#]|$)/.test(v) || /^(\d{1,3}\.){3}\d{1,3}/.test(v) || /^localhost/.test(v);
  }

  function seletorSites(urlAtual, textoBotao, aoConcluir, editando) {
    var campo = h('input', { class: 'campo', value: editando ? (urlAtual || '') : '', placeholder: editando ? tr('ex.: youtube.com') : tr('Procurar ou digitar um endereço…'), inputmode: 'url', spellcheck: 'false', autocomplete: 'off', 'data-foco': '' });
    var botao = h('button', { type: 'button', class: 'botao primario' }, textoBotao);
    var msg = h('p', { class: 'nota', hidden: true });
    var lista = h('div', { class: 'lista-apps lista-sites', role: 'listbox', 'aria-label': tr('Sites sugeridos') });
    var ocupado = false;
    function concluir(url, titulo, item) {
      if (ocupado) return;
      ocupado = true;
      botao.disabled = true;
      if (item) item.classList.add('buscando');
      msg.hidden = false;
      msg.className = 'nota';
      msg.textContent = tr('Buscando o ícone do site…');
      api('/api/editor/site', { corpo: { url: url, titulo: titulo || null }, limite: 40000 }).then(function (r) {
        if (r.titulo) S.titulosSites[r.url] = r.titulo;
        msg.hidden = !r.semInternet;
        msg.textContent = r.semInternet ? tr('Não consegui abrir o site agora — por enquanto fica a inicial no lugar do ícone.') : '';
        if (r.pedido) S.mapaImg2[r.pedido] = r.img2 || null;
        aoConcluir({ tipo: 'site', url: r.url }, { titulo: r.titulo, pedido: r.pedido, img: r.img });
      }).catch(function (e) {
        msg.hidden = false;
        msg.className = 'erro-campo';
        msg.textContent = e.message;
      }).finally(function () { ocupado = false; botao.disabled = false; if (item) item.classList.remove('buscando'); });
    }
    function enviar() {
      var v = campo.value.trim();
      if (!v) { campo.focus(); return; }
      if (!pareceEndereco(v)) {
        var primeiro = lista.querySelector('.app-item[data-url]');
        if (primeiro) { primeiro.click(); return; }
      }
      concluir(v, null, null);
    }
    function item(x, origem) {
      var figuraItem = x.img ? h('img', { src: comToken(x.img), alt: '', loading: 'lazy', draggable: 'false' }) : null;
      if (figuraItem && x.img2 && window.escolherFigura) escolherFigura(figuraItem, comToken(x.img2));
      var el = h('button', { type: 'button', class: 'app-item', role: 'option' },
        figuraItem || miniLetra(x.titulo || x.url),
        h('span', { class: 'duas' }, h('b', { text: x.titulo || x.url }), h('small', { text: x.url.replace(/^https?:\/\/(www\.)?/, '') })),
        origem ? h('span', { class: 'etiqueta', text: origem }) : null);
      el.dataset.url = x.url;
      el.addEventListener('click', function () { concluir(x.url, x.titulo, el); });
      return el;
    }
    function preencher() {
      var rolagem = lista.scrollTop;
      lista.textContent = '';
      var mesmo = editando && campo.value.trim() === String(urlAtual || '').trim();
      var termo = mesmo ? '' : semAcento(campo.value.trim());
      var dados = S.sites;
      var total = 0;
      if (dados) {
        var vistos = {};
        [['abas', tr('Abas abertas agora')], ['favoritos', tr('Favoritos')], ['visitados', tr('Mais visitados')]].forEach(function (g) {
          var itens = (dados[g[0]] || []).filter(function (x) {
            var k = x.url.replace(/^https?:\/\/(www\.)?/, '').replace(/#.*$/, '').replace(/\/$/, '');
            if (vistos[k]) return false;
            if (termo && semAcento(x.titulo).indexOf(termo) < 0 && semAcento(x.url).indexOf(termo) < 0) return false;
            vistos[k] = true;
            return true;
          });
          if (!itens.length) return;
          lista.appendChild(h('div', { class: 'grupo-titulo', text: g[1] }));
          itens.forEach(function (x) { lista.appendChild(item(x, g[0] === 'abas' ? x.navegador : null)); total++; });
        });
      }
      var v = campo.value.trim();
      if (v && !mesmo && pareceEndereco(v)) {
        var livre = h('button', { type: 'button', class: 'app-item' }, miniLetra(v), h('span', { text: tr('Abrir ') + v }));
        livre.addEventListener('click', function () { concluir(v, null, livre); });
        lista.insertBefore(livre, lista.firstChild);
        total++;
      }
      if (!total) {
        lista.appendChild(h('div', { class: 'lista-vazia', text: !dados || S.sitesCarregando
          ? tr('Procurando abas, favoritos e sites mais visitados…')
          : (termo ? tr('Nada com “{q}”. Digite o endereço completo (ex.: nome.com).', { q: campo.value.trim() }) : tr('Digite o endereço de um site (ex.: youtube.com).')) }));
      }
      lista.scrollTop = rolagem;
    }
    campo.addEventListener('input', function () { S.buscaSite = campo.value; lista.scrollTop = 0; preencher(); });
    campo.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); enviar(); } });
    botao.addEventListener('click', enviar);
    var atualizar = h('button', { type: 'button', class: 'botao fraco', title: tr('Procurar de novo as abas abertas'), 'aria-label': tr('Atualizar') }, '↻');
    atualizar.addEventListener('click', function () { carregarSites(true); });
    var caixa = h('div', null, h('div', { class: 'linha-campo' }, campo, botao), msg,
      h('div', { class: 'cabeca-lista' }, h('span', { class: 'rotulo', style: 'margin:0', text: tr('Sugestões deste computador') }), atualizar), lista);
    caixa._preencher = preencher;
    S.seletorSite = caixa;
    preencher();
    carregarSites(true);
    return caixa;
  }

  function carregarSites(comAbas) {
    if (S.sitesPedindo) { if (comAbas) S.sitesQuerAbas = true; return; }
    S.sitesPedindo = true;
    api('/api/editor/sites' + (comAbas ? '' : '?abas=0'), { limite: 20000 }).then(function (r) {
      var abas = comAbas ? r.abas : ((S.sites && S.sites.abas) || r.abas);
      S.sites = { abas: abas, favoritos: r.favoritos, visitados: r.visitados };
      S.sitesCarregando = !!r.carregando;
      S.navegadores = r.navegadores || S.navegadores;
      if (S.seletorSite && document.body.contains(S.seletorSite)) S.seletorSite._preencher();
      var querAbas = S.sitesQuerAbas;
      S.sitesQuerAbas = false;
      if (querAbas) { S.sitesPedindo = false; carregarSites(true); }
      else if (S.sitesCarregando) setTimeout(function () { S.sitesPedindo = false; carregarSites(false); }, 1200);
      else S.sitesPedindo = false;
    }).catch(function () {
      S.sitesPedindo = false;
      S.sitesQuerAbas = false;
      setTimeout(function () { if (S.seletorSite && document.body.contains(S.seletorSite)) carregarSites(false); }, 3000);
    });
  }

  function miniLetra(nome) {
    var e = h('span', { class: 'mini-letra', text: (letras(String(nome).trim())[0] || '?').toUpperCase() });
    e.style.setProperty('--matiz', matiz(nome));
    return e;
  }

  function seletorApps(valorAtual, aoEscolher) {
    var campo = h('input', { class: 'campo', type: 'search', placeholder: tr('Procurar app…'), value: S.busca, 'aria-label': tr('Procurar app'), autocomplete: 'off', spellcheck: 'false', 'data-foco': '' });
    var lista = h('div', { class: 'lista-apps', role: 'listbox', 'aria-label': tr('Apps deste computador') });
    var caixa = h('div', { class: 'seletor' }, h('div', { class: 'busca' }, icone('busca'), campo), lista);
    function preencher() {
      var rolagem = lista.scrollTop;
      lista.textContent = '';
      var termo = semAcento(campo.value.trim());
      if (!S.apps || (!S.apps.length && S.appsCarregando)) {
        lista.appendChild(h('div', { class: 'lista-vazia', text: tr('Procurando os apps deste {s}…', { s: S.nomeSistema || tr('computador') }) }));
        return;
      }
      var itens = S.apps.filter(function (a) {
        return !termo || semAcento(a.nome).indexOf(termo) >= 0 || semAcento(a.valor).indexOf(termo) >= 0;
      });
      var exato = itens.some(function (a) { return semAcento(a.nome) === termo || semAcento(a.valor) === termo; });
      itens.forEach(function (a) {
        var sel = !!valorAtual && (a.valor === valorAtual || a.nome === valorAtual);
        var item = h('button', { type: 'button', class: 'app-item', role: 'option', 'aria-selected': String(sel) },
          a.img ? h('img', { src: comToken(a.img), alt: '', loading: 'lazy', draggable: 'false' }) : miniLetra(a.nome),
          h('span', { text: a.nome }), sel ? h('span', { class: 'marca-sel', text: '✓' }) : null);
        item.addEventListener('click', function () { aoEscolher(a); });
        lista.appendChild(item);
      });
      if (termo && !exato) {
        var livre = campo.value.trim();
        var outro = h('button', { type: 'button', class: 'app-item' }, miniLetra(livre), h('span', { text: tr('Usar “{n}” como nome do app', { n: livre }) }));
        outro.addEventListener('click', function () { aoEscolher({ nome: livre, valor: livre, img: null }); });
        lista.appendChild(outro);
      }
      if (!itens.length && !termo) lista.appendChild(h('div', { class: 'lista-vazia', text: tr('Não achei apps neste computador.') }));
      lista.scrollTop = rolagem;
    }
    campo.addEventListener('input', function () { S.busca = campo.value; lista.scrollTop = 0; preencher(); });
    campo.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        var primeiro = lista.querySelector('.app-item');
        if (primeiro) { e.preventDefault(); primeiro.click(); }
      }
    });
    caixa._preencher = preencher;
    S.seletor = caixa;
    preencher();
    carregarApps();
    if (valorAtual) {
      setTimeout(function () {
        var marcado = lista.querySelector('[aria-selected="true"]');
        if (marcado && !campo.value) lista.scrollTop = Math.max(0, marcado.offsetTop - lista.clientHeight / 2 + 20);
      }, 0);
    }
    return caixa;
  }

  function carregarApps() {
    if (S.appsPedindo) return;
    if (S.apps && !S.appsCarregando && Date.now() - (S.appsQuando || 0) < 60000) return;
    S.appsPedindo = true;
    api('/api/editor/apps', { limite: 20000 }).then(function (r) {
      S.apps = r.apps || [];
      S.appsCarregando = !!r.carregando;
      S.appsQuando = Date.now();
      S.apps.forEach(function (a) { if (a.img) S.mapaImg['app:' + a.valor] = a.img; });
      if (S.seletor && document.body.contains(S.seletor)) S.seletor._preencher();
      redesenharTeclas();
      if (S.appsCarregando) setTimeout(function () { S.appsPedindo = false; carregarApps(); }, 1200);
      else S.appsPedindo = false;
    }).catch(function () {
      S.appsPedindo = false;
      setTimeout(carregarApps, 3000);
    });
  }

  var MODS_MAC = { cmd: '⌘', ctrl: '⌃', alt: '⌥', shift: '⇧', win: '⌘' };
  var MODS_PC = { cmd: 'Ctrl', ctrl: 'Ctrl', alt: 'Alt', shift: 'Shift', win: 'Win' };
  var NOMES_TECLAS = { up: '↑', down: '↓', left: '←', right: '→', cima: '↑', baixo: '↓', esquerda: '←', direita: '→', enter: 'Enter', return: 'Enter',
    esc: 'Esc', escape: 'Esc', tab: 'Tab', space: 'Espaço', espaco: 'Espaço', backspace: '⌫', delete: '⌫', del: 'Del', home: 'Home', end: 'End',
    pageup: 'PgUp', pagedown: 'PgDn', print: 'PrtSc', insert: 'Ins' };
  function partesCombo(combo) {
    var s = String(combo || '').trim();
    if (!s) return [];
    if (s === '+') return ['+'];
    if (/\+\+$/.test(s)) return s.slice(0, -2).split('+').map(function (x) { return x.trim(); }).concat(['+']);
    return s.split('+').map(function (x) { return x.trim(); });
  }
  function nomeBonito(parte, ultima) {
    var k = parte.toLowerCase();
    if (!ultima) return (S.sistema === 'mac' ? MODS_MAC : MODS_PC)[k] || parte;
    if (NOMES_TECLAS[k]) return NOMES_TECLAS[k];
    if (/^f\d{1,2}$/.test(k)) return k.toUpperCase();
    return parte.length === 1 ? parte.toUpperCase() : parte;
  }
  function bonitoCombo(combo) {
    var partes = partesCombo(combo);
    var nomes = partes.map(function (x, n) { return nomeBonito(x, n === partes.length - 1); });
    return S.sistema === 'mac' ? nomes.join('') : nomes.join('+');
  }
  function comboEl(combo) {
    var partes = partesCombo(combo);
    var e = h('span', { class: 'combo' });
    partes.forEach(function (x, n) { e.appendChild(h('kbd', { text: nomeBonito(x, n === partes.length - 1) })); });
    return e;
  }
  var CODIGOS = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', Enter: 'enter', NumpadEnter: 'enter', Escape: 'esc',
    Space: 'space', Backspace: 'backspace', Delete: 'del', Home: 'home', End: 'end', PageUp: 'pageup', PageDown: 'pagedown', Insert: 'insert',
    PrintScreen: 'print', Tab: 'tab', Minus: '-', Equal: '=', BracketLeft: '[', BracketRight: ']', Backslash: '\\', Semicolon: ';', Quote: "'",
    Comma: ',', Period: '.', Slash: '/', Backquote: '`', NumpadAdd: 'mais', NumpadSubtract: '-', NumpadMultiply: '*', NumpadDivide: '/', NumpadDecimal: '.' };
  function nomeTecla(e) {
    var c = e.code || '';
    var m = /^Key([A-Z])$/.exec(c);
    if (m) return m[1].toLowerCase();
    m = /^(?:Digit|Numpad)(\d)$/.exec(c);
    if (m) return m[1];
    m = /^F(\d{1,2})$/.exec(c);
    if (m) return 'f' + m[1];
    if (CODIGOS[c]) return CODIGOS[c];
    if (e.key && e.key.length === 1 && !/\s/.test(e.key)) return e.key.toLowerCase();
    return null;
  }
  function modsDe(e) {
    var m = [];
    if (e.ctrlKey) m.push('ctrl');
    if (e.altKey) m.push('alt');
    if (e.shiftKey) m.push('shift');
    if (e.metaKey) m.push(S.sistema === 'mac' ? 'cmd' : 'win');
    return m;
  }
  function gravadorTeclas(atual, aoGravar) {
    var g = h('div', { class: 'gravador', tabindex: '0', role: 'button', 'aria-label': tr('Gravar atalho: clique e aperte as teclas') });
    var combo = atual;
    function mostrar(texto) {
      g.textContent = '';
      if (combo && !texto) g.appendChild(comboEl(combo));
      else g.appendChild(document.createTextNode(texto || tr('Clique aqui e aperte o atalho')));
    }
    mostrar();
    g.addEventListener('focus', function () { if (!combo) mostrar(tr('Aperte as teclas agora…')); });
    g.addEventListener('blur', function () { mostrar(); });
    g.addEventListener('click', function () { g.focus(); });
    g.addEventListener('keydown', function (e) {
      if (e.key === 'Tab' && !e.ctrlKey && !e.metaKey && !e.altKey) return;
      e.preventDefault();
      e.stopPropagation();
      var k = nomeTecla(e);
      var mods = modsDe(e);
      if (!k) {
        mostrar(mods.length ? mods.map(function (x) { return nomeBonito(x, false); }).join(S.sistema === 'mac' ? '' : '+') + (S.sistema === 'mac' ? '' : '+') + '…' : tr('Aperte as teclas agora…'));
        return;
      }
      combo = mods.concat([k]).join('+');
      mostrar();
      aoGravar(combo);
    });
    return g;
  }

  function removerBotao(p, i) {
    var b = botaoEm(p, i);
    if (!b) return;
    var nome = tituloDe(b) || tr('Botão');
    S.sel = null;
    mudar(function () { colocar(p, i, null); });
    toast(tr('“{n}” removido.', { n: nome }), tr('Desfazer'), desfazer);
  }

  function moverBotao(o, d) {
    if (o.p === d.p && o.i === d.i) return;
    var bo = botaoEm(o.p, o.i);
    if (!bo) return;
    var bd = botaoEm(d.p, d.i);
    S.sel = { p: d.p, i: d.i };
    S.tipoNovo = null;
    S.pag = d.p;
    mudar(function () {
      colocar(d.p, d.i, bo);
      colocar(o.p, o.i, bd);
    });
  }

  function moverParaPagina(p, i, q) {
    if (ehPlayer(q)) {
      toast(tr('A página “{p}” é o player (modo DJ) e não tem botões.', { p: nomePagina(q) }), null, null, 'erro');
      desenharPainel();
      return false;
    }
    var destino = null;
    for (var k = 0; k < cap(); k++) if (!botaoEm(q, k)) { destino = k; break; }
    if (destino === null) {
      toast(tr('A página “{p}” está cheia. Libere um espaço ou mude a grade.', { p: nomePagina(q) }), null, null, 'erro');
      desenharPainel();
      return false;
    }
    moverBotao({ p: p, i: i }, { p: q, i: destino });
    toast(tr('Movido para “{p}”.', { p: nomePagina(q) }));
    return true;
  }

  function renomearPagina(p, novo) {
    var antigo = nomePagina(p);
    var nome = nomeUnico(novo, p);
    if (!String(novo || '').trim() || nome === antigo) { desenhar(); return; }
    mudar(function () {
      paginas()[p].nome = nome;
      paginas().forEach(function (pg, q) {
        botoes(q).forEach(function (b) {
          var t = vazioB(b) ? null : tipoCanon(b);
          if (t !== 'pagina' && t !== 'modo') return;
          var alvo = ler(b, 'pagina');
          if (typeof alvo === 'string' && simples(alvo) === simples(antigo)) {
            if (t === 'pagina' && tituloDe(b) === alvo) escrever(b, 'titulo', nome);
            escrever(b, 'pagina', nome);
          }
        });
      });
    });
  }

  function novaPagina() {
    var nome = nomeUnico('Página ' + (paginas().length + 1));
    var p = paginas().length;
    S.pag = p;
    S.sel = null;
    S.tipoNovo = null;
    S.tela = 'pagina';
    mudar(function () { paginas().push({ nome: nome, botoes: [] }); });
    setTimeout(function () { var c = $('#nome-pagina'); if (c) { c.focus(); c.select(); } }, 30);
  }

  function apagarPagina(p) {
    if (paginas().length < 2) return;
    var nome = nomePagina(p);
    S.sel = null;
    S.tela = null;
    S.pag = Math.max(0, p - 1);
    mudar(function () { paginas().splice(p, 1); });
    toast(tr('Página “{p}” apagada.', { p: nome }), tr('Desfazer'), desfazer);
  }

  function moverPagina(de, para) {
    para = Math.max(0, Math.min(paginas().length - 1, para));
    if (de === para) return;
    var atual = paginas()[S.pag];
    var nome = nomePagina(de);
    mudar(function () {
      var pg = paginas().splice(de, 1)[0];
      paginas().splice(para, 0, pg);
    });
    S.pag = paginas().indexOf(atual);
    S.sel = null;
    desenhar();
    toast(tr('“{p}” agora é a página {n}.', { p: nome, n: para + 1 }), tr('Desfazer'), desfazer);
  }

  function focarAba(p) {
    var el = document.querySelector('#abas .aba[data-p="' + p + '"]');
    if (el) el.focus();
  }

  function editarNomeAba(aba, p) {
    S.renomeando = p;
    var campo = h('input', { class: 'aba-renomear', value: nomePagina(p), maxlength: '24', spellcheck: 'false', autocomplete: 'off' });
    aba.replaceWith(campo);
    campo.focus();
    campo.select();
    var feito = false;
    function fim(salvarNome) {
      if (feito) return;
      feito = true;
      S.renomeando = null;
      if (salvarNome) renomearPagina(p, campo.value);
      else desenhar();
    }
    campo.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') fim(true);
      else if (e.key === 'Escape') fim(false);
    });
    campo.addEventListener('blur', function () { fim(true); });
  }

  var arraste = null;
  function alvoEm(x, y) {
    var el = document.elementFromPoint(x, y);
    if (!el) return null;
    var slot = el.closest('.aparelhos .slot');
    if (slot) return { tipo: 'slot', el: slot, p: parseInt(slot.dataset.p, 10), i: parseInt(slot.dataset.i, 10) };
    var aba = el.closest('#abas .aba');
    if (aba) return { tipo: 'aba', el: aba, p: parseInt(aba.dataset.p, 10) };
    return null;
  }
  function limparAlvos() {
    Array.prototype.forEach.call(document.querySelectorAll('.alvo-solta, .aba.alvo'), function (e) { e.classList.remove('alvo-solta', 'alvo'); });
  }

  function comecarArrasteTecla(a, e) {
    var tk = a.el.querySelector('.tecla');
    if (!tk) return false;
    var r = a.el.getBoundingClientRect();
    var k = r.width;
    var f = h('div', { class: 'fantasma' });
    f.style.setProperty('--k', k + 'px');
    f.appendChild(tk.cloneNode(true));
    document.body.appendChild(f);
    a.fantasma = f;
    a.dx = a.x0 - r.left;
    a.dy = a.y0 - r.top;
    a.el.classList.add('origem');
    document.body.classList.add('arrastando');
    return true;
  }

  function moverArrasteTecla(a, e) {
    a.fantasma.style.transform = 'translate(' + (e.clientX - a.dx) + 'px,' + (e.clientY - a.dy) + 'px)';
    limparAlvos();
    var alvo = alvoEm(e.clientX, e.clientY);
    a.alvo = alvo;
    if (!alvo) { clearTimeout(a.mola); a.molaP = null; return; }
    if (alvo.tipo === 'slot') { alvo.el.classList.add('alvo-solta'); clearTimeout(a.mola); a.molaP = null; return; }
    alvo.el.classList.add('alvo');
    if (alvo.p !== S.pag && a.molaP !== alvo.p) {
      clearTimeout(a.mola);
      a.molaP = alvo.p;
      a.mola = setTimeout(function () {
        if (!arraste || arraste !== a) return;
        S.pag = alvo.p;
        desenharAbas();
        desenharPalco();
        var origem = document.querySelector('.aparelhos .slot[data-p="' + a.p + '"][data-i="' + a.i + '"]');
        if (origem) origem.classList.add('origem');
      }, 520);
    }
  }

  function terminarArrasteTecla(a) {
    clearTimeout(a.mola);
    S.redesenharDepois = false;
    if (a.fantasma) a.fantasma.remove();
    document.body.classList.remove('arrastando');
    limparAlvos();
    var alvo = a.alvo;
    if (alvo && alvo.tipo === 'slot') {
      moverBotao({ p: a.p, i: a.i }, { p: alvo.p, i: alvo.i });
      return;
    }
    if (alvo && alvo.tipo === 'aba' && alvo.p !== a.p) {
      if (!moverParaPagina(a.p, a.i, alvo.p)) S.pag = a.p;
      desenhar();
      return;
    }
    desenhar();
  }

  function unidadesDa(a) {
    var unidades = [];
    Array.prototype.forEach.call(a.cont.querySelectorAll(a.seletor), function (el) {
      var p = parseInt(el.dataset.p, 10);
      var r = el.getBoundingClientRect();
      var u = unidades.length && unidades[unidades.length - 1].p === p ? unidades[unidades.length - 1] : null;
      if (!u) { u = { p: p, els: [], ini: Infinity, fim: -Infinity }; unidades.push(u); }
      u.els.push(el);
      u.ini = Math.min(u.ini, a.vertical ? r.top : r.left);
      u.fim = Math.max(u.fim, a.vertical ? r.bottom : r.right);
    });
    return unidades;
  }

  function comecarArrasteAba(a, e) {
    a.unidades = unidadesDa(a);
    a.de = -1;
    a.unidades.forEach(function (u, n) { if (u.p === a.p) a.de = n; });
    if (a.de < 0 || a.unidades.length < 2) return false;
    var minha = a.unidades[a.de];
    var depois = a.unidades[a.de + 1], antes = a.unidades[a.de - 1];
    var folga = depois ? depois.ini - minha.fim : minha.ini - antes.fim;
    a.passo = (minha.fim - minha.ini) + Math.max(0, folga);
    a.rolagem0 = a.vertical ? a.cont.scrollTop : a.cont.scrollLeft;
    var r = a.el.getBoundingClientRect();
    var copia = a.el.cloneNode(true);
    copia.removeAttribute('id');
    var f = copia;
    if (a.tipo === 'pilula') {
      f = h('div', { class: 'pilulas fantasma-pilulas' });
      f.appendChild(copia);
    } else {
      f.classList.add('fantasma-aba');
    }
    f.style.left = r.left + 'px';
    f.style.top = r.top + 'px';
    f.style.width = r.width + 'px';
    f.style.height = r.height + 'px';
    document.body.appendChild(f);
    a.fantasma = f;
    a.r0 = r;
    a.d = a.vertical ? a.y0 - r.top : a.x0 - r.left;
    a.para = a.de;
    minha.els.forEach(function (el) { el.classList.add('segurando'); });
    a.unidades.forEach(function (u) { u.els.forEach(function (el) { el.classList.add('deslizando'); }); });
    document.body.classList.add('arrastando');
    return true;
  }

  function rolarPerto(a, c) {
    var r = a.cont.getBoundingClientRect();
    var ini = a.vertical ? r.top : r.left, fim = a.vertical ? r.bottom : r.right;
    var v = c < ini + 36 ? -10 : c > fim - 36 ? 10 : 0;
    if (!v) return;
    if (a.vertical) a.cont.scrollTop += v;
    else a.cont.scrollLeft += v;
  }

  function moverArrasteAba(a, e) {
    var c = a.vertical ? e.clientY : e.clientX;
    var pos = c - a.d;
    a.fantasma.style.transform = a.vertical ? 'translateY(' + (pos - a.r0.top) + 'px)' : 'translateX(' + (pos - a.r0.left) + 'px)';
    rolarPerto(a, c);
    var desloc = (a.vertical ? a.cont.scrollTop : a.cont.scrollLeft) - a.rolagem0;
    var centro = pos + (a.vertical ? a.r0.height : a.r0.width) / 2 + desloc;
    var para = 0;
    a.unidades.forEach(function (u, n) {
      if (n !== a.de && (u.ini + u.fim) / 2 < centro) para++;
    });
    a.para = para;
    a.unidades.forEach(function (u, n) {
      var t = 0;
      if (n > a.de && n <= para) t = -a.passo;
      else if (n < a.de && n >= para) t = a.passo;
      var valor = t ? (a.vertical ? 'translateY(' : 'translateX(') + t + 'px)' : '';
      u.els.forEach(function (el) { el.style.transform = valor; });
    });
  }

  function terminarArrasteAba(a) {
    document.body.classList.remove('arrastando');
    if (a.fantasma) a.fantasma.remove();
    (a.unidades || []).forEach(function (u) {
      u.els.forEach(function (el) { el.classList.remove('segurando', 'deslizando'); el.style.transform = ''; });
    });
    var redesenhar = S.redesenharDepois;
    S.redesenharDepois = false;
    if (!a.cancelado && typeof a.para === 'number' && a.para !== a.de) {
      moverPagina(a.de, a.para);
      if (a.tipo === 'aba') focarAba(a.para);
      return;
    }
    if (redesenhar) desenhar();
  }

  document.addEventListener('pointermove', function (e) {
    var a = arraste;
    if (!a || e.pointerId !== a.id) return;
    if (!a.ativo) {
      if (Math.hypot(e.clientX - a.x0, e.clientY - a.y0) < 6) return;
      if (a.tipo === 'nada') { arraste = null; return; }
      a.ativo = a.tipo === 'tecla' ? comecarArrasteTecla(a, e) : comecarArrasteAba(a, e);
      if (!a.ativo) { arraste = null; return; }
      try { a.el.setPointerCapture(a.id); } catch (erro) { a.semCaptura = true; }
    }
    e.preventDefault();
    if (a.tipo === 'tecla') moverArrasteTecla(a, e);
    else moverArrasteAba(a, e);
  });
  document.addEventListener('pointerup', function (e) {
    var a = arraste;
    if (!a || e.pointerId !== a.id) return;
    arraste = null;
    if (!a.ativo) { if (a.clique) a.clique(); return; }
    if (a.tipo === 'tecla') terminarArrasteTecla(a);
    else terminarArrasteAba(a);
  });
  function cancelarArraste() {
    var a = arraste;
    arraste = null;
    if (!a || !a.ativo) return;
    a.alvo = null;
    a.cancelado = true;
    if (a.tipo === 'tecla') terminarArrasteTecla(a);
    else terminarArrasteAba(a);
  }
  document.addEventListener('pointercancel', function (e) {
    if (arraste && e.pointerId === arraste.id) cancelarArraste();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && arraste && arraste.ativo) { e.preventDefault(); e.stopPropagation(); cancelarArraste(); }
  }, true);

  function clicarSlot(p, i) {
    if (botaoEm(p, i)) {
      if (!(S.sel && !S.sel.novo && S.sel.p === p && S.sel.i === i)) { S.sel = { p: p, i: i }; S.tipoNovo = null; }
    } else {
      S.sel = { p: p, i: i, novo: true };
      S.tipoNovo = null;
    }
    S.tela = null;
    S.grupo = null;
    S.busca = '';
    desenhar();
  }

  function fecharMenu() { $('#menu-card').hidden = true; S.menuAlvo = null; }
  function abrirMenu(p, i, ancora) {
    var m = $('#menu-card');
    S.menuAlvo = { p: p, i: i };
    m.hidden = false;
    var r = ancora.getBoundingClientRect();
    var larg = m.offsetWidth, alt = m.offsetHeight;
    var x = Math.min(r.right - larg, innerWidth - larg - 8), y = r.bottom + 6;
    if (y + alt > innerHeight - 8) y = r.top - alt - 6;
    m.style.left = Math.max(8, x) + 'px';
    m.style.top = Math.max(8, y) + 'px';
    m.querySelector('button').focus();
  }
  $('#menu-card').addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b || !S.menuAlvo) return;
    var alvo = S.menuAlvo;
    fecharMenu();
    if (b.dataset.acao === 'remover') { removerBotao(alvo.p, alvo.i); return; }
    S.sel = { p: alvo.p, i: alvo.i };
    S.tela = null;
    S.tipoNovo = null;
    desenhar();
    if (b.dataset.acao === 'mover') {
      var sel = $('#painel .mover select');
      if (sel) { sel.focus(); sel.scrollIntoView({ block: 'center' }); }
      else toast(tr('Crie outra página para poder mover botões.'));
    }
  });
  document.addEventListener('pointerdown', function (e) {
    if (!$('#menu-card').hidden && !e.target.closest('#menu-card') && !e.target.closest('.pontos')) fecharMenu();
  }, true);

  $('#aparelhos').addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    if (e.target.closest('.pontos')) return;
    var slot = e.target.closest('.slot');
    if (!slot) return;
    var p = parseInt(slot.dataset.p, 10), i = parseInt(slot.dataset.i, 10);
    arraste = {
      tipo: botaoEm(p, i) ? 'tecla' : 'nada', id: e.pointerId, x0: e.clientX, y0: e.clientY, el: slot, p: p, i: i,
      ativo: false, clique: function () { clicarSlot(p, i); },
    };
  });
  $('#aparelhos').addEventListener('click', function (e) {
    var pontos = e.target.closest('.pontos');
    if (pontos) {
      var slotP = pontos.closest('.slot');
      clicarSlot(parseInt(slotP.dataset.p, 10), parseInt(slotP.dataset.i, 10));
      return;
    }
    if (e.detail !== 0) return;
    var slot = e.target.closest('.slot');
    if (slot) clicarSlot(parseInt(slot.dataset.p, 10), parseInt(slot.dataset.i, 10));
  });
  $('#aparelhos').addEventListener('contextmenu', function (e) {
    var slot = e.target.closest('.slot');
    if (!slot || !botaoEm(parseInt(slot.dataset.p, 10), parseInt(slot.dataset.i, 10))) return;
    e.preventDefault();
    abrirMenu(parseInt(slot.dataset.p, 10), parseInt(slot.dataset.i, 10), slot.querySelector('.pontos') || slot);
  });
  $('#aparelhos').addEventListener('dragstart', function (e) { e.preventDefault(); });

  $('#abas').addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    var aba = e.target.closest('.aba');
    if (!aba) return;
    var p = parseInt(aba.dataset.p, 10);
    arraste = {
      tipo: 'aba', id: e.pointerId, x0: e.clientX, y0: e.clientY, el: aba, p: p, ativo: false,
      cont: $('#abas'), seletor: '.aba-linha', vertical: true,
      clique: function () {
        var agora = Date.now();
        if (S.ultimoCliqueAba && S.ultimoCliqueAba.p === p && agora - S.ultimoCliqueAba.t < 380) {
          S.ultimoCliqueAba = null;
          var atualEl = document.querySelector('#abas .aba[data-p="' + p + '"]');
          if (atualEl) editarNomeAba(atualEl, p);
          return;
        }
        S.ultimoCliqueAba = { p: p, t: agora };
        if (S.pag !== p || S.sel || S.tela) { S.pag = p; S.sel = null; S.tela = null; S.tipoNovo = null; desenhar(); }
      },
    };
  });
  $('#abas').addEventListener('click', function (e) {
    var olho = e.target.closest('.olho');
    if (olho) { alternarOculta(parseInt(olho.dataset.p, 10)); return; }
    if (e.detail !== 0) return;
    var aba = e.target.closest('.aba');
    if (!aba) return;
    S.pag = parseInt(aba.dataset.p, 10);
    S.sel = null;
    S.tela = null;
    desenhar();
  });
  $('#abas').addEventListener('keydown', function (e) {
    var aba = e.target.closest('.aba');
    if (!aba) return;
    var p = parseInt(aba.dataset.p, 10);
    if (e.key === 'F2') { e.preventDefault(); editarNomeAba(aba, p); return; }
    if (e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      e.preventDefault();
      var para = p + (e.key === 'ArrowUp' ? -1 : 1);
      if (para < 0 || para >= paginas().length) return;
      moverPagina(p, para);
      focarAba(para);
    }
  });

  ['#pilulas', '#pilulas-topo'].forEach(function (id) {
    var cont = $(id);
    var irPara = function (p) {
      if (S.pag !== p || S.sel || S.tela) { S.pag = p; S.sel = null; S.tela = null; S.tipoNovo = null; desenhar(); }
    };
    cont.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      var b = e.target.closest('button[data-p]');
      if (!b) return;
      var p = parseInt(b.dataset.p, 10);
      arraste = {
        tipo: 'pilula', id: e.pointerId, x0: e.clientX, y0: e.clientY, el: b, p: p, ativo: false,
        cont: cont, seletor: 'button[data-p]', vertical: false, clique: function () { irPara(p); },
      };
    });
    cont.addEventListener('click', function (e) {
      if (e.detail !== 0) return;
      var b = e.target.closest('button[data-p]');
      if (b) irPara(parseInt(b.dataset.p, 10));
    });
    cont.addEventListener('keydown', function (e) {
      var b = e.target.closest('button[data-p]');
      if (!b || !e.altKey || (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight')) return;
      e.preventDefault();
      var p = parseInt(b.dataset.p, 10);
      var para = p + (e.key === 'ArrowLeft' ? -1 : 1);
      if (para < 0 || para >= paginas().length) return;
      moverPagina(p, para);
      var novo = cont.querySelector('button[data-p="' + para + '"]');
      if (novo) novo.focus();
    });
  });

  function adicionarRapido(tipo) {
    if (ehPlayer(S.pag)) { toast(tr('Esta página é o player (modo DJ). Para pôr botões, mude o tipo da página.'), null, null, 'erro'); return; }
    S.ultimoAdd = tipo;
    var destino = null;
    for (var k = 0; k < cap(); k++) if (!botaoEm(S.pag, k)) { destino = k; break; }
    if (destino === null) { toast(tr('Esta página está cheia. Libere um espaço ou aumente a grade nas configurações.'), null, null, 'erro'); return; }
    S.sel = { p: S.pag, i: destino, novo: true };
    S.tela = null;
    S.tipoNovo = tipo;
    S.busca = '';
    desenhar();
  }
  document.querySelectorAll('.segmentos-add button').forEach(function (b) {
    b.addEventListener('click', function () { adicionarRapido(b.dataset.add); });
  });
  $('#btn-buscar').addEventListener('click', function () {
    var caixa = $('#busca-caixa');
    caixa.hidden = !caixa.hidden;
    if (!caixa.hidden) { $('#busca').focus(); }
    else { S.filtro = ''; $('#busca').value = ''; desenharPalco(); }
  });
  $('#busca').addEventListener('input', function () { S.filtro = $('#busca').value; desenharPalco(); });
  $('#busca').addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { $('#btn-buscar').click(); }
    if (e.key === 'Enter') {
      var primeiro = document.querySelector('.aparelhos .slot:not(.vazio):not(.escondido)') || document.querySelector('.achado');
      if (primeiro) primeiro.click();
    }
  });
  function abrirPagina() { S.sel = null; S.tipoNovo = null; S.tela = 'pagina'; desenhar(); setTimeout(function () { var c = $('#nome-pagina'); if (c) c.focus(); }, 30); }
  function abrirConfig() { S.sel = null; S.tipoNovo = null; S.tela = S.tela === 'config' ? null : 'config'; desenhar(); }
  $('#btn-pagina').addEventListener('click', abrirPagina);
  $('#btn-config').addEventListener('click', abrirConfig);
  $('#config-lateral').addEventListener('click', abrirConfig);
  $('#fechar-gaveta').addEventListener('click', function () { S.sel = null; S.tela = null; S.tipoNovo = null; desenhar(); });

  $('#nova-pagina').addEventListener('click', novaPagina);
  $('#nome-deck').addEventListener('input', function () {
    var v = $('#nome-deck').value;
    mudar(function () { S.cfg.nome = v.trim() ? v : 'Deck'; }, { painel: false, grupo: 'nome-deck' });
  });
  $('#nome-deck').addEventListener('blur', function () { S.grupo = null; if (!$('#nome-deck').value.trim()) $('#nome-deck').value = 'Deck'; });
  $('#nome-deck').addEventListener('keydown', function (e) { if (e.key === 'Enter') $('#nome-deck').blur(); });

  function editando(e) {
    var t = e.target;
    return t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.classList.contains('gravador'));
  }
  document.addEventListener('keydown', function (e) {
    var mod = e.metaKey || e.ctrlKey;
    if (e.key === 'Escape') {
      if (!$('#menu-card').hidden) { fecharMenu(); return; }
      if (!$('#conectar').hidden) { fecharConectar(); return; }
      if (!editando(e) && (S.sel || S.tela)) { S.sel = null; S.tela = null; S.tipoNovo = null; desenhar(); }
      return;
    }
    if (editando(e)) return;
    if (mod && !e.altKey && (e.key === 'z' || e.key === 'Z')) {
      e.preventDefault();
      if (e.shiftKey) refazer(); else desfazer();
      return;
    }
    if (mod && !e.altKey && (e.key === 'y' || e.key === 'Y')) { e.preventDefault(); refazer(); return; }
    if ((e.key === 'Delete' || e.key === 'Backspace') && S.sel && !S.sel.novo && $('#conectar').hidden) {
      e.preventDefault();
      removerBotao(S.sel.p, S.sel.i);
    }
  });

  var esperaMedida = null;
  window.addEventListener('resize', function () {
    cancelAnimationFrame(esperaMedida);
    esperaMedida = requestAnimationFrame(medirTeclas);
  });

  var conectar = null;
  function atualizarConectar() {
    if ($('#conectar').hidden || !S.status) return;
    if (!conectar) conectar = Conectar($('#conectar-ui'));
    conectar.atualizar(S.status);
  }
  function abrirConectar() {
    $('#conectar').hidden = false;
    atualizarConectar();
    $('#fechar-conectar').focus();
  }
  function fecharConectar() {
    $('#conectar').hidden = true;
    if (location.hash === '#conectar') history.replaceState(null, '', location.pathname);
  }
  $('#celular').addEventListener('click', abrirConectar);
  $('#fechar-conectar').addEventListener('click', fecharConectar);
  $('#conectar').addEventListener('click', function (e) { if (e.target === $('#conectar')) fecharConectar(); });

  window.aoTrocarLink = function (token) {
    S.token = token;
    S.status = null;
    toast(tr('Link novo gerado. Escaneie o QR code de novo nos celulares.'));
  };

  function atualizarCelular() {
    var b = $('#celular');
    var recentes = ((S.status && S.status.clientes) || []).filter(function (c) { return c.segundos < 30 && !c.bloqueado; });
    b.classList.toggle('ligado', recentes.length > 0);
    b.classList.toggle('primaria', !recentes.length && !((S.status && S.status.clientes) || []).length);
    b.classList.toggle('alerta', !recentes.length && ((S.status && S.status.avisos) || []).length > 0);
    b.querySelector('span').textContent = recentes.length
      ? (recentes.length > 1 ? tr('{n} aparelhos conectados', { n: recentes.length }) : tr('{a} conectado', { a: recentes[0].aparelho }))
      : (((S.status && S.status.clientes) || []).length ? tr('Celular desconectado') : tr('Conectar celular'));
  }

  function vigiar() {
    api('/api/editor/status', { limite: 6000 }).then(function (r) {
      if (!S.online) { S.online = true; mostrarFaixa(); if (S.sujo) salvar(); }
      if (r.app && S.appVersao && r.app !== S.appVersao) { location.reload(); return; }
      if (r.idioma && window.IDIOMA && r.idioma !== window.IDIOMA && !S.sujo && !S.salvando) { location.reload(); return; }
      if (S.redesenharDepois && !(arraste && arraste.ativo)) { S.redesenharDepois = false; redesenharTeclas(); }
      S.status = r;
      atualizarCelular();
      atualizarConectar();
      if (r.erroConfig !== S.erroConfig && !S.sujo) { S.erroConfig = r.erroConfig || null; mostrarFaixa(); }
      if (r.base !== S.base && !S.sujo && !S.salvando) {
        return api('/api/editor').then(function (d) {
          if (S.sujo || S.salvando) return;
          S.undo = [];
          S.redo = [];
          aplicarDados(d);
          toast(tr('O config.json mudou fora do editor — atualizei aqui.'));
        });
      }
      if (r.geracao !== S.geracao) {
        S.geracao = r.geracao;
        atualizarVisao();
        if (S.seletorSite && document.body.contains(S.seletorSite)) carregarSites(false);
      }
    }).catch(function (e) {
      if (e && e.status === 403) {
        S.online = true;
        mostrarFaixa();
        return;
      }
      S.online = false;
      mostrarFaixa();
    }).finally(function () { setTimeout(vigiar, 2000); });
  }

  function aplicarDados(d) {
    S.sistema = d.sistema || S.sistema;
    S.nomeSistema = d.nomeSistema || S.nomeSistema;
    S.computador = d.computador || S.computador;
    S.tipos = d.tipos || S.tipos;
    S.chaves = d.chavesSistema || S.chaves;
    S.cores = d.cores || S.cores;
    S.navegadores = d.navegadores || S.navegadores;
    if (!S.appVersao) S.appVersao = d.app;
    S.cfg = normalizarCfg(d.config);
    S.base = d.base;
    S.erroConfig = d.erroConfig || null;
    S.geracao = d.geracao;
    aplicarVisao(d.visao);
    S.iconesPagina = d.iconesPagina || S.iconesPagina;
    $('#nome-deck').value = S.cfg.nome || 'Deck';
    corrigirSelecao();
    mostrarFaixa();
    desenhar();
  }

  function iniciar() {
    $('#fechar-conectar').appendChild(icone('fechar'));
    $('#fechar-gaveta').appendChild(icone('fechar'));
    $('#btn-config').appendChild(icone('engrenagem'));
    $('#btn-celular').appendChild(icone('usuario'));
    $('#btn-celular').addEventListener('click', abrirConectar);
    $('#btn-buscar').appendChild(icone('busca'));
    $('#btn-pagina').appendChild(icone('lapis'));
    $('.logo-tile').appendChild(icone('grade'));
    $('#guia-lateral').appendChild(icone('livro'));
    $('#guia-lateral').appendChild(h('span', { text: tr('Como usar') }));
    $('#config-lateral').appendChild(icone('engrenagem'));
    $('#config-lateral').appendChild(h('span', { text: tr('Configurações') }));
    $('#nova-pagina').appendChild(icone('mais'));
    $('#nova-pagina').appendChild(h('span', { text: tr('Nova página') }));
    var addApp = $('.segmentos-add .add-app'), addSite = $('.segmentos-add .add-site');
    addApp.appendChild(icone('app')); addApp.appendChild(h('span', { text: 'Apps' }));
    addSite.appendChild(icone('site')); addSite.appendChild(h('span', { text: 'Sites' }));
    var tentar = function () {
      fetch('/api/editor/sessao', { cache: 'no-store' }).then(function (r) {
        if (r.status === 403) throw Object.assign(new Error('fora'), { status: 403 });
        return r.json();
      }).then(function (s) {
        S.token = s.token;
        return api('/api/editor');
      }).then(function (d) {
        aplicarDados(d);
        mostrarSalvo('');
        vigiar();
        carregarApps();
        if (location.hash === '#conectar') abrirConectar();
      }).catch(function (e) {
        var f = $('#faixa');
        f.className = 'faixa grave';
        f.hidden = false;
        if (e.status === 403) {
          f.textContent = tr('O editor só abre no próprio computador onde o deck está ligado: ') + 'http://localhost:' + (location.port || '8787') + '/editar';
          $('#aparelhos').textContent = '';
          return;
        }
        f.textContent = tr('Não consegui falar com o deck. Ele está ligado? Tentando de novo…');
        setTimeout(tentar, 2500);
      });
    };
    tentar();
  }

  iniciar();
})();
