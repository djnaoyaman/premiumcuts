/* A single, brief first-visit sweep of the homepage. Never a scroll lock. */
(() => {
  const key = 'premium-cuts-home-intro-v1';
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let active = null;
  function stop() {
    if (!active) return;
    active.cancelled = true;
    window.cancelAnimationFrame(active.frame);
    for (const remove of active.listeners) remove();
    active = null;
  }
  window.initPremiumHomeIntro = ({fromHistory = false} = {}) => {
    const main = document.getElementById('main');
    if (active?.main === main && !fromHistory) return;
    stop();
    const path = location.pathname.replace(/index\.html$/, '');
    const home = path === '/' || path === '/premiumcuts/';
    const navigation = window.performance.getEntriesByType('navigation')[0];
    if (!home || !main || location.hash || fromHistory || motion.matches ||
        document.visibilityState !== 'visible' ||
        (navigation && navigation.type !== 'navigate')) return;
    try {
      if (sessionStorage.getItem(key)) return;
      sessionStorage.setItem(key, '1');
    } catch { return; } // No storage: skip rather than repeat on every visit.
    const run = active = {main, cancelled: false, frame: 0, listeners: []};
    function listen(target, event, handler = stop) {
      target.addEventListener(event, handler, {passive: true});
      run.listeners.push(() => target.removeEventListener(event, handler));
    }
    for (const event of ['wheel', 'touchstart', 'pointerdown', 'keydown', 'popstate', 'pagehide']) listen(window, event);
    listen(document, 'visibilitychange', () => { if (document.visibilityState !== 'visible') stop(); });
    if (motion.addEventListener) listen(motion, 'change', () => { if (motion.matches) stop(); });
    const frame = callback => { run.frame = window.requestAnimationFrame(callback); };
    let timer;
    const fonts = document.fonts?.ready || Promise.resolve();
    Promise.race([fonts, new Promise(resolve => {timer = window.setTimeout(resolve, 800);})]).then(() => {
      window.clearTimeout(timer);
      if (run.cancelled) return;
      // Two paint frames let the existing font/layout settle without hiding it.
      frame(() => frame(() => {
        if (run.cancelled || document.getElementById('main') !== main || location.hash || window.scrollY > 4) { stop(); return; }
        const bottom = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight) - window.innerHeight;
        if (bottom < window.innerHeight) { stop(); return; }
        window.scrollTo({top: bottom, behavior: 'instant'});
        const start = window.performance.now();
        function tick(now) {
          if (run.cancelled) return;
          const progress = Math.min(1, (now - start) / 680);
          window.scrollTo({top: bottom * Math.pow(1 - progress, 3), behavior: 'instant'});
          if (progress < 1) frame(tick); else stop();
        }
        frame(tick);
      }));
    }, stop);
  };
  window.initPremiumHomeIntro();
})();
