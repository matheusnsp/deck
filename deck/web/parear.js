(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  var ui = Conectar($('#conectar-ui'));

  function atualizar() {
    fetch('/api/parear', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        $('#sub').textContent = 'a ' + (d.computador || 'este computador') + (d.sistema ? ' (' + d.sistema + ')' : '');
        ui.atualizar(d);
      })
      .catch(function () { ui.desligado(); });
  }

  atualizar();
  setInterval(atualizar, 2000);
})();
