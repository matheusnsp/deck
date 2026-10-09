(function () {
  'use strict';

  var $ = function (s) { return document.querySelector(s); };
  var guardado = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { return; } },
  };

  var el = {
    app: $('#app'), nome: $('#nome'), status: $('#status'), statusTxt: $('#status span'),
    mini: $('#status-mini'), avisos: $('#avisos'), palco: $('#palco'), grade: $('#grade'),
    vazio: $('#vazio'), rodape: $('#rodape'), bancos: $('#bancos'), toast: $('#toast'), dica: $('#dica'),
    dicaTexto: $('#dica-texto'), folha: $('#folha'), folhaLista: $('#folha-lista'),
    telaCheia: document.querySelectorAll('.tela-cheia'),
    minis: document.querySelectorAll('.mini-player'), fichas: document.querySelectorAll('.ficha-foco'),
    foco: $('#foco'), chamada: $('#chamada'),
  };
  var SVG_P = {
    anterior: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><rect x="5" y="5" width="2.4" height="14" rx="1"/><path d="M19 6.3v11.4a1 1 0 0 1-1.5.86l-8.4-5.7a1.1 1.1 0 0 1 0-1.72l8.4-5.7a1 1 0 0 1 1.5.86z"/></svg>',
    proxima: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><rect x="16.6" y="5" width="2.4" height="14" rx="1"/><path d="M5 6.3v11.4a1 1 0 0 0 1.5.86l8.4-5.7a1.1 1.1 0 0 0 0-1.72l-8.4-5.7A1 1 0 0 0 5 6.3z"/></svg>',
    tocar: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M8 5.7v12.6a1 1 0 0 0 1.53.85l10-6.3a1 1 0 0 0 0-1.7l-10-6.3A1 1 0 0 0 8 5.7z"/></svg>',
    pausar: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><rect x="6" y="5" width="4.4" height="14" rx="1.2"/><rect x="13.6" y="5" width="4.4" height="14" rx="1.2"/></svg>',
    som: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/></svg>',
    mudo: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z"/><path d="m16 9.5 5 5M21 9.5l-5 5"/></svg>',
    nota: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>',
    trava: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5.5" y="2.5" width="13" height="19" rx="2.8"/><rect x="8.9" y="11" width="6.2" height="5" rx="1.1"/><path d="M10.1 11V9.6a1.9 1.9 0 0 1 3.8 0V11"/></svg>',
  };

  var busca = new URLSearchParams(location.search);
  var ancora = new URLSearchParams(location.hash.replace(/^#/, ''));
  var tokenUrl = busca.get('k') || ancora.get('k');
  if (tokenUrl) guardado.set('deck.k', tokenUrl);
  var token = tokenUrl || guardado.get('deck.k');
  var manifesto = document.querySelector('link[rel="manifest"]');
  if (manifesto && token) manifesto.setAttribute('href', 'manifest.webmanifest?k=' + encodeURIComponent(token));

  var deck = null;
  var paginas = [];
  var atual = 0;
  var ativos = new Set();
  var indisponiveis = new Set();
  var avisosAtuais = [];
  var erroConfig = null;
  var appVersao = null;
  var pl = null;
  var tocando = null;
  var tocandoEm = 0;
  var timerTocando = null;
  var pedindoTocando = false;
  var arrastandoBarra = null;
  var quadroTempo = null;
  var modoAtual = null;
  var modoEm = 0;
  var focoMinimizado = null;
  var timerFoco = null;
  var chamadaAtual = null;

  function api(caminho, opcoes, limiteMs) {
    opcoes = opcoes || {};
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, limiteMs || 5000);
    var cab = { 'X-Deck-Token': token || '' };
    if (opcoes.body) cab['Content-Type'] = 'application/json';
    return fetch(caminho, {
      method: opcoes.method || 'GET', body: opcoes.body, headers: cab,
      cache: 'no-store', signal: ctl.signal,
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (dados) {
        if (res.status === 401) { var e = new Error('nao-autorizado'); e.status = 401; e.erro = dados.erro; throw e; }
        if (!res.ok && !('ok' in dados)) { var e2 = new Error('HTTP ' + res.status); e2.status = res.status; throw e2; }
        return dados;
      });
    }).finally(function () { clearTimeout(timer); });
  }

  var falhas = 0;
  function definirStatus(tipo, texto) {
    el.status.className = 'status ' + tipo;
    el.mini.className = 'status-mini ' + tipo;
    el.statusTxt.textContent = texto;
    el.mini.title = texto;
    el.mini.setAttribute('aria-label', texto);
  }

  var carregandoDeck = null;
  function carregarDeck() {
    if (carregandoDeck) return carregandoDeck;
    carregandoDeck = api('/api/deck', {}, 6000).then(function (d) {
      var nomeAnterior = paginas[atual] && paginas[atual].nome;
      deck = d;
      if (d.idioma && window.IDIOMA && d.idioma !== window.IDIOMA) { location.reload(); return; }
      erroConfig = d.erroConfig || null;
      if (!appVersao) appVersao = d.app;
      el.nome.textContent = d.nome || 'Deck';
      document.title = d.nome || 'Deck';
      aplicarTema(d.tema);
      document.documentElement.setAttribute('data-luz', d.luz || 'parada');
      montarPaginas();
      if (bloqueio.audio && temPaginaPlayer() < 0) pararBloqueio();
      var salvo = nomeAnterior || guardado.get('deck.pagina');
      var idx = paginas.findIndex(function (p) { return p.nome === salvo; });
      atual = idx >= 0 ? idx : Math.min(atual, Math.max(0, paginas.length - 1));
      mostrarAvisos(d.avisos || []);
      desenhar();
      definirStatus('ok', d.computador || tr('Conectado'));
      falhas = 0;
    }).finally(function () { carregandoDeck = null; });
    return carregandoDeck;
  }

  var vigiando = false;
  function vigiar() {
    if (vigiando || !token || !deck || document.hidden || semAcessoAtivo) return;
    vigiando = true;
    api('/api/espera?v=' + encodeURIComponent(deck.versao) + '&s=' + encodeURIComponent(deck.imgs || ''), {}, 32000)
      .then(function (r) {
        vigiando = false;
        if (appVersao && r.app && r.app !== appVersao) { location.reload(); return; }
        if (deck && (r.versao !== deck.versao || r.imgs !== deck.imgs)) {
          return carregarDeck().then(vigiar, function () { setTimeout(vigiar, 2000); });
        }
        vigiar();
      })
      .catch(function (e) {
        vigiando = false;
        if (e.status === 401) return semAcesso(e.erro);
        setTimeout(vigiar, 2500);
      });
  }

  function aplicarTema(tema) {
    var t = tema === 'normal' ? 'normal' : 'preto';
    document.documentElement.setAttribute('data-tema', t);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', t === 'normal' ? '#1b2028' : '#000000');
  }

  function montarPaginas() {
    var porPagina = Math.max(1, deck.grade.colunas * deck.grade.linhas);
    paginas = [];
    deck.paginas.forEach(function (pg, real) {
      if (pg.oculta) return;
      if (pg.tipo === 'player') {
        paginas.push({ nome: pg.nome, icone: pg.icone || 'musica', real: real, tipo: 'player', botoes: [] });
        return;
      }
      var partes = Math.max(1, Math.ceil(pg.botoes.length / porPagina));
      for (var k = 0; k < partes; k++) {
        paginas.push({
          nome: partes > 1 ? pg.nome + ' ' + (k + 1) : pg.nome,
          icone: pg.icone || (window.sugerirIconePagina ? sugerirIconePagina(pg.nome, real) : 'pasta'),
          real: real,
          botoes: pg.botoes.slice(k * porPagina, (k + 1) * porPagina),
        });
      }
    });
  }

  function desenhar() {
    el.grade.textContent = '';
    if (deck && !paginas.length && deck.paginas.length) {
      mostrarVazio('🙈', tr('Todas as páginas estão ocultas'), tr('No editor do computador, clique no olho ao lado de uma página para ela voltar a aparecer aqui.'));
      desenharBancos();
      return;
    }
    if (!deck || !paginas.length) {
      mostrarVazio('📭', tr('Nenhum botão ainda'), tr('No computador, abra o editor do deck e escolha os apps e sites — eles aparecem aqui na hora.'));
      desenharBancos();
      return;
    }
    el.vazio.hidden = true;
    var pg = paginas[atual];
    el.grade.classList.toggle('modo-player', pg.tipo === 'player');
    pl = null;
    if (pg.tipo === 'player') {
      el.grade.appendChild(criarPlayer());
      desenharTocando();
      agendarTocando(0);
    } else {
      var total = deck.grade.colunas * deck.grade.linhas;
      for (var n = 0; n < total; n++) el.grade.appendChild(criarTecla(pg.botoes[n] || null));
    }
    desenharBancos();
    medir();
    aplicarEstados();
    atualizarMinis();
  }

  function desenharBancos() {
    el.bancos.textContent = '';
    el.rodape.hidden = paginas.length < 2;
    paginas.forEach(function (p, n) {
      var b = document.createElement('button');
      b.type = 'button';
      if (window.iconePagina) b.appendChild(iconePagina(p.icone));
      var rotulo = document.createElement('span');
      rotulo.textContent = p.nome;
      b.appendChild(rotulo);
      if (n === atual) b.setAttribute('aria-current', 'page');
      b.addEventListener('click', function () { irPara(n); });
      el.bancos.appendChild(b);
    });
    var cur = el.bancos.querySelector('[aria-current]');
    if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest', inline: 'center' });
  }

  var segmentador = (typeof Intl !== 'undefined' && Intl.Segmenter) ? new Intl.Segmenter('pt', { granularity: 'grapheme' }) : null;
  function contarLetras(s) {
    return segmentador ? Array.from(segmentador.segment(s)).length : Array.from(s).length;
  }
  var reEmoji = /\p{Extended_Pictographic}|⃣|️|\p{Regional_Indicator}/u;

  function letras(s) {
    s = String(s || '');
    return segmentador ? Array.from(segmentador.segment(s)).map(function (x) { return x.segment; }) : Array.from(s);
  }
  function matiz(s) {
    var n = 0;
    String(s || '').split('').forEach(function (c) { n = (n * 31 + c.charCodeAt(0)) % 3600; });
    return n % 360;
  }
  function letraEm(ico, base) {
    ico.className = 'ico letra';
    ico.textContent = (letras(String(base || '').trim())[0] || '?').toUpperCase();
    ico.style.setProperty('--matiz', matiz(base));
  }
  function brilhoLetra(t, base) {
    if (window.triplaDoMatiz) t.style.setProperty('--tom', triplaDoMatiz(matiz(base)));
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

  function criarTecla(b) {
    var t = document.createElement('button');
    t.type = 'button';
    t.className = 'tecla';
    if (!b) {
      t.classList.add('vazia');
      t.tabIndex = -1;
      t.setAttribute('aria-hidden', 'true');
      return t;
    }
    t._b = b;
    t.dataset.id = b.p + '.' + b.i;
    var corrente = document.createElement('span');
    corrente.className = 'corrente';
    corrente.setAttribute('aria-hidden', 'true');
    ['halo', 'fio'].forEach(function (nome) {
      var faixa = document.createElement('b');
      faixa.className = nome;
      faixa.appendChild(document.createElement('i'));
      corrente.appendChild(faixa);
    });
    t.appendChild(corrente);
    t.setAttribute('aria-label', b.titulo || b.icone || 'Botão');
    if (b.cor) {
      t.style.setProperty('--c', b.cor);
      if (window.triplaDoHex && triplaDoHex(b.cor)) t.style.setProperty('--tom', triplaDoHex(b.cor));
      t.classList.add(corClara(b.cor) ? 'clara' : 'colorida');
    }
    if (b.corAtivo) t.style.setProperty('--luz', b.corAtivo);

    if (b.selo) {
      var led = document.createElement('span');
      led.className = 'led';
      led.textContent = b.selo;
      t.appendChild(led);
    }

    var ico = document.createElement('span');
    ico.className = 'ico';
    var auto = b.tipo === 'app' || b.tipo === 'link';
    if (b.img) {
      var img = new Image();
      img.alt = '';
      img.draggable = false;
      img.decoding = 'async';
      img.onerror = function () { letraEm(ico, b.titulo || b.tipo); brilhoLetra(t, b.titulo || b.tipo); };
      img.src = b.img + (b.img.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(token || '');
      ico.classList.add('figura');
      ico.appendChild(img);
      t.classList.add('com-figura');
      t.appendChild(ico);
      var pintar = function () { if (window.tomDaImagem && !b.cor) tomDaImagem(img, function (tom) { t.style.setProperty('--tom', tripla(tom)); }); };
      pintar();
      if (b.img2 && window.escolherFigura) escolherFigura(img, b.img2 + (b.img2.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(token || ''), function () { img.addEventListener('load', pintar, { once: true }); });
    } else if (b.icone) {
      ico.textContent = b.icone;
      if (!reEmoji.test(b.icone) || contarLetras(b.icone) > 2) ico.classList.add('txt');
      t.appendChild(ico);
    } else if (auto) {
      letraEm(ico, b.titulo || b.tipo);
      brilhoLetra(t, b.titulo || b.tipo);
      t.classList.add('com-figura');
      t.appendChild(ico);
    }
    t._ico = ico;

    var rot = document.createElement('span');
    rot.className = 'rot';
    rot.textContent = b.titulo || '';
    t._rot = rot;
    if (b.titulo) t.appendChild(rot);
    if (!b.icone && !b.img && !auto) t.classList.add('so-texto');

    if (b.erro) {
      var alerta = document.createElement('span');
      alerta.className = 'alerta';
      alerta.textContent = '⚠️';
      t.appendChild(alerta);
    }
    if (window.SVG_SETA && !b.selo) {
      var seta = document.createElement('span');
      seta.className = 'seta';
      seta.innerHTML = SVG_SETA;
      t.appendChild(seta);
    }
    return t;
  }

  function medir() {
    if (!deck) return;
    if (el.grade.classList.contains('modo-player')) {
      var caixa = el.palco.getBoundingClientRect();
      var est = getComputedStyle(el.palco);
      el.grade.style.setProperty('--pw', Math.floor(caixa.width - parseFloat(est.paddingLeft) - parseFloat(est.paddingRight)) + 'px');
      el.grade.style.setProperty('--ph', Math.floor(caixa.height - parseFloat(est.paddingTop) - parseFloat(est.paddingBottom)) + 'px');
      return;
    }
    var deitado = innerWidth > innerHeight;
    var cols = deitado ? deck.grade.colunas : deck.grade.linhas;
    var lins = deitado ? deck.grade.linhas : deck.grade.colunas;
    var r = el.palco.getBoundingClientRect();
    var estilo = getComputedStyle(el.palco);
    var largura = r.width - parseFloat(estilo.paddingLeft) - parseFloat(estilo.paddingRight);
    var altura = r.height - parseFloat(estilo.paddingTop) - parseFloat(estilo.paddingBottom);
    var gap = Math.round(Math.max(8, Math.min(16, Math.min(largura, altura) * 0.03)));
    var k = Math.floor(Math.min((largura - gap * (cols - 1)) / cols, (altura - gap * (lins - 1)) / lins, 220));
    el.grade.style.setProperty('--k', Math.max(44, k) + 'px');
    el.grade.style.setProperty('--gap', gap + 'px');
    el.grade.style.setProperty('--cols', cols);
  }

  function aplicarEstados() {
    Array.prototype.forEach.call(el.grade.children, function (t) {
      var b = t._b;
      if (!b) return;
      var id = t.dataset.id;
      var ligado = ativos.has(id);
      t.classList.toggle('ativa', ligado);
      t.classList.toggle('off', indisponiveis.has(id));
      if (b.tituloAtivo && t._rot) t._rot.textContent = ligado ? b.tituloAtivo : (b.titulo || '');
      if (b.iconeAtivo && t._ico && !b.img) t._ico.textContent = ligado ? b.iconeAtivo : (b.icone || '');
    });
  }

  var timerEstado = null;
  var consultando = false;
  function agendarEstado(ms) {
    clearTimeout(timerEstado);
    timerEstado = setTimeout(atualizarEstado, ms);
  }

  function atualizarEstado() {
    if (!token || document.hidden || semAcessoAtivo) return;
    if (consultando) { agendarEstado(400); return; }
    consultando = true;
    var p = paginas[atual] ? paginas[atual].real : -1;
    api('/api/estado?p=' + p, {}, 4500).then(function (r) {
      if (appVersao && r.app && r.app !== appVersao) { location.reload(); return; }
      var recarregar = !deck || r.versao !== deck.versao || (r.imgs !== undefined && r.imgs !== deck.imgs);
      falhas = 0;
      ativos = new Set(r.ativos || []);
      indisponiveis = new Set(r.indisponiveis || []);
      if (r.erroConfig !== erroConfig) {
        erroConfig = r.erroConfig || null;
        if (deck && !recarregar) mostrarAvisos(deck.avisos || []);
      }
      aplicarModo(r.modo);
      aplicarChamada(r.chamada);
      if (recarregar) return carregarDeck();
      definirStatus('ok', deck.computador || tr('Conectado'));
      aplicarEstados();
    }).catch(function (e) {
      falhas++;
      if (e.status === 401) return semAcesso(e.erro);
      definirStatus(falhas > 2 ? 'off' : 'tentando', falhas > 2 ? tr('Sem conexão com o computador') : tr('Reconectando…'));
    }).finally(function () {
      consultando = false;
      if (!semAcessoAtivo) agendarEstado(falhas ? Math.min(1000 * Math.pow(2, falhas - 1), 8000) : 2000);
    });
  }

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) { agendarEstado(0); agendarTocando(0); pedirTelaLigada(); vigiar(); }
  });
  window.addEventListener('pageshow', function () { agendarEstado(0); });
  window.addEventListener('online', function () { agendarEstado(0); });

  var gestos = new Map();

  el.grade.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    var t = e.target.closest('.tecla');
    var ctl = e.target.closest('[data-ctl]');
    var g = { x: e.clientX, y: e.clientY, t0: performance.now(), modo: 'toque', tecla: t && t._b ? t : null, ctl: ctl };
    gestos.set(e.pointerId, g);
    try { el.grade.setPointerCapture(e.pointerId); } catch (err) { g.semCaptura = true; }
    if (g.tecla) g.tecla.classList.add('pressionada');
    if (ctl && ctl.classList.contains('barra')) {
      if (ctl.classList.contains('travada')) { g.ctl = null; return; }
      g.modo = 'barra';
      arrastandoBarra = ctl;
      moverBarra(ctl, e.clientX);
    } else if (ctl) {
      ctl.classList.add('pressionado');
    }
  });

  el.grade.addEventListener('pointermove', function (e) {
    var g = gestos.get(e.pointerId);
    if (!g) return;
    var dx = e.clientX - g.x;
    var dy = e.clientY - g.y;
    if (g.modo === 'barra') { moverBarra(g.ctl, e.clientX); return; }
    if (g.modo === 'toque') {
      if (gestos.size === 1 && paginas.length > 1 && Math.abs(dx) > 14 && Math.abs(dx) > Math.abs(dy) * 1.3) {
        g.modo = 'arraste';
        soltar(g);
      } else if (Math.hypot(dx, dy) > 24) {
        g.modo = 'cancelado';
        soltar(g);
      }
    }
    if (g.modo === 'arraste') arrastar(dx);
  });

  el.grade.addEventListener('pointerup', function (e) {
    var g = gestos.get(e.pointerId);
    if (!g) return;
    gestos.delete(e.pointerId);
    var dx = e.clientX - g.x;
    if (g.modo === 'arraste') {
      var rapido = Math.abs(dx) / Math.max(1, performance.now() - g.t0) > 0.45;
      if (Math.abs(dx) > 70 || (rapido && Math.abs(dx) > 30)) irPara(atual + (dx < 0 ? 1 : -1), dx < 0 ? -1 : 1);
      else voltarArraste();
      return;
    }
    soltar(g);
    if (g.modo === 'barra') { soltarBarra(g.ctl, e.clientX); return; }
    if (g.modo === 'toque' && g.tecla) acionar(g.tecla);
    else if (g.modo === 'toque' && g.ctl) controlarPlayer(g.ctl.getAttribute('data-ctl'));
  });

  el.grade.addEventListener('pointercancel', function (e) {
    var g = gestos.get(e.pointerId);
    if (!g) return;
    gestos.delete(e.pointerId);
    soltar(g);
    if (g.modo === 'barra') { arrastandoBarra = null; desenharTocando(); }
    if (g.modo === 'arraste') voltarArraste();
  });

  el.grade.addEventListener('click', function (e) {
    if (e.detail !== 0) return;
    var t = e.target.closest('.tecla');
    if (t && t._b) { acionar(t); return; }
    var ctl = e.target.closest('button[data-ctl]');
    if (ctl) controlarPlayer(ctl.getAttribute('data-ctl'));
  });

  el.grade.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); });
  document.addEventListener('touchmove', function (e) {
    if (!e.target.closest('.rolavel, .bancos')) e.preventDefault();
  }, { passive: false });

  function soltar(g) {
    if (g.tecla) g.tecla.classList.remove('pressionada');
    if (g.ctl) g.ctl.classList.remove('pressionado');
  }

  function arrastar(dx) {
    var borda = (atual === 0 && dx > 0) || (atual === paginas.length - 1 && dx < 0);
    var d = borda ? dx * 0.18 : dx * 0.55;
    el.grade.style.transition = 'none';
    el.grade.style.transform = 'translateX(' + d + 'px)';
    el.grade.style.opacity = String(1 - Math.min(0.5, Math.abs(d) / 600));
  }

  function voltarArraste() {
    el.grade.style.transition = 'transform .22s cubic-bezier(.2,.8,.25,1), opacity .22s';
    el.grade.style.transform = '';
    el.grade.style.opacity = '';
  }

  var trocando = false;
  function irPara(n, direcao) {
    if (n < 0 || n >= paginas.length || n === atual || trocando) { voltarArraste(); return; }
    var dir = direcao || (n > atual ? -1 : 1);
    trocando = true;
    var largura = Math.min(innerWidth, 500) * 0.35;
    el.grade.style.transition = 'transform .15s ease-in, opacity .15s ease-in';
    el.grade.style.transform = 'translateX(' + (dir * largura) + 'px)';
    el.grade.style.opacity = '0';
    setTimeout(function () {
      atual = n;
      guardado.set('deck.pagina', paginas[n].nome);
      ativos = new Set();
      indisponiveis = new Set();
      desenhar();
      el.grade.style.transition = 'none';
      el.grade.style.transform = 'translateX(' + (-dir * largura) + 'px)';
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          el.grade.style.transition = 'transform .22s cubic-bezier(.2,.8,.25,1), opacity .22s';
          el.grade.style.transform = '';
          el.grade.style.opacity = '';
          trocando = false;
        });
      });
      agendarEstado(0);
      agendarTocando(0);
    }, 150);
  }

  function irParaReal(indiceReal) {
    var n = paginas.findIndex(function (p) { return p.real === indiceReal; });
    if (n >= 0) irPara(n);
    else if (deck && deck.paginas[indiceReal] && deck.paginas[indiceReal].oculta) toast(tr('Essa página está oculta no celular.'), 'info');
  }

  function vibrar(ms) {
    if (!navigator.vibrate) return;
    try { navigator.vibrate(ms); } catch (e) { return; }
  }

  function acionar(t) {
    var b = t._b;
    if (b.erro) { vibrar([20, 40, 20]); piscar(t, 'erro'); toast(b.erro, 'erro'); return; }

    if (b.confirmar && !t._confirma) {
      vibrar(8);
      limparConfirmacoes();
      var c = document.createElement('span');
      c.className = 'confirma';
      c.textContent = tr('Toque de novo');
      t.appendChild(c);
      t._confirma = setTimeout(function () { limparConfirmacao(t); }, 2600);
      return;
    }
    limparConfirmacao(t);
    vibrar(12);

    if (b.tipo === 'pagina') {
      if (typeof b.destino === 'number') irParaReal(b.destino);
      return;
    }
    if (b.tipo === 'modo') prepararSom();

    t.classList.add('rodando');
    api('/api/apertar', { method: 'POST', body: JSON.stringify({ p: b.p, i: b.i, versao: deck.versao }) }, 9000)
      .then(function (r) {
        if (r.recarregar) {
          toast(r.mensagem || tr('Os botões mudaram no computador.'), 'aviso');
          return carregarDeck();
        }
        if (r.modo !== undefined) aplicarModo(r.modo);
        if (r.ok && b.tipo === 'modo' && r.ativo && typeof b.destino === 'number') irParaReal(b.destino);
        if (r.ok) {
          piscar(t, r.pendente ? 'pendente' : 'ok');
          if (r.info && !(b.selo && typeof r.ativo === 'boolean')) mostrarInfo(t, r.info);
          if (r.mensagem) toast(r.mensagem, r.pendente ? 'info' : 'ok');
        } else {
          vibrar([20, 40, 20]);
          piscar(t, 'erro');
          toast(r.mensagem || tr('Não funcionou.'), 'erro');
        }
        if (typeof r.ativo === 'boolean') {
          if (r.ativo) ativos.add(t.dataset.id); else ativos.delete(t.dataset.id);
          aplicarEstados();
        }
      })
      .catch(function (e) {
        piscar(t, 'erro');
        if (e.status === 401) return semAcesso(e.erro);
        toast(tr('Sem resposta do computador. Ele está ligado, na mesma rede e com o deck aberto?'), 'erro');
        definirStatus('tentando', tr('Reconectando…'));
      })
      .finally(function () {
        t.classList.remove('rodando');
        agendarEstado(350);
      });
  }

  function limparConfirmacao(t) {
    if (!t._confirma) return;
    clearTimeout(t._confirma);
    t._confirma = null;
    var c = t.querySelector('.confirma');
    if (c) c.remove();
  }
  function limparConfirmacoes() {
    Array.prototype.forEach.call(el.grade.children, limparConfirmacao);
  }

  function piscar(t, tipo) {
    t.classList.remove('ok', 'erro', 'pendente');
    void t.offsetWidth;
    t.classList.add(tipo);
    clearTimeout(t._pisca);
    t._pisca = setTimeout(function () { t.classList.remove(tipo); }, tipo === 'erro' ? 700 : 380);
  }

  function mostrarInfo(t, texto) {
    var antigo = t.querySelector('.info');
    if (antigo) antigo.remove();
    clearTimeout(t._info);
    var i = document.createElement('span');
    i.className = 'info';
    i.textContent = texto;
    t.appendChild(i);
    t.classList.add('com-info');
    t._info = setTimeout(function () { i.remove(); t.classList.remove('com-info'); }, 1500);
  }

  var timerToast = null;
  function toast(msg, tipo) {
    el.toast.textContent = msg;
    el.toast.className = 'toast mostra ' + (tipo || '');
    clearTimeout(timerToast);
    timerToast = setTimeout(function () { el.toast.className = 'toast'; },
      tipo === 'erro' ? 6000 : tipo === 'aviso' ? 4000 : 2400);
  }
  el.toast.addEventListener('click', function () { el.toast.className = 'toast'; });

  function mostrarAvisos(lista) {
    avisosAtuais = (erroConfig ? [erroConfig + tr(' — o deck segue com a última versão que funcionava.')] : []).concat(lista);
    el.avisos.hidden = !avisosAtuais.length;
    el.avisos.textContent = avisosAtuais.length === 1 ? tr('1 aviso') : tr('{n} avisos', { n: avisosAtuais.length });
  }
  el.avisos.addEventListener('click', function () {
    el.folhaLista.textContent = '';
    avisosAtuais.forEach(function (a) {
      var li = document.createElement('li');
      li.textContent = a;
      el.folhaLista.appendChild(li);
    });
    el.folha.hidden = false;
  });
  $('#folha-ok').addEventListener('click', function () { el.folha.hidden = true; });
  el.folha.addEventListener('click', function (e) { if (e.target === el.folha) el.folha.hidden = true; });

  function mostrarVazio(icone, titulo, texto) {
    el.grade.textContent = '';
    el.vazio.textContent = '';
    var tecla = document.createElement('div');
    tecla.className = 'tecla-demo';
    tecla.textContent = icone;
    var h = document.createElement('h2');
    h.textContent = titulo;
    var p = document.createElement('p');
    p.textContent = texto;
    el.vazio.append(tecla, h, p);
    el.vazio.hidden = false;
  }

  var semAcessoAtivo = false;
  function semAcesso(erro) {
    semAcessoAtivo = true;
    deck = null;
    paginas = [];
    pararBloqueio();
    el.bancos.textContent = '';
    el.rodape.hidden = true;
    if (erro === 'bloqueado') {
      definirStatus('off', tr('Desconectado'));
      mostrarVazio('⛔', tr('Desconectado pelo computador'), tr('Este aparelho foi desconectado em Conectar celular. Para voltar, peça para liberar lá — e abra o app de novo.'));
      return;
    }
    definirStatus('off', tr('Link inválido'));
    mostrarVazio('🔑', tr('Link antigo'), tr('Este link não vale mais. No computador, abra a página do QR code e escaneie de novo com a câmera do celular.'));
  }

  function el2(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) e.className = classe;
    if (texto !== undefined && texto !== null) e.textContent = texto;
    return e;
  }

  function botaoCtl(acao, rotulo, svg, classe) {
    var b = el2('button', 'ctl' + (classe ? ' ' + classe : ''));
    b.type = 'button';
    b.setAttribute('data-ctl', acao);
    b.setAttribute('aria-label', rotulo);
    b.innerHTML = svg;
    return b;
  }

  function criarPlayer() {
    var raiz = el2('div', 'player sem-midia');
    var fundo = el2('div', 'player-fundo');
    var capa = el2('div', 'player-capa');
    var img = new Image();
    img.alt = '';
    img.draggable = false;
    var nota = el2('span', 'player-nota');
    nota.innerHTML = SVG_P.nota;
    capa.append(img, nota);
    var info = el2('div', 'player-info');
    var app = el2('div', 'player-app');
    var eq = el2('span', 'eq');
    eq.append(el2('i'), el2('i'), el2('i'));
    var appNome = el2('span', 'player-app-nome');
    app.append(eq, appNome);
    var titulo = el2('div', 'player-titulo');
    var artista = el2('div', 'player-artista');
    var barra = el2('div', 'barra posicao');
    barra.setAttribute('data-ctl', 'posicao');
    barra.setAttribute('role', 'slider');
    barra.setAttribute('aria-label', tr('Posição'));
    var cheio = el2('div', 'cheio');
    var bolinha = el2('div', 'bolinha');
    barra.append(cheio, bolinha);
    var tempos = el2('div', 'tempos');
    var ja = el2('span', null, '0:00');
    var total = el2('span', null, '');
    tempos.append(ja, total);
    var controles = el2('div', temSessao ? 'player-controles com-trava' : 'player-controles');
    var alternar = botaoCtl('alternar', tr('Tocar ou pausar'), SVG_P.tocar, 'grande');
    var trava = botaoCtl('bloqueio', tr('Controles na tela bloqueada'), SVG_P.trava, 'pequeno trava');
    var espaco = el2('span', 'ctl pequeno espaco');
    espaco.setAttribute('aria-hidden', 'true');
    if (!temSessao) { trava.hidden = true; espaco.hidden = true; }
    controles.append(espaco, botaoCtl('anterior', tr('Anterior'), SVG_P.anterior), alternar, botaoCtl('proxima', tr('Próxima'), SVG_P.proxima), trava);
    var volume = el2('div', 'player-volume');
    var mudo = botaoCtl('mudo', tr('Mudo'), SVG_P.som, 'pequeno');
    var vbarra = el2('div', 'barra volume');
    vbarra.setAttribute('data-ctl', 'volume');
    vbarra.setAttribute('role', 'slider');
    vbarra.setAttribute('aria-label', tr('Volume'));
    var vcheio = el2('div', 'cheio');
    var vbola = el2('div', 'bolinha');
    vbarra.append(vcheio, vbola);
    var vnum = el2('span', 'vol-num', '');
    volume.append(mudo, vbarra, vnum);
    var vazio = el2('div', 'player-vazio');
    vazio.append(el2('b', null, tr('Nada tocando agora')), el2('span', null, tr('Dê play no Spotify, no YouTube ou em qualquer player do computador — aparece aqui.')));
    info.append(vazio, app, titulo, artista, barra, tempos, controles, volume);
    raiz.append(fundo, capa, info);
    img.addEventListener('load', function () {
      capa.classList.add('com-capa');
      capa.classList.toggle('larga', img.naturalWidth > img.naturalHeight * 1.3);
      if (window.tomDaImagem) tomDaImagem(img, function (tom) {
        raiz.style.setProperty('--tom', tripla(tom));
        if (window.tomClaro) raiz.style.setProperty('--tom-texto', tripla(tomClaro(tom, 0.72)));
      });
    });
    img.addEventListener('error', function () { capa.classList.remove('com-capa'); });
    pl = { raiz: raiz, fundo: fundo, img: img, capa: capa, appNome: appNome, titulo: titulo, artista: artista, barra: barra,
      cheio: cheio, bolinha: bolinha, ja: ja, total: total, alternar: alternar, mudo: mudo, vbarra: vbarra, vcheio: vcheio,
      vbola: vbola, vnum: vnum, trava: trava, capaUrl: null };
    desenharTrava();
    return raiz;
  }

  var temSessao = 'mediaSession' in navigator && typeof window.MediaMetadata === 'function';
  var bloqueio = { querido: temSessao && guardado.get('deck.bloqueio') === '1', suspenso: false, audio: null, url: null, meta: '', estado: '', pular: null, pos: null };

  function desenharTrava() {
    if (!pl || !pl.trava) return;
    pl.trava.classList.toggle('ligado', bloqueio.querido);
    pl.trava.classList.toggle('pausado', !!(bloqueio.querido && bloqueio.suspenso));
    pl.trava.setAttribute('aria-pressed', bloqueio.querido ? 'true' : 'false');
    pl.trava.title = bloqueio.querido ? tr('Controles na tela bloqueada: ligados') : tr('Controles na tela bloqueada: desligados');
  }

  function wavQuaseMudo() {
    var taxa = 8000, total = taxa * 10;
    var dados = new DataView(new ArrayBuffer(44 + total * 2));
    var texto = function (pos, s) { for (var i = 0; i < s.length; i++) dados.setUint8(pos + i, s.charCodeAt(i)); };
    texto(0, 'RIFF');
    dados.setUint32(4, 36 + total * 2, true);
    texto(8, 'WAVEfmt ');
    dados.setUint32(16, 16, true);
    dados.setUint16(20, 1, true);
    dados.setUint16(22, 1, true);
    dados.setUint32(24, taxa, true);
    dados.setUint32(28, taxa * 2, true);
    dados.setUint16(32, 2, true);
    dados.setUint16(34, 16, true);
    texto(36, 'data');
    dados.setUint32(40, total * 2, true);
    for (var n = 0; n < total; n++) dados.setInt16(44 + n * 2, Math.round(66 * Math.sin(2 * Math.PI * 25 * n / taxa)), true);
    return new Blob([dados.buffer], { type: 'audio/wav' });
  }

  function audioDoBloqueio() {
    if (bloqueio.audio) return bloqueio.audio;
    try {
      var a = new Audio();
      a.loop = true;
      a.preload = 'auto';
      bloqueio.url = URL.createObjectURL(wavQuaseMudo());
      a.src = bloqueio.url;
      a.addEventListener('playing', function () {
        bloqueio.suspenso = false;
        desenharTrava();
        atualizarSessao();
        agendarTocando(0);
      });
      a.addEventListener('pause', function () {
        if (a !== bloqueio.audio || !bloqueio.querido) return;
        bloqueio.suspenso = true;
        desenharTrava();
      });
      bloqueio.audio = a;
    } catch (e) { bloqueio.audio = null; }
    return bloqueio.audio;
  }

  function bloqueioTocando() { return !!(bloqueio.querido && bloqueio.audio && !bloqueio.audio.paused); }

  function iniciarBloqueio() {
    if (!bloqueio.querido || semAcessoAtivo || temPaginaPlayer() < 0) return;
    var a = audioDoBloqueio();
    if (!a || !a.paused) return;
    prepararSessao();
    var p = a.play();
    if (p && p.catch) p.catch(function () { return null; });
    agendarTocando(0);
  }

  function pararBloqueio() {
    var a = bloqueio.audio;
    if (a) {
      a.pause();
      a.removeAttribute('src');
      a.load();
    }
    if (bloqueio.url) URL.revokeObjectURL(bloqueio.url);
    bloqueio.audio = null;
    bloqueio.url = null;
    bloqueio.suspenso = false;
    bloqueio.meta = '';
    bloqueio.estado = '';
    bloqueio.pular = null;
    bloqueio.pos = null;
    if (!temSessao) return;
    ['play', 'pause', 'previoustrack', 'nexttrack', 'seekto'].forEach(function (k) {
      try { navigator.mediaSession.setActionHandler(k, null); } catch (e) { return; }
    });
    try { navigator.mediaSession.metadata = null; navigator.mediaSession.playbackState = 'none'; } catch (e) { return; }
  }

  function alternarBloqueio() {
    if (bloqueio.querido && bloqueio.suspenso) {
      bloqueio.suspenso = false;
      iniciarBloqueio();
      desenharTrava();
      vibrar(10);
      toast(tr('Controles na tela bloqueada de volta.'), 'ok');
      return;
    }
    bloqueio.querido = !bloqueio.querido;
    guardado.set('deck.bloqueio', bloqueio.querido ? '1' : '0');
    desenharTrava();
    vibrar(10);
    if (bloqueio.querido) {
      iniciarBloqueio();
      toast(tr('Pronto: bloqueie o celular e controle a música do computador pela tela de bloqueio.'), 'ok');
    } else {
      pararBloqueio();
      toast(tr('Controles na tela bloqueada desligados.'), 'ok');
    }
  }

  function pularPara(d) {
    if (!tocando || !tocando.tem || !(tocando.pode || {}).posicao || !(d && d.seekTime >= 0)) return;
    tocando.posicao = d.seekTime;
    tocandoEm = performance.now();
    desenharTocando();
    enviarPlayer('posicao', Math.round(d.seekTime * 10) / 10);
  }

  function prepararSessao() {
    var acao = function (nome, fn) {
      try { navigator.mediaSession.setActionHandler(nome, fn); } catch (e) { return; }
    };
    acao('play', function () {
      bloqueio.suspenso = false;
      if (bloqueio.audio && bloqueio.audio.paused) {
        var p = bloqueio.audio.play();
        if (p && p.catch) p.catch(function () { return null; });
      }
      if (!(tocando && tocando.tocando)) controlarPlayer('alternar');
    });
    acao('pause', function () { controlarPlayer('alternar'); });
    acao('previoustrack', function () { controlarPlayer('anterior'); });
    acao('nexttrack', function () { controlarPlayer('proxima'); });
    bloqueio.meta = '';
    bloqueio.estado = '';
    bloqueio.pular = null;
    bloqueio.pos = null;
    atualizarSessao();
  }

  function atualizarSessao() {
    if (!temSessao || !bloqueio.querido || !bloqueio.audio) return;
    var ms = navigator.mediaSession;
    var t = tocando || {};
    var capa = new URL(t.tem && t.capa ? t.capa + (t.capa.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(token || '') : 'icon-512.png', location.href).href;
    var titulo = t.tem ? (t.titulo || tr('Sem título')) : tr('Nada tocando no computador');
    var artista = t.tem ? [t.artista, t.album && t.album !== t.titulo ? t.album : ''].filter(Boolean).join(' · ') : ((deck && deck.computador) || '');
    var chave = [titulo, artista, t.app || '', capa].join('\n');
    if (chave !== bloqueio.meta) {
      bloqueio.meta = chave;
      try { ms.metadata = new MediaMetadata({ title: titulo, artist: artista, album: t.tem ? (t.app || '') : 'Deck', artwork: [{ src: capa, sizes: '512x512' }] }); } catch (e) { bloqueio.meta = ''; }
    }
    var estado = t.tem && t.tocando ? 'playing' : 'paused';
    if (estado !== bloqueio.estado) {
      bloqueio.estado = estado;
      try { ms.playbackState = estado; } catch (e) { bloqueio.estado = ''; }
    }
    var pular = !!(t.tem && (t.pode || {}).posicao);
    if (pular !== bloqueio.pular) {
      bloqueio.pular = pular;
      try { ms.setActionHandler('seekto', pular ? pularPara : null); } catch (e) { bloqueio.pular = null; }
    }
    if (!ms.setPositionState) return;
    var p = posicaoAgora();
    var pos = t.tem && t.duracao > 0 && p !== null
      ? { duration: t.duracao, position: Math.max(0, Math.min(p, t.duracao)), playbackRate: t.tocando ? 1 : 0.000001 }
      : { duration: 0, position: 0, playbackRate: 1 };
    var u = bloqueio.pos;
    var agora = performance.now();
    if (u && u.duration === pos.duration && u.playbackRate === pos.playbackRate &&
        Math.abs(Math.min(u.position + (agora - u.em) / 1000 * u.playbackRate, u.duration || Infinity) - pos.position) < 1.5) return;
    try {
      ms.setPositionState(pos);
      bloqueio.pos = { duration: pos.duration, position: pos.position, playbackRate: pos.playbackRate, em: agora };
    } catch (e) { bloqueio.pos = null; }
  }

  ['pointerup', 'touchend', 'click', 'keydown'].forEach(function (tipo) {
    document.addEventListener(tipo, function () {
      if (bloqueio.querido && !bloqueio.suspenso && (!bloqueio.audio || bloqueio.audio.paused)) iniciarBloqueio();
    }, true);
  });

  function relogio(seg) {
    if (!(seg >= 0) || !isFinite(seg)) return '';
    seg = Math.floor(seg);
    var h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60), s2 = seg % 60;
    return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (s2 < 10 ? '0' : '') + s2;
  }

  function posicaoAgora() {
    if (!tocando || !tocando.tem || tocando.posicao === null || tocando.posicao === undefined) return null;
    var p = tocando.posicao + (tocando.tocando ? (performance.now() - tocandoEm) / 1000 : 0);
    return tocando.duracao ? Math.min(p, tocando.duracao) : p;
  }

  function pintarBarra(cheio, bolinha, fracao) {
    var f = Math.max(0, Math.min(1, fracao || 0));
    cheio.style.transform = 'scaleX(' + f + ')';
    bolinha.style.left = (f * 100) + '%';
  }

  function desenharTempo() {
    if (!pl || !tocando || !tocando.tem) return;
    if (arrastandoBarra === pl.barra) return;
    var p = posicaoAgora();
    var d = tocando.duracao;
    pl.ja.textContent = p === null ? '' : relogio(p);
    pl.total.textContent = d ? relogio(d) : '';
    pintarBarra(pl.cheio, pl.bolinha, d && p !== null ? p / d : 0);
  }

  function animarTempo() {
    cancelAnimationFrame(quadroTempo);
    if (!pl || !tocando || !tocando.tem || !tocando.tocando) return;
    var passo = function () {
      desenharTempo();
      if (pl && tocando && tocando.tocando) quadroTempo = requestAnimationFrame(passo);
    };
    quadroTempo = requestAnimationFrame(passo);
  }

  function desenharTocando() {
    atualizarMinis();
    if (!pl) return;
    var t = tocando || {};
    pl.raiz.classList.toggle('sem-midia', !t.tem);
    pl.raiz.classList.toggle('tocando', !!(t.tem && t.tocando));
    if (t.tem) {
      pl.appNome.textContent = t.app || '';
      pl.titulo.textContent = t.titulo || tr('Sem título');
      pl.artista.textContent = [t.artista, t.album && t.album !== t.titulo ? t.album : ''].filter(Boolean).join(' · ');
      pl.alternar.innerHTML = t.tocando ? SVG_P.pausar : SVG_P.tocar;
      pl.alternar.setAttribute('aria-label', t.tocando ? tr('Pausar') : tr('Tocar'));
      var pode = t.pode || {};
      pl.barra.classList.toggle('travada', !pode.posicao);
      pl.raiz.querySelector('[data-ctl="anterior"]').disabled = pode.anterior === false;
      pl.raiz.querySelector('[data-ctl="proxima"]').disabled = pode.proxima === false;
      var url = t.capa ? t.capa + (t.capa.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(token || '') : null;
      if (url !== pl.capaUrl) {
        pl.capaUrl = url;
        pl.capa.classList.remove('com-capa', 'larga');
        pl.raiz.style.removeProperty('--tom');
        pl.raiz.style.removeProperty('--tom-texto');
        if (url) { pl.img.src = url; pl.fundo.style.backgroundImage = 'url("' + url + '")'; }
        else { pl.img.removeAttribute('src'); pl.fundo.style.backgroundImage = ''; }
      }
    } else {
      pl.alternar.innerHTML = SVG_P.tocar;
    }
    var temVol = typeof t.volume === 'number';
    pl.raiz.classList.toggle('sem-volume', !temVol);
    if (temVol && arrastandoBarra !== pl.vbarra) {
      pintarBarra(pl.vcheio, pl.vbola, (t.mudo ? 0 : t.volume) / 100);
      pl.vnum.textContent = t.mudo ? tr('Mudo') : t.volume + '%';
    }
    pl.mudo.innerHTML = t.mudo ? SVG_P.mudo : SVG_P.som;
    pl.mudo.classList.toggle('ativo', !!t.mudo);
    desenharTempo();
    animarTempo();
  }

  function temPaginaPlayer() {
    for (var i = 0; i < paginas.length; i++) if (paginas[i].tipo === 'player') return i;
    return -1;
  }

  function naPaginaPlayer() { return !!(paginas[atual] && paginas[atual].tipo === 'player'); }

  function agendarTocando(ms) {
    clearTimeout(timerTocando);
    timerTocando = setTimeout(atualizarTocando, ms);
  }

  function atualizarTocando() {
    var bloq = bloqueioTocando();
    if (!token || semAcessoAtivo || !deck) return;
    if ((document.hidden || temPaginaPlayer() < 0) && !bloq) return;
    if (pedindoTocando) { agendarTocando(500); return; }
    pedindoTocando = true;
    api('/api/tocando', {}, 7000).then(function (r) {
      tocando = r;
      tocandoEm = performance.now();
      desenharTocando();
      atualizarSessao();
    }).catch(function (e) {
      if (e.status === 401) semAcesso(e.erro);
    }).finally(function () {
      pedindoTocando = false;
      if (!semAcessoAtivo) agendarTocando(document.hidden ? 2500 : (naPaginaPlayer() ? 1000 : 4000));
    });
  }

  function atualizarMinis() {
    var idx = temPaginaPlayer();
    var t = tocando || {};
    var mostrar = idx >= 0 && !naPaginaPlayer() && !!t.tem;
    Array.prototype.forEach.call(el.minis, function (m) {
      m.hidden = !mostrar;
      if (!mostrar) return;
      m.classList.toggle('tocando', !!t.tocando);
      m.setAttribute('aria-label', tr('Tocando agora: {t}', { t: t.titulo || '' }));
      var img = m.querySelector('img');
      var url = t.capa ? t.capa + (t.capa.indexOf('?') < 0 ? '?' : '&') + 'k=' + encodeURIComponent(token || '') : '';
      if (img.getAttribute('src') !== url) { if (url) img.src = url; else img.removeAttribute('src'); }
      m.classList.toggle('sem-capa', !url);
      var rot = m.querySelector('.mini-titulo');
      if (rot) rot.textContent = t.titulo || '';
    });
  }

  Array.prototype.forEach.call(el.minis, function (m) {
    m.addEventListener('click', function () {
      var idx = temPaginaPlayer();
      if (idx >= 0) irPara(idx);
    });
  });

  function fracaoDaBarra(barra, x) {
    var r = barra.getBoundingClientRect();
    return Math.max(0, Math.min(1, (x - r.left) / Math.max(1, r.width)));
  }

  function moverBarra(barra, x) {
    if (!pl || !barra) return;
    var f = fracaoDaBarra(barra, x);
    if (barra === pl.barra) {
      pintarBarra(pl.cheio, pl.bolinha, f);
      if (tocando && tocando.duracao) pl.ja.textContent = relogio(f * tocando.duracao);
    } else {
      pintarBarra(pl.vcheio, pl.vbola, f);
      pl.vnum.textContent = Math.round(f * 100) + '%';
    }
    barra.classList.add('mexendo');
  }

  function soltarBarra(barra, x) {
    arrastandoBarra = null;
    if (!pl || !barra) return;
    barra.classList.remove('mexendo');
    var f = fracaoDaBarra(barra, x);
    if (barra === pl.barra) {
      if (!tocando || !tocando.duracao) return;
      var alvo = Math.round(f * tocando.duracao * 10) / 10;
      tocando.posicao = alvo;
      tocandoEm = performance.now();
      desenharTempo();
      enviarPlayer('posicao', alvo);
    } else {
      var v = Math.round(f * 100);
      if (tocando) { tocando.volume = v; tocando.mudo = false; }
      desenharTocando();
      enviarPlayer('volume', v);
    }
  }

  function enviarPlayer(acao, valor) {
    vibrar(10);
    return api('/api/tocando', { method: 'POST', body: JSON.stringify({ acao: acao, valor: valor }) }, 9000).then(function (r) {
      if (!r.ok) toast(r.mensagem || tr('Não funcionou.'), 'erro');
    }).catch(function (e) {
      if (e.status === 401) return semAcesso(e.erro);
      toast(tr('Sem resposta do computador. Ele está ligado, na mesma rede e com o deck aberto?'), 'erro');
    }).finally(function () { agendarTocando(350); });
  }

  function controlarPlayer(acao) {
    if (acao === 'bloqueio') { alternarBloqueio(); return; }
    if (!acao || acao === 'posicao' || acao === 'volume') return;
    if (bloqueio.querido && bloqueio.suspenso && (acao === 'alternar' || acao === 'anterior' || acao === 'proxima') && !document.hidden) {
      bloqueio.suspenso = false;
      iniciarBloqueio();
    }
    if (acao === 'alternar' && tocando && tocando.tem) {
      tocando.posicao = posicaoAgora();
      tocandoEm = performance.now();
      tocando.tocando = !tocando.tocando;
      desenharTocando();
    }
    if (acao === 'mudo' && tocando) { tocando.mudo = !tocando.mudo; desenharTocando(); }
    enviarPlayer(acao);
  }

  function restanteFoco() {
    if (!modoAtual || modoAtual.restante === undefined) return 0;
    if (modoAtual.concluido) return 0;
    if (modoAtual.pausado) return modoAtual.restante;
    return Math.max(0, modoAtual.restante - (performance.now() - modoEm) / 1000);
  }

  var somFoco = null;
  function prepararSom() {
    try {
      if (!somFoco && (window.AudioContext || window.webkitAudioContext)) somFoco = new (window.AudioContext || window.webkitAudioContext)();
      if (somFoco && somFoco.state === 'suspended') somFoco.resume();
    } catch (e) { somFoco = null; }
  }
  function tocarAviso() {
    vibrar([60, 80, 60, 80, 120]);
    if (!somFoco) return;
    try {
      [0, 0.22, 0.44].forEach(function (atraso, n) {
        var o = somFoco.createOscillator();
        var g = somFoco.createGain();
        o.type = 'sine';
        o.frequency.value = [660, 880, 1046][n];
        g.gain.setValueAtTime(0.0001, somFoco.currentTime + atraso);
        g.gain.exponentialRampToValueAtTime(0.25, somFoco.currentTime + atraso + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, somFoco.currentTime + atraso + 0.5);
        o.connect(g);
        g.connect(somFoco.destination);
        o.start(somFoco.currentTime + atraso);
        o.stop(somFoco.currentTime + atraso + 0.55);
      });
    } catch (e) { return; }
  }

  function aplicarModo(m) {
    var antes = modoAtual;
    modoAtual = m && m.total ? m : null;
    modoEm = performance.now();
    if (!modoAtual) {
      el.foco.hidden = true;
      clearInterval(timerFoco);
      timerFoco = null;
      atualizarFichas();
      return;
    }
    if (!antes || antes.id !== modoAtual.id) focoMinimizado = null;
    if (modoAtual.concluido && !(antes && antes.concluido && antes.id === modoAtual.id)) {
      focoMinimizado = null;
      tocarAviso();
    }
    var f = el.foco;
    f.style.setProperty('--c', modoAtual.cor || '#5e5ce6');
    if (window.triplaDoHex) f.style.setProperty('--tom', triplaDoHex(modoAtual.cor || '#5e5ce6') || '94, 92, 230');
    f.querySelector('.foco-icone').textContent = modoAtual.icone || '⏱';
    f.querySelector('.foco-titulo').textContent = modoAtual.concluido ? tr('{t}: tempo encerrado', { t: modoAtual.titulo }) : modoAtual.titulo;
    f.classList.toggle('concluido', !!modoAtual.concluido);
    f.classList.toggle('pausado', !!modoAtual.pausado);
    var pausa = f.querySelector('[data-foco="pausar"]');
    pausa.hidden = !!modoAtual.concluido;
    pausa.textContent = modoAtual.pausado ? tr('Retomar') : tr('Pausar');
    pausa.setAttribute('data-acao', modoAtual.pausado ? 'retomar' : 'pausar');
    f.querySelector('[data-foco="encerrar"]').textContent = modoAtual.concluido ? tr('Fechar') : tr('Encerrar');
    f.hidden = focoMinimizado === modoAtual.id + (modoAtual.concluido ? 'c' : '');
    tickFoco();
    if (!timerFoco) timerFoco = setInterval(tickFoco, 250);
  }

  function tickFoco() {
    if (!modoAtual) return;
    var r = restanteFoco();
    var txt = relogio(Math.ceil(r));
    el.foco.querySelector('.foco-tempo').textContent = modoAtual.concluido ? '0:00' : txt;
    var anel = el.foco.querySelector('.foco-progresso');
    var total = modoAtual.total || 1;
    var feito = modoAtual.concluido ? 1 : 1 - r / total;
    anel.style.strokeDashoffset = String(Math.max(0, Math.min(1, 1 - feito)) * 100);
    atualizarFichas(txt);
    if (r <= 0 && !modoAtual.concluido && !modoAtual.pausado) agendarEstado(400);
  }

  function atualizarFichas(txt) {
    var mostrar = !!modoAtual && el.foco.hidden;
    Array.prototype.forEach.call(el.fichas, function (fc) {
      fc.hidden = !mostrar;
      if (!mostrar) return;
      fc.style.setProperty('--c', modoAtual.cor || '#5e5ce6');
      fc.querySelector('.ficha-icone').textContent = modoAtual.icone || '⏱';
      fc.querySelector('.ficha-tempo').textContent = modoAtual.concluido ? tr('Fim') : (txt || relogio(Math.ceil(restanteFoco())));
      fc.setAttribute('aria-label', tr('Mostrar o cronômetro de {t}', { t: modoAtual.titulo || '' }));
      fc.classList.toggle('pausado', !!modoAtual.pausado);
    });
  }

  Array.prototype.forEach.call(el.fichas, function (fc) {
    fc.addEventListener('click', function () {
      focoMinimizado = null;
      el.foco.hidden = false;
      atualizarFichas();
    });
  });

  el.foco.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (!b) return;
    prepararSom();
    if (b.classList.contains('foco-minimizar')) {
      focoMinimizado = modoAtual ? modoAtual.id + (modoAtual.concluido ? 'c' : '') : null;
      el.foco.hidden = true;
      atualizarFichas();
      return;
    }
    var acao = b.getAttribute('data-acao') || b.getAttribute('data-foco');
    if (acao === 'encerrar' && modoAtual && modoAtual.concluido) acao = 'fechar';
    vibrar(10);
    api('/api/modo', { method: 'POST', body: JSON.stringify({ acao: acao }) }, 8000).then(function (r) {
      if (r.ok) aplicarModo(r.modo); else toast(r.mensagem || tr('Não funcionou.'), 'erro');
      agendarEstado(300);
    }).catch(function (e2) {
      if (e2.status === 401) return semAcesso(e2.erro);
      toast(tr('Sem resposta do computador. Ele está ligado, na mesma rede e com o deck aberto?'), 'erro');
    });
  });

  function aplicarChamada(c) {
    var antes = chamadaAtual;
    chamadaAtual = c || null;
    if (!chamadaAtual) { el.chamada.hidden = true; return; }
    el.chamada.querySelector('.chamada-quem').textContent = chamadaAtual.quem || tr('Chamada');
    el.chamada.querySelector('.chamada-detalhe').textContent = chamadaAtual.detalhe || tr('Chamada chegando no computador');
    el.chamada.querySelector('[data-chamada="recusar"]').hidden = !chamadaAtual.recusar;
    if (el.chamada.hidden || !antes) vibrar([200, 100, 200]);
    el.chamada.hidden = false;
  }

  el.chamada.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-chamada]');
    if (!b) return;
    var acao = b.getAttribute('data-chamada');
    b.disabled = true;
    api('/api/chamada', { method: 'POST', body: JSON.stringify({ acao: acao }) }, 9000).then(function (r) {
      if (r.ok) { el.chamada.hidden = true; chamadaAtual = null; toast(acao === 'atender' ? tr('Atendendo no computador…') : tr('Chamada recusada.'), 'ok'); }
      else { toast(r.mensagem || tr('Não funcionou.'), 'erro'); el.chamada.hidden = true; }
    }).catch(function (e2) {
      if (e2.status === 401) return semAcesso(e2.erro);
      toast(tr('Sem resposta do computador. Ele está ligado, na mesma rede e com o deck aberto?'), 'erro');
    }).finally(function () { b.disabled = false; agendarEstado(500); });
  });

  var ua = navigator.userAgent;
  var ehIPhone = /iPhone|iPod/.test(ua);
  var ehIOS = ehIPhone || /iPad/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var ehAndroid = /Android/.test(ua);
  var raiz = document.documentElement;
  var noApp = (window.matchMedia && (matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches)) || navigator.standalone === true;
  var suportaCheia = !ehIPhone && !!((raiz.requestFullscreen || raiz.webkitRequestFullscreen) && (document.fullscreenEnabled || document.webkitFullscreenEnabled));

  function emTelaCheia() { return !!(document.fullscreenElement || document.webkitFullscreenElement); }

  function alternarTelaCheia() {
    if (emTelaCheia()) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      return;
    }
    var pedido = (raiz.requestFullscreen || raiz.webkitRequestFullscreen).call(raiz, { navigationUI: 'hide' });
    var travar = function () {
      if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(function () { return null; });
    };
    if (pedido && pedido.then) pedido.then(travar).catch(function () { return null; });
  }

  function atualizarCheia() { document.body.classList.toggle('cheia', emTelaCheia()); }
  document.addEventListener('fullscreenchange', atualizarCheia);
  document.addEventListener('webkitfullscreenchange', atualizarCheia);
  Array.prototype.forEach.call(el.telaCheia, function (b) {
    b.hidden = !suportaCheia || noApp;
    b.addEventListener('click', alternarTelaCheia);
  });

  if (!noApp && !guardado.get('deck.dica') && (ehIOS || ehAndroid)) {
    el.dicaTexto.innerHTML = ehIOS
      ? tr('Para usar como app em tela cheia: toque em <b>Compartilhar</b> e depois em <b>Adicionar à Tela de Início</b>.')
      : tr('Para ter um atalho: menu <b>⋮</b> e depois <b>Adicionar à tela inicial</b>. O botão de tela cheia esconde as barras e deixa deitado.');
    el.dica.hidden = false;
  }
  $('#dica-fechar').addEventListener('click', function () {
    el.dica.hidden = true;
    guardado.set('deck.dica', '1');
  });

  var travaTela = null;
  function pedirTelaLigada() {
    if (!('wakeLock' in navigator) || travaTela) return;
    navigator.wakeLock.request('screen').then(function (t) {
      travaTela = t;
      t.addEventListener('release', function () { travaTela = null; });
    }).catch(function () { return null; });
  }

  var esperaMedida = null;
  var timerMedida = null;
  function medirDeNovo() {
    cancelAnimationFrame(esperaMedida);
    esperaMedida = requestAnimationFrame(medir);
    clearTimeout(timerMedida);
    timerMedida = setTimeout(medir, 400);
  }
  window.addEventListener('resize', medirDeNovo);
  window.addEventListener('orientationchange', medirDeNovo);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', medirDeNovo);
  if (window.ResizeObserver) new ResizeObserver(function () { medir(); }).observe(el.palco);

  if (!token) {
    definirStatus('off', tr('Sem link'));
    mostrarVazio('📷', tr('Conecte ao computador'), tr('No computador, rode o deck e escaneie o QR code com a câmera do celular.'));
    return;
  }

  definirStatus('tentando', tr('Conectando…'));
  carregarDeck().then(function () {
    agendarEstado(0);
    agendarTocando(0);
    pedirTelaLigada();
    vigiar();
  }).catch(function (e) {
    if (e.status === 401) return semAcesso(e.erro);
    definirStatus('off', tr('Sem conexão com o computador'));
    mostrarVazio('📡', tr('Computador fora do alcance'), tr('Confira se o computador está ligado, na mesma rede e com o deck aberto. Tentando de novo…'));
    falhas = 1;
    var tentar = function () {
      carregarDeck().then(function () { agendarEstado(0); vigiar(); }).catch(function (err) {
        if (err.status === 401) return semAcesso(err.erro);
        setTimeout(tentar, 3000);
      });
    };
    setTimeout(tentar, 3000);
  });
})();
