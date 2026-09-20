/* Bölümleri kaydırınca belirginleştir (JS yoksa içerik zaten görünür kalır) */
(function () {
  var els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  document.documentElement.classList.add('js');
  if (!('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: .15 });
  els.forEach(function (el) { io.observe(el); });
})();

/* Türkçe sayı ayrıştırma / biçimlendirme + hızlı hesaplama kutusu */
(function () {
  function parse(v) {
    v = String(v == null ? '' : v).replace(/\s/g, '');
    if (!v) return NaN;
    if (v.indexOf(',') > -1) v = v.replace(/\./g, '').replace(',', '.');
    else if ((v.match(/\./g) || []).length > 1) v = v.replace(/\./g, '');
    else if (/^\d{1,3}\.\d{3}$/.test(v)) v = v.replace('.', '');
    return parseFloat(v);
  }
  function fmt(n, d) {
    return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: d, maximumFractionDigits: d }).format(n);
  }
  window.TR = { parse: parse, fmt: fmt };

  document.querySelectorAll('[data-calc]').forEach(function (box) {
    var price = parseFloat(box.getAttribute('data-price'));
    var input = box.querySelector('[data-in]');
    var out = box.querySelector('[data-out]');
    function run() {
      var q = parse(input.value);
      out.textContent = isFinite(q) ? fmt(q * price, 2) : '–';
    }
    input.addEventListener('input', run);
    run();
  });
})();
