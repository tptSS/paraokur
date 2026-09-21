/* Site çerçevesi: tema anahtarı, Araçlar açılır menüsü, mobil alt çekmece. Bağımlılık yok. */
(function () {
  var root = document.documentElement;
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  /* Tema: kayıtlı tercih yoksa sistemi izler; anahtar tercihi kaydeder. */
  var themeBtn = document.querySelector('.theme-btn');
  function stored() { try { return localStorage.getItem('po-theme'); } catch (e) { return null; } }
  function label() {
    if (themeBtn) themeBtn.setAttribute('aria-label', root.getAttribute('data-theme') === 'dark' ? 'Açık temaya geç' : 'Koyu temaya geç');
  }
  label();
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('po-theme', next); } catch (e) { /* özel pencere */ }
    label();
  });
  (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(function () {
    if (!stored()) { root.setAttribute('data-theme', mq.matches ? 'dark' : 'light'); label(); }
  });

  /* Araçlar menüsü: Esc ve dışarı tıklama ile kapanır, Esc'de odak düğmeye döner. */
  var menu = document.querySelector('.menu');
  if (menu) {
    document.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    menu.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
    });
    menu.addEventListener('focusout', function (e) {
      if (menu.open && e.relatedTarget && !menu.contains(e.relatedTarget)) menu.open = false;
    });
  }

  /* Mobil çekmece: <dialog> odak tuzağı ve Esc'yi kendisi yönetir. */
  var drawer = document.getElementById('drawer');
  var openBtn = document.querySelector('.menu-btn');
  if (drawer && typeof drawer.showModal === 'function' && openBtn) {
    openBtn.addEventListener('click', function () { drawer.showModal(); });
    drawer.querySelector('.drawer-close').addEventListener('click', function () { drawer.close(); });
    drawer.addEventListener('click', function (e) { if (e.target === drawer) drawer.close(); });   /* boşluğa tıklama */
    drawer.addEventListener('close', function () { openBtn.focus(); });
    drawer.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { drawer.close(); }); });
    var wide = window.matchMedia('(min-width: 900px)');
    (wide.addEventListener ? wide.addEventListener.bind(wide, 'change') : wide.addListener.bind(wide))(function () {
      if (wide.matches && drawer.open) drawer.close();
    });
  }
})();
