(function () {
  'use strict';

  var MODOS = [
    { id: 'wifi', tipo: 'rede', rotulo: 'Wi-Fi' },
    { id: 'usb', tipo: 'usb', rotulo: tr('Cabo USB') },
    { id: 'bluetooth', tipo: 'bluetooth', rotulo: 'Bluetooth' },
    { id: 'compartilhamento', tipo: 'compartilhamento', rotulo: tr('Rede do computador') },
  ];

  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'class') el.className = attrs[k];
      else if (k === 'html') el.innerHTML = attrs[k];
      else if (k === 'text') el.textContent = attrs[k];
      else el.setAttribute(k, attrs[k]);
    });
    for (var i = 2; i < arguments.length; i++) {
      var f = arguments[i];
      if (f == null) continue;
      el.appendChild(typeof f === 'string' ? document.createTextNode(f) : f);
    }
    return el;
  }

  function svgQR(texto) {
    var qr = qrcode(0, 'M');
    qr.addData(texto);
    qr.make();
    var n = qr.getModuleCount();
    var borda = 2;
    var d = '';
    for (var y = 0; y < n; y++) {
      for (var x = 0; x < n; x++) {
        if (qr.isDark(y, x)) d += 'M' + (x + borda) + ',' + (y + borda) + 'h1v1h-1z';
      }
    }
    var lado = n + borda * 2;
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + lado + ' ' + lado +
      '" shape-rendering="crispEdges" role="img" aria-label="' + tr('QR code do link do Deck') + '">' +
      '<rect width="100%" height="100%" fill="#fff"/><path fill="#000" d="' + d + '"/></svg>';
  }

  function passos(modo, sistema) {
    var mac = sistema === 'Mac', win = sistema === 'Windows';
    var salvar = tr('Salve na tela inicial para abrir como app. <small>iPhone: <b>Compartilhar</b> › <b>Adicionar à Tela de Início</b>. Android: menu <b>⋮</b> › <b>Adicionar à tela inicial</b>.</small>');
    if (modo === 'wifi') {
      return [
        tr('Celular no <b>mesmo Wi-Fi</b> deste computador. <small>Redes de visitantes e de empresa costumam isolar os aparelhos; se não abrir, use o cabo USB ou o Bluetooth.</small>'),
        tr('Abra a <b>câmera</b> do celular, aponte para o código e toque no link.'),
        salvar,
      ];
    }
    if (modo === 'usb') {
      return [
        tr('No iPhone: <b>Ajustes › Hotspot Pessoal › Permitir que Outros se Conectem</b>. <small>Android: Ajustes › Conexões › Roteador Wi-Fi e Ancoragem › <b>Ancoragem USB</b>{mac}.</small>', { mac: mac ? tr(' (no Mac, só Android 14 ou mais novo)') : '' }),
        tr('Ligue o <b>cabo</b> entre o celular e o computador. Se o celular perguntar <b>"Confiar neste computador?"</b>, toque em Confiar.'),
        tr('Quando o computador enxergar o celular, o código aparece aqui sozinho. Escaneie com a câmera e ') + salvar.charAt(0).toLowerCase() + salvar.slice(1),
      ];
    }
    if (modo === 'bluetooth') {
      return [
        tr('No iPhone: <b>Ajustes › Hotspot Pessoal</b> ligado, e Bluetooth ligado nos dois aparelhos. <small>Android: Roteador Wi-Fi e Ancoragem › <b>Ancoragem Bluetooth</b>.</small>'),
        mac ? tr('Pareie: <b>Ajustes do Sistema › Bluetooth</b> › conecte ao celular.')
          : win ? tr('Pareie: <b>Configurações › Bluetooth e dispositivos › Adicionar dispositivo</b>.')
          : tr('Pareie o celular nas configurações de Bluetooth do computador.'),
        mac ? tr('Entre na rede do celular: menu <b>Bluetooth</b> da barra › nome do celular › <b>Conectar à Rede</b>. O código aparece aqui quando a conexão subir.')
          : win ? tr('Entre na rede do celular: <b>Bluetooth e dispositivos › Dispositivos</b> › ⋯ no celular › <b>Ingressar em rede de área pessoal</b> › Ponto de acesso. O código aparece aqui quando a conexão subir.')
          : tr('Conecte-se à rede do celular pelo Bluetooth (no GNOME: Configurações › Bluetooth › celular › Acesso à Internet). O código aparece aqui quando a conexão subir.'),
        salvar,
      ];
    }
    if (mac) {
      return [
        tr('<b>Ajustes do Sistema › Geral › Compartilhamento › Compartilhamento de Internet</b> ⓘ: compartilhar a conexão <b>Wi-Fi</b> com computadores que usam <b>Bluetooth PAN</b>. Depois ligue o Compartilhamento de Internet.'),
        tr('No celular: <b>Ajustes › Bluetooth</b> › toque no nome do Mac e aceite o pareamento. <small>Android: depois do pareamento, ⚙ ao lado do Mac › <b>Acesso à Internet</b>.</small>'),
        tr('O código aparece aqui quando a rede subir (o endereço é sempre 192.168.2.1, então não muda). Escaneie e ') + salvar.charAt(0).toLowerCase() + salvar.slice(1),
      ];
    }
    if (win) {
      return [
        tr('<b>Configurações › Rede e Internet › Ponto de acesso móvel</b> › ligar.'),
        tr('No celular, entre no Wi-Fi do computador com o nome e a senha mostrados ali.'),
        tr('O código aparece aqui quando a rede subir (endereço 192.168.137.1, que não muda). Escaneie e ') + salvar.charAt(0).toLowerCase() + salvar.slice(1),
      ];
    }
    return [
      tr('Configurações › Wi-Fi › menu <b>⋮</b> › <b>Ligar ponto de acesso Wi-Fi</b>.'),
      tr('No celular, entre no Wi-Fi do computador com a senha mostrada ali.'),
      tr('O código aparece aqui quando a rede subir. Escaneie e ') + salvar.charAt(0).toLowerCase() + salvar.slice(1),
    ];
  }

  var NOTAS = {
    wifi: tr('Funciona com qualquer celular na mesma rede. É a opção mais simples.'),
    usb: tr('Zero atraso, carrega o celular e não depende de roteador. Enquanto o cabo estiver ligado, o computador pode passar a usar a internet do celular.'),
    bluetooth: tr('Sem cabo e sem roteador. Mais lento que Wi-Fi e cabo, mas sobra para apertar botões.'),
    compartilhamento: tr('Para quando não há Wi-Fi nenhum por perto, ou o plano do celular não tem hotspot. A internet do celular passa a vir pelo computador.'),
  };

  var ESPERAS = {
    usb: tr('Esperando o celular pelo cabo…'),
    bluetooth: tr('Esperando a conexão por Bluetooth…'),
    compartilhamento: tr('Esperando a rede do computador subir…'),
    wifi: tr('Não achei o endereço deste computador na rede. Ele está no Wi-Fi?'),
  };

  function ler(chave, padrao) {
    try { return localStorage.getItem(chave) || padrao; } catch (e) { return padrao; }
  }
  function gravar(chave, valor) {
    try { localStorage.setItem(chave, valor); } catch (e) { return; }
  }

  window.Conectar = function (raiz) {
    var info = null;
    var modo = ler('parear.modo', 'wifi');
    if (!MODOS.some(function (m) { return m.id === modo; })) modo = 'wifi';
    var sub = ler('parear.sub', '');
    var ultimaUrl = null;

    var abas = h('div', { class: 'con-modos', role: 'tablist', 'aria-label': tr('Forma de conexão') });
    MODOS.forEach(function (m) {
      abas.appendChild(h('button', { type: 'button', role: 'tab', 'data-modo': m.id, text: m.rotulo }));
    });
    var qr = h('div', { class: 'qr', id: 'qr' }, h('div', { class: 'falta', text: tr('Gerando o código…') }));
    var subModo = h('div', { class: 'modo', role: 'group', 'aria-label': tr('Tipo de endereço') },
      h('button', { type: 'button', 'data-sub': 'nome', text: tr('Pelo nome') }),
      h('button', { type: 'button', 'data-sub': 'ip', text: tr('Pelo IP') }));
    var subNota = h('p', { class: 'modo-nota', id: 'modo-nota' });
    var detectado = h('p', { class: 'con-detectado', id: 'con-detectado' });
    var lista = h('ol', { class: 'con-passos' });
    var nota = h('p', { class: 'con-nota', id: 'con-nota' });
    var url = h('code', { id: 'url-celular', text: '…' });
    var copiar = h('button', { type: 'button', id: 'copiar', text: tr('Copiar link') });
    var conexaoTxt = h('span', { id: 'conexao-txt', text: tr('Esperando o celular abrir o link…') });
    var conexaoSub = h('small', { id: 'conexao-sub' });
    var conexao = h('div', { class: 'conexao', id: 'conexao', role: 'status' }, h('i'), h('div', null, conexaoTxt, conexaoSub));
    var aparelhos = h('div', { class: 'con-aparelhos', id: 'con-aparelhos' });
    var novoLink = h('button', { type: 'button', class: 'con-novo-link', id: 'novo-link', text: tr('Gerar link novo (desconecta todos)') });
    var avisos = h('div', { class: 'con-avisos', id: 'con-avisos' });
    var dica = h('p', { class: 'con-dica', id: 'con-dica', html: tr('Abriu com a <b>tela preta</b>? Feche o app no celular (deslize para cima) e abra de novo. Se continuar, escaneie o QR code de novo.') });

    raiz.textContent = '';
    raiz.appendChild(abas);
    raiz.appendChild(h('div', { class: 'con-corpo' },
      h('div', { class: 'con-esq' }, qr, subModo, subNota, detectado),
      h('div', { class: 'con-dir' }, lista, nota, h('div', { class: 'link' }, url, copiar), conexao, aparelhos, avisos, dica, novoLink)));

    var token = null;
    function pedir(acao, ip) {
      var enviar = function () {
        return fetch('/api/editor/celulares', {
          method: 'POST', cache: 'no-store',
          headers: { 'Content-Type': 'application/json', 'X-Deck-Token': token || '' },
          body: JSON.stringify({ acao: acao, ip: ip }),
        }).then(function (r) { return r.json(); });
      };
      if (token) return enviar();
      return fetch('/api/editor/sessao', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (sessao) {
        token = sessao.token;
        return enviar();
      });
    }

    function tipoDoModo(m) {
      for (var i = 0; i < MODOS.length; i++) if (MODOS[i].id === m) return MODOS[i].tipo;
      return 'rede';
    }

    function enderecoAtual() {
      if (!info) return null;
      var tipo = tipoDoModo(modo);
      var lista2 = (info.enderecos || []).filter(function (e) { return e.tipo === tipo; });
      if (modo === 'wifi' && !lista2.length && info.urlIp) lista2 = [{ ip: info.ips && info.ips[0], url: info.urlIp, nome: 'Wi-Fi', via: '' }];
      return lista2[0] || null;
    }

    function subAtual() {
      if (sub) return sub;
      return modo === 'wifi' ? (info && info.padrao) || 'ip' : 'ip';
    }

    function urlAtual() {
      if (!info) return null;
      var e = enderecoAtual();
      if (modo !== 'wifi' && !e) return null;
      if (subAtual() === 'nome' && info.urlNome) return info.urlNome;
      return e ? e.url : (info.urlNome || null);
    }

    function desenhar() {
      if (!info) return;
      var sistema = info.sistema || '';
      Array.prototype.forEach.call(abas.children, function (b) {
        var ativo = b.dataset.modo === modo;
        b.setAttribute('aria-selected', String(ativo));
        var tipo = tipoDoModo(b.dataset.modo);
        var tem = (info.enderecos || []).some(function (e) { return e.tipo === tipo; });
        b.classList.toggle('ligado', tem && b.dataset.modo !== 'wifi');
      });
      lista.textContent = '';
      passos(modo, sistema).forEach(function (texto) {
        lista.appendChild(h('li', null, h('span', { html: texto })));
      });
      nota.textContent = NOTAS[modo];
      var e = enderecoAtual();
      var s = subAtual();
      Array.prototype.forEach.call(subModo.children, function (b) { b.setAttribute('aria-pressed', String(b.dataset.sub === s)); });
      subModo.hidden = !info.urlNome || (modo !== 'wifi' && !e);
      if (info.urlNome && !subModo.hidden) {
        subNota.textContent = s === 'nome'
          ? tr('O nome ({n}) continua valendo mesmo se o IP mudar — o melhor para iPhone. Android não abre por nome: use "Pelo IP".', { n: info.nome || '' })
          : tr('Abre em qualquer celular. Se o IP do computador mudar, é preciso escanear de novo') + (modo === 'wifi' ? tr(' — por isso o nome é melhor no iPhone.') : '.');
      } else {
        subNota.textContent = '';
      }
      detectado.textContent = e && modo !== 'wifi' ? (tr('Celular visto em: ') + (e.via || e.nome) + ' · ' + e.ip) : '';
      var u = urlAtual();
      if (!u) {
        qr.innerHTML = '';
        qr.appendChild(h('div', { class: 'falta esperando' }, h('i'), h('span', { text: ESPERAS[modo] })));
        url.textContent = '—';
        ultimaUrl = null;
      } else if (u !== ultimaUrl) {
        qr.innerHTML = svgQR(u);
        url.textContent = u;
        ultimaUrl = u;
      }
      var recentes = (info.clientes || []).filter(function (c) { return c.segundos < 30 && !c.bloqueado; });
      conexao.classList.toggle('ok', recentes.length > 0);
      aparelhos.textContent = '';
      (info.clientes || []).forEach(function (c) {
        var estado = c.bloqueado ? tr('desconectado') : (c.segundos < 30 ? tr('conectado agora') : tr('visto há {t}', { t: tempo(c.segundos) }));
        var botao = h('button', { type: 'button', 'data-ip': c.ip, 'data-acao': c.bloqueado ? 'permitir' : 'desconectar', text: c.bloqueado ? tr('Permitir de novo') : tr('Desconectar') });
        aparelhos.appendChild(h('div', { class: 'con-aparelho' + (c.bloqueado ? ' bloqueado' : ''), 'data-ip': c.ip },
          h('i'), h('span', null, h('b', { text: c.aparelho }), h('small', { text: c.ip + ' · ' + estado })), botao));
      });
      novoLink.hidden = !(info.clientes || []).length && !(info.lembrados || []).length;
      if (recentes.length) {
        conexaoTxt.textContent = recentes.length > 1 ? tr('{n} aparelhos conectados', { n: recentes.length }) : tr('{a} conectado', { a: recentes[0].aparelho });
        conexaoSub.textContent = tr('Pronto — pode fechar esta janela.');
      } else if ((info.clientes || []).length || (info.lembrados || []).length) {
        conexaoTxt.textContent = tr('Nenhum celular conectado agora');
        conexaoSub.textContent = tr('Abra o Deck no celular. Se ele não achar o computador, escaneie o código de novo.');
      } else {
        conexaoTxt.textContent = tr('Esperando o celular abrir o link…');
        conexaoSub.textContent = '';
      }
      avisos.textContent = '';
      (info.avisos || []).forEach(function (a) {
        avisos.appendChild(h('div', { class: 'con-aviso', 'data-tipo': a.tipo, text: a.texto }));
      });
      if (info.erroConfig) avisos.appendChild(h('div', { class: 'con-aviso', 'data-tipo': 'config', text: tr('Problema no config.json: ') + info.erroConfig }));
      dica.hidden = !((info.lembrados || []).length) || recentes.length > 0;
    }

    function tempo(seg) {
      if (seg < 90) return seg + ' s';
      if (seg < 5400) return Math.round(seg / 60) + ' min';
      if (seg < 172800) return Math.round(seg / 3600) + ' h';
      return Math.round(seg / 86400) + tr(' dias');
    }
    aparelhos.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-ip]');
      if (!b) return;
      b.disabled = true;
      pedir(b.dataset.acao, b.dataset.ip).then(function (r) {
        if (!r.ok) { b.disabled = false; alertar(r.mensagem || tr('Não deu.')); }
      }).catch(function () { b.disabled = false; });
    });
    var confirmando = null;
    novoLink.addEventListener('click', function () {
      if (!confirmando) {
        novoLink.textContent = tr('Tem certeza? Todos os celulares vão precisar escanear de novo — clique outra vez');
        novoLink.classList.add('confirmando');
        confirmando = setTimeout(function () { confirmando = null; novoLink.textContent = tr('Gerar link novo (desconecta todos)'); novoLink.classList.remove('confirmando'); }, 5000);
        return;
      }
      clearTimeout(confirmando);
      confirmando = null;
      novoLink.disabled = true;
      pedir('novo-link').then(function (r) {
        novoLink.disabled = false;
        novoLink.classList.remove('confirmando');
        novoLink.textContent = tr('Gerar link novo (desconecta todos)');
        if (r.ok && r.token) {
          token = r.token;
          ultimaUrl = null;
          if (window.aoTrocarLink) window.aoTrocarLink(r.token);
        } else {
          alertar((r && r.mensagem) || tr('Não consegui gerar o link novo.'));
        }
      }).catch(function () { novoLink.disabled = false; });
    });
    function alertar(texto) {
      avisos.appendChild(h('div', { class: 'con-aviso', 'data-tipo': 'erro', text: texto }));
    }

    abas.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-modo]');
      if (!b) return;
      modo = b.dataset.modo;
      gravar('parear.modo', modo);
      desenhar();
    });
    subModo.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-sub]');
      if (!b) return;
      sub = b.dataset.sub;
      gravar('parear.sub', sub);
      desenhar();
    });
    copiar.addEventListener('click', function () {
      var u = urlAtual();
      if (!u) return;
      var avisar = function (texto) {
        copiar.textContent = texto;
        setTimeout(function () { copiar.textContent = tr('Copiar link'); }, 1800);
      };
      var falhou = function () {
        var r = document.createRange();
        r.selectNodeContents(url);
        var sel = getSelection();
        sel.removeAllRanges();
        sel.addRange(r);
        avisar(tr('Selecionado'));
      };
      if (navigator.clipboard) navigator.clipboard.writeText(u).then(function () { avisar(tr('Copiado')); }, falhou);
      else falhou();
    });

    return {
      atualizar: function (novo) { info = novo; desenhar(); },
      desligado: function () {
        conexao.classList.remove('ok');
        conexaoTxt.textContent = tr('O deck foi desligado.');
        conexaoSub.textContent = tr('Ligue de novo no computador.');
      },
      url: urlAtual,
      modo: function () { return modo; },
    };
  };
})();
