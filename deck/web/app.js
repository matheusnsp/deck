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
      erroConfig = d.erroConfig || null;
      if (!appVersao) appVersao = d.app;
      el.nome.textContent = d.nome || 'Deck';
      document.title = d.nome || 'Deck';
      aplicarTema(d.tema);
      montarPaginas();
      var salvo = nomeAnterior || guardado.get('deck.pagina');
      var idx = paginas.findIndex(function (p) { return p.nome === salvo; });
      atual = idx >= 0 ? idx : Math.min(atual, Math.max(0, paginas.length - 1));
      mostrarAvisos(d.avisos || []);
      desenhar();
      definirStatus('ok', d.computador || 'Conectado');
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
    if (!deck || !paginas.length) {
      mostrarVazio('📭', 'Nenhum botão ainda', 'No computador, abra o editor do deck e escolha os apps e sites — eles aparecem aqui na hora.');
      desenharBancos();
      return;
    }
    el.vazio.hidden = true;
    var pg = paginas[atual];
    var total = deck.grade.colunas * deck.grade.linhas;
    for (var n = 0; n < total; n++) el.grade.appendChild(criarTecla(pg.botoes[n] || null));
    desenharBancos();
    medir();
    aplicarEstados();
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
      if (recarregar) return carregarDeck();
      definirStatus('ok', deck.computador || 'Conectado');
      aplicarEstados();
    }).catch(function (e) {
      falhas++;
      if (e.status === 401) return semAcesso(e.erro);
      definirStatus(falhas > 2 ? 'off' : 'tentando', falhas > 2 ? 'Sem conexão com o computador' : 'Reconectando…');
    }).finally(function () {
      consultando = false;
      if (!semAcessoAtivo) agendarEstado(falhas ? Math.min(1000 * Math.pow(2, falhas - 1), 8000) : 2000);
    });
  }

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) { agendarEstado(0); pedirTelaLigada(); vigiar(); }
  });
  window.addEventListener('pageshow', function () { agendarEstado(0); });
  window.addEventListener('online', function () { agendarEstado(0); });

  var gestos = new Map();

  el.grade.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    var t = e.target.closest('.tecla');
    var g = { x: e.clientX, y: e.clientY, t0: performance.now(), modo: 'toque', tecla: t && t._b ? t : null };
    gestos.set(e.pointerId, g);
    try { el.grade.setPointerCapture(e.pointerId); } catch (err) { g.semCaptura = true; }
    if (g.tecla) g.tecla.classList.add('pressionada');
  });

  el.grade.addEventListener('pointermove', function (e) {
    var g = gestos.get(e.pointerId);
    if (!g) return;
    var dx = e.clientX - g.x;
    var dy = e.clientY - g.y;
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
    if (g.modo === 'toque' && g.tecla) acionar(g.tecla);
  });

  el.grade.addEventListener('pointercancel', function (e) {
    var g = gestos.get(e.pointerId);
    if (!g) return;
    gestos.delete(e.pointerId);
    soltar(g);
    if (g.modo === 'arraste') voltarArraste();
  });

  el.grade.addEventListener('click', function (e) {
    if (e.detail !== 0) return;
    var t = e.target.closest('.tecla');
    if (t && t._b) acionar(t);
  });

  el.grade.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); });
  document.addEventListener('touchmove', function (e) {
    if (!e.target.closest('.rolavel, .bancos')) e.preventDefault();
  }, { passive: false });

  function soltar(g) { if (g.tecla) g.tecla.classList.remove('pressionada'); }

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
    }, 150);
  }

  function irParaReal(indiceReal) {
    var n = paginas.findIndex(function (p) { return p.real === indiceReal; });
    if (n >= 0) irPara(n);
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
      c.textContent = 'Toque de novo';
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

    t.classList.add('rodando');
    api('/api/apertar', { method: 'POST', body: JSON.stringify({ p: b.p, i: b.i, versao: deck.versao }) }, 9000)
      .then(function (r) {
        if (r.recarregar) {
          toast(r.mensagem || 'Os botões mudaram no computador.', 'aviso');
          return carregarDeck();
        }
        if (r.ok) {
          piscar(t, r.pendente ? 'pendente' : 'ok');
          if (r.info && !(b.selo && typeof r.ativo === 'boolean')) mostrarInfo(t, r.info);
          if (r.mensagem) toast(r.mensagem, r.pendente ? 'info' : 'ok');
        } else {
          vibrar([20, 40, 20]);
          piscar(t, 'erro');
          toast(r.mensagem || 'Não funcionou.', 'erro');
        }
        if (typeof r.ativo === 'boolean') {
          if (r.ativo) ativos.add(t.dataset.id); else ativos.delete(t.dataset.id);
          aplicarEstados();
        }
      })
      .catch(function (e) {
        piscar(t, 'erro');
        if (e.status === 401) return semAcesso(e.erro);
        toast('Sem resposta do computador. Ele está ligado, na mesma rede e com o deck aberto?', 'erro');
        definirStatus('tentando', 'Reconectando…');
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
    avisosAtuais = (erroConfig ? [erroConfig + ' — o deck segue com a última versão que funcionava.'] : []).concat(lista);
    el.avisos.hidden = !avisosAtuais.length;
    el.avisos.textContent = avisosAtuais.length === 1 ? '1 aviso' : avisosAtuais.length + ' avisos';
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
    el.bancos.textContent = '';
    el.rodape.hidden = true;
    if (erro === 'bloqueado') {
      definirStatus('off', 'Desconectado');
      mostrarVazio('⛔', 'Desconectado pelo computador', 'Este aparelho foi desconectado em Conectar celular. Para voltar, peça para liberar lá — e abra o app de novo.');
      return;
    }
    definirStatus('off', 'Link inválido');
    mostrarVazio('🔑', 'Link antigo', 'Este link não vale mais. No computador, abra a página do QR code e escaneie de novo com a câmera do celular.');
  }

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
      ? 'Para usar como app em tela cheia: toque em <b>Compartilhar</b> e depois em <b>Adicionar à Tela de Início</b>.'
      : 'Para ter um atalho: menu <b>⋮</b> e depois <b>Adicionar à tela inicial</b>. O botão de tela cheia esconde as barras e deixa deitado.';
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
  window.addEventListener('resize', function () {
    cancelAnimationFrame(esperaMedida);
    esperaMedida = requestAnimationFrame(medir);
  });

  if (!token) {
    definirStatus('off', 'Sem link');
    mostrarVazio('📷', 'Conecte ao computador', 'No computador, rode o deck e escaneie o QR code com a câmera do celular.');
    return;
  }

  definirStatus('tentando', 'Conectando…');
  carregarDeck().then(function () {
    agendarEstado(0);
    pedirTelaLigada();
    vigiar();
  }).catch(function (e) {
    if (e.status === 401) return semAcesso(e.erro);
    definirStatus('off', 'Sem conexão com o computador');
    mostrarVazio('📡', 'Computador fora do alcance', 'Confira se o computador está ligado, na mesma rede e com o deck aberto. Tentando de novo…');
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
