/* Songs-only position control. Delegated handlers survive internal navigation. */
(() => {
  const control = () => location.pathname.endsWith('/tracks.html') ? document.getElementById('songs-scroll-nav') : null;
  let scheduled = false;
  const extent = () => Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
  function update() {
    scheduled = false;
    const nav = control(); if (!nav) return;
    const max = extent(), percent = max ? Math.round(Math.min(1, Math.max(0, window.scrollY / max)) * 100) : 0;
    nav.hidden = max < 2;
    nav.querySelector('output').textContent = percent + '%';
    nav.querySelector('input').value = percent;
    nav.querySelector('input').setAttribute('aria-valuetext', 'ページの ' + percent + ' パーセント');
    nav.querySelector('[data-scroll-edge="top"]').disabled = percent === 0;
    nav.querySelector('[data-scroll-edge="bottom"]').disabled = percent === 100;
  }
  function schedule() { if (!scheduled) { scheduled = true; window.requestAnimationFrame(update); } }
  for (const name of ['scroll', 'resize', 'pageshow']) window.addEventListener(name, schedule, {passive:true});
  document.addEventListener('input', event => {
    const nav = control(); if (!nav || event.target !== nav.querySelector('input')) return;
    window.scrollTo({top:extent() * Number(event.target.value) / 100, behavior:'instant'}); schedule();
  });
  document.addEventListener('click', event => {
    const nav = control(), button = event.target.closest('[data-scroll-edge]');
    if (!nav || !button || !nav.contains(button) || button.disabled) return;
    event.preventDefault();
    const top = button.dataset.scrollEdge === 'top';
    const target = document.querySelector(top ? 'main h1' : 'body > footer');
    if (target) {
      target.setAttribute('tabindex','-1'); target.focus({preventScroll:true});
      target.addEventListener('blur', () => target.removeAttribute('tabindex'), {once:true});
    }
    window.scrollTo({top:top ? 0 : extent(), behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
  // Filters, late images, player fold and SPA swaps can all change the extent.
  if ('ResizeObserver' in window) new ResizeObserver(schedule).observe(document.body);
  if ('MutationObserver' in window) new MutationObserver(records => {
    if (records.some(r => !r.target.closest?.('#songs-scroll-nav'))) schedule();
  }).observe(document.body, {childList:true,subtree:true});
  update();
})();
