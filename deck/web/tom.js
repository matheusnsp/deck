(function () {
  'use strict';
  var cache = {};

  function hsl(R, G, B) {
    var r = R / 255, g = G / 255, b = B / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    var l = (mx + mn) / 2;
    var s = d ? d / (1 - Math.abs(2 * l - 1)) : 0;
    var h = 0;
    if (d) {
      if (mx === r) h = ((g - b) / d) % 6;
      else if (mx === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    return [h, s, l];
  }

  function medir(img) {
    var n = 32;
    var c = document.createElement('canvas');
    c.width = n;
    c.height = n;
    var g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0, n, n);
    var d = g.getImageData(0, 0, n, n).data;
    var caixas = [];
    for (var k = 0; k < 12; k++) caixas.push({ peso: 0, r: 0, g: 0, b: 0 });
    var opacos = 0;
    for (var i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 140) continue;
      opacos++;
      var v = hsl(d[i], d[i + 1], d[i + 2]);
      if (v[1] < 0.22 || v[2] < 0.12 || v[2] > 0.9) continue;
      var w = v[1] * (1 - Math.abs(v[2] - 0.5));
      var cx = caixas[Math.floor(v[0] / 30) % 12];
      cx.peso += w;
      cx.r += d[i] * w;
      cx.g += d[i + 1] * w;
      cx.b += d[i + 2] * w;
    }
    if (!opacos) return null;
    var melhor = null;
    for (var j = 0; j < 12; j++) {
      var soma = caixas[j].peso + caixas[(j + 1) % 12].peso * 0.5 + caixas[(j + 11) % 12].peso * 0.5;
      if (!melhor || soma > melhor.soma) melhor = { soma: soma, caixa: caixas[j] };
    }
    if (!melhor || melhor.caixa.peso < opacos * 0.015) return null;
    var cx2 = melhor.caixa;
    var r = cx2.r / cx2.peso, gg = cx2.g / cx2.peso, b = cx2.b / cx2.peso;
    var f = Math.min(255 / Math.max(r, gg, b, 1), 1.4);
    return { r: Math.round(r * f), g: Math.round(gg * f), b: Math.round(b * f) };
  }

  function brancura(img) {
    var n = 24;
    var c = document.createElement('canvas');
    c.width = n;
    c.height = n;
    var g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0, n, n);
    var d = g.getImageData(0, 0, n, n).data;
    var opacos = 0, brancos = 0, x0 = n, y0 = n, x1 = -1, y1 = -1;
    for (var i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 200) continue;
      opacos++;
      var x = (i / 4) % n, y = Math.floor(i / 4 / n);
      if (x < x0) x0 = x;
      if (x > x1) x1 = x;
      if (y < y0) y0 = y;
      if (y > y1) y1 = y;
      if (d[i] > 228 && d[i + 1] > 228 && d[i + 2] > 228) brancos++;
    }
    if (!opacos) return 0;
    var caixa = (x1 - x0 + 1) * (y1 - y0 + 1);
    var cheio = opacos / caixa;
    return cheio > 0.7 && caixa >= n * n * 0.2 ? brancos / opacos : 0;
  }

  var cacheBranco = {};
  window.fundoBranco = function (img) {
    var chave = img.currentSrc || img.src;
    if (chave in cacheBranco) return cacheBranco[chave];
    var r = false;
    try { r = brancura(img) > 0.45; } catch (e) { r = false; }
    cacheBranco[chave] = r;
    return r;
  };

  window.escolherFigura = function (img, alternativa, aoTrocar) {
    if (!alternativa) return;
    var checar = function () {
      var branco = window.fundoBranco(img);
      var pequeno = img.naturalWidth > 0 && img.naturalWidth < 64;
      if (!branco && !pequeno) return;
      var teste = new Image();
      teste.onload = function () {
        if (branco && window.fundoBranco(teste) && teste.naturalWidth < img.naturalWidth) return;
        if (!branco && teste.naturalWidth <= img.naturalWidth) return;
        img.src = teste.src;
        if (aoTrocar) aoTrocar();
      };
      teste.src = alternativa;
    };
    if (img.complete && img.naturalWidth) checar();
    else img.addEventListener('load', checar, { once: true });
  };

  window.tomDaImagem = function (img, cb) {
    var chave = img.currentSrc || img.src;
    if (!chave) return;
    if (chave in cache) {
      if (cache[chave]) cb(cache[chave]);
      return;
    }
    var pronto = function () {
      var tom = null;
      try { tom = medir(img); } catch (e) { tom = null; }
      cache[chave] = tom;
      if (tom) cb(tom);
    };
    if (img.complete && img.naturalWidth) pronto();
    else img.addEventListener('load', pronto, { once: true });
  };

  window.brilhoDe = function (tom, alfa) {
    return 'rgba(' + tom.r + ',' + tom.g + ',' + tom.b + ',' + alfa + ')';
  };

  window.tomClaro = function (tom, minimo) {
    var v = hsl(tom.r, tom.g, tom.b);
    var h = v[0], sat = Math.min(v[1], 0.85), l = Math.max(v[2], minimo);
    var c = (1 - Math.abs(2 * l - 1)) * sat, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = l - c / 2;
    var r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; } else if (h < 120) { r = x; g = c; } else if (h < 180) { g = c; b = x; }
    else if (h < 240) { g = x; b = c; } else if (h < 300) { r = x; b = c; } else { r = c; b = x; }
    return { r: Math.round((r + m) * 255), g: Math.round((g + m) * 255), b: Math.round((b + m) * 255) };
  };

  window.tripla = function (tom) {
    return tom.r + ', ' + tom.g + ', ' + tom.b;
  };

  window.triplaDoHex = function (hex) {
    var m = /^#?([0-9a-f]{6})$/i.exec(hex || '');
    if (!m) return null;
    var v = parseInt(m[1], 16);
    return ((v >> 16) & 255) + ', ' + ((v >> 8) & 255) + ', ' + (v & 255);
  };

  window.triplaDoMatiz = function (h) {
    var c = 0.55, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = 0.48 - c / 2;
    var r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; } else if (h < 120) { r = x; g = c; } else if (h < 180) { g = c; b = x; }
    else if (h < 240) { g = x; b = c; } else if (h < 300) { r = x; b = c; } else { r = c; b = x; }
    return Math.round((r + m) * 255) + ', ' + Math.round((g + m) * 255) + ', ' + Math.round((b + m) * 255);
  };
})();
