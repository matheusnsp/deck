(function () {
  'use strict';
  var A = 'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"';
  var ICONES = {
    estrela: '<path d="m12 3.5 2.6 5.4 5.9.8-4.3 4.1 1.1 5.9L12 17l-5.3 2.7 1.1-5.9-4.3-4.1 5.9-.8z"/>',
    grade: '<rect x="4" y="4" width="6.5" height="6.5" rx="1.8"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="1.8"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="1.8"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.8"/>',
    globo: '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
    play: '<rect x="3.5" y="4.5" width="17" height="15" rx="3"/><path d="m10 9 4.5 3-4.5 3z"/>',
    raio: '<path d="M13 3 5 13.5h6L10.5 21 19 10.5h-6z"/>',
    engrenagem: '<circle cx="12" cy="12" r="3"/><path d="M12 3.5v2.2M12 18.3v2.2M3.5 12h2.2M18.3 12h2.2M6 6l1.6 1.6M16.4 16.4 18 18M6 18l1.6-1.6M16.4 7.6 18 6"/>',
    pasta: '<path d="M3.5 7.5A2 2 0 0 1 5.5 5.5h4l2 2h7a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
    casa: '<path d="m4 11 8-7 8 7"/><path d="M6.5 9.5V20h11V9.5"/><path d="M10 20v-5h4v5"/>',
    musica: '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    chat: '<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-5 3.5V17H6.5A2.5 2.5 0 0 1 4 14.5z"/>',
    camera: '<path d="M4 8.5A2 2 0 0 1 6 6.5h2.2l1.3-2h5l1.3 2H18a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><circle cx="12" cy="13" r="3.2"/>',
    codigo: '<path d="m8 8-4.5 4L8 16M16 8l4.5 4L16 16M13.5 5l-3 14"/>',
    coracao: '<path d="M12 20s-7.5-4.6-7.5-10A4 4 0 0 1 12 7.6 4 4 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    maleta: '<rect x="3.5" y="7.5" width="17" height="12" rx="2.5"/><path d="M9 7.5V5.5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3.5 12.5h17"/>',
    jogo: '<path d="M7 7.5h10a4.5 4.5 0 0 1 4.3 5.8l-1 3.3a2.3 2.3 0 0 1-4 .7L15 15.5H9l-1.3 1.8a2.3 2.3 0 0 1-4-.7l-1-3.3A4.5 4.5 0 0 1 7 7.5z"/><path d="M8 10.5v3M6.5 12h3M15.5 11h.01M17.5 13h.01"/>',
    video: '<rect x="3.5" y="6.5" width="12" height="11" rx="2.5"/><path d="m15.5 10.5 5-2.5v8l-5-2.5"/>',
    lampada: '<path d="M9 18h6M10 21h4M8 12a4 4 0 1 1 8 0c0 1.6-1 2.6-1.6 3.4-.4.6-.4 1.1-.4 1.6h-4c0-.5 0-1-.4-1.6C9 14.6 8 13.6 8 12z"/>',
    sino: '<path d="M6.5 16V11a5.5 5.5 0 0 1 11 0v5l1.5 1.5h-14z"/><path d="M10 19.5a2 2 0 0 0 4 0"/>',
  };
  var PALAVRAS = [
    ['estrela', ['favorit', 'principal', 'inicio', 'início', 'home', 'main', 'top']],
    ['grade', ['app', 'program', 'aplic']],
    ['globo', ['site', 'web', 'aba', 'link', 'internet', 'navega']],
    ['play', ['midia', 'mídia', 'media', 'filme', 'video', 'vídeo', 'netflix', 'youtube', 'tv']],
    ['musica', ['music', 'música', 'musica', 'spotify', 'som', 'audio', 'áudio', 'podcast']],
    ['raio', ['produtiv', 'atalho', 'rapid', 'rápid', 'acao', 'ação', 'macro']],
    ['engrenagem', ['config', 'ajuste', 'sistema', 'setting']],
    ['chat', ['chat', 'conversa', 'mensag', 'whatsapp', 'zap', 'telegram', 'discord', 'slack', 'teams', 'reuni']],
    ['maleta', ['trabalho', 'work', 'escrit', 'office', 'empresa', 'negoc', 'negóc']],
    ['camera', ['camera', 'câmera', 'foto', 'captura', 'live', 'stream', 'obs']],
    ['codigo', ['code', 'código', 'codigo', 'dev', 'terminal', 'program']],
    ['jogo', ['game', 'jogo', 'steam', 'xbox', 'play']],
    ['casa', ['casa', 'home', 'lar', 'pessoal']],
    ['coracao', ['saude', 'saúde', 'amor', 'vida', 'bem']],
    ['pasta', ['arquiv', 'pasta', 'doc', 'file']],
  ];
  function svg(chave, classe) {
    var corpo = ICONES[chave] || ICONES.pasta;
    return '<svg viewBox="0 0 24 24" aria-hidden="true"' + (classe ? ' class="' + classe + '"' : '') + ' ' + A + '>' + corpo + '</svg>';
  }
  function elemento(chave, classe) {
    var t = document.createElement('template');
    t.innerHTML = svg(chave, classe);
    return t.content.firstChild;
  }
  function sugerir(nome, indice) {
    var n = String(nome || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    for (var i = 0; i < PALAVRAS.length; i++) {
      var lista = PALAVRAS[i][1];
      for (var j = 0; j < lista.length; j++) {
        var p = lista[j].normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
        if (n.indexOf(p) >= 0) return PALAVRAS[i][0];
      }
    }
    return indice === 0 ? 'estrela' : 'pasta';
  }
  window.ICONES_PAGINA = ICONES;
  window.iconePagina = elemento;
  window.svgPagina = svg;
  window.sugerirIconePagina = sugerir;
  window.SVG_SETA = '<svg viewBox="0 0 24 24" aria-hidden="true" ' + A + '><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  window.SVG_PONTOS = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>';
})();
