/* ParaOkur arayüz modülleri: TR binlik ayraçlı girdi, sekmeler, sözlük terimi kartı. Bağımlılık yok. */
(function () {
  'use strict';

  /* ---- Girdi: yazarken TR binlik ayracı (1.234.567,89). data-money, isteğe bağlı data-decimals="2" ---- */
  function formatMoney(el) {
    var dec = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var v = el.value;
    var caret = el.selectionStart == null ? v.length : el.selectionStart;
    var sig = 0;                                      /* imleçten önceki anlamlı karakter (rakam, virgül) sayısı */
    for (var i = 0; i < caret; i++) if (/[\d,]/.test(v.charAt(i))) sig++;
    var raw = v.replace(/[^\d,]/g, '');
    var ci = raw.indexOf(',');
    var intPart = ci < 0 ? raw : raw.slice(0, ci);
    var frac = ci < 0 || dec === 0 ? null : raw.slice(ci + 1).replace(/,/g, '').slice(0, dec);
    intPart = intPart.replace(/^0+(?=\d)/, '').replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    var out = intPart + (frac === null ? '' : ',' + frac);
    if (out === v) return;
    el.value = out;
    var pos = 0, seen = 0;
    while (pos < out.length && seen < sig) { if (/[\d,]/.test(out.charAt(pos))) seen++; pos++; }
    try { el.setSelectionRange(pos, pos); } catch (e) { /* bazı tarayıcılar desteklemez */ }
  }
  function bindMoney(root) {
    (root || document).querySelectorAll('input[data-money]').forEach(function (el) {
      if (el.__money) return;
      el.__money = true;
      el.addEventListener('beforeinput', function (e) {
        /* Noktalı klavyede "." yazan kullanıcı ondalık kastediyor olabilir: ondalık varsa ve virgül yoksa virgüle çevir */
        if (e.data === '.' && parseInt(el.getAttribute('data-decimals') || '0', 10) > 0 && el.value.indexOf(',') < 0) {
          e.preventDefault();
          var s = el.selectionStart, t = el.selectionEnd;
          el.value = el.value.slice(0, s) + ',' + el.value.slice(t);
          el.setSelectionRange(s + 1, s + 1);
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
      el.addEventListener('input', function () { formatMoney(el); });
      if (el.value) formatMoney(el);
    });
  }
  window.UI = window.UI || {};
  window.UI.bindMoney = bindMoney;
  bindMoney();

  /* ---- Sekmeler: ok tuşları, Home/End, otomatik etkinleştirme ---- */
  document.querySelectorAll('[data-tabs]').forEach(function (box) {
    var tabs = [].slice.call(box.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var p = document.getElementById(t.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t, false); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') n = tabs[0];
        else if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---- Sözlük terimi: <button class="term" data-term="anahtar">; tanımlar #glossary-data JSON'undan ---- */
  var dataEl = document.getElementById('glossary-data');
  var pop = document.getElementById('term-pop');
  if (!dataEl || !pop) return;
  var G = {};
  try { G = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var native = typeof pop.showPopover === 'function';
  var wide = window.matchMedia('(min-width: 720px)');
  var current = null;
  var titleEl = pop.querySelector('.term-title');
  var textEl = pop.querySelector('.term-text');

  function place(btn) {
    if (!wide.matches) { pop.style.top = pop.style.left = ''; return; }
    var r = btn.getBoundingClientRect();
    var w = pop.offsetWidth, h = pop.offsetHeight, vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), vw - w - 8);
    var below = r.bottom + 10 + h <= vh || r.top - 10 - h < 0;
    var top = below ? r.bottom + 10 : r.top - 10 - h;
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
    pop.style.setProperty('--ox', (r.left + r.width / 2 - left) + 'px');
    pop.style.setProperty('--oy', below ? '0' : '100%');
  }
  function close() {
    if (native) { if (pop.matches(':popover-open')) pop.hidePopover(); } else { pop.hidden = true; onClosed(); }
  }
  function onClosed() {
    if (current) { current.setAttribute('aria-expanded', 'false'); current.focus({ preventScroll: true }); current = null; }
  }
  function open(btn) {
    var t = G[btn.getAttribute('data-term')];
    if (!t) return;
    if (current === btn) { close(); return; }
    current = btn;
    titleEl.textContent = t.title;
    textEl.textContent = t.text;
    btn.setAttribute('aria-expanded', 'true');
    if (native) { if (!pop.matches(':popover-open')) pop.showPopover(); } else { pop.hidden = false; }
    place(btn);
    pop.focus({ preventScroll: true });
  }

  if (native) pop.addEventListener('toggle', function (e) { if (e.newState === 'closed') onClosed(); });
  else {
    pop.hidden = true;
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !pop.hidden) close(); });
    document.addEventListener('click', function (e) { if (!pop.hidden && !pop.contains(e.target) && !e.target.closest('.term')) close(); });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.term[data-term]');
    if (b) { e.preventDefault(); open(b); }
  });
  var closeBtn = pop.querySelector('.term-close');
  if (closeBtn) closeBtn.addEventListener('click', close);
  window.addEventListener('resize', function () { if (current) place(current); });
})();
