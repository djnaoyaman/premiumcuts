/* Progressive enhancement: without JavaScript every artwork remains visible. */
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  let observer;
  function init() {
    const gallery = document.querySelector('.about-page .about-gallery');
    if (!gallery || gallery.dataset.revealReady) return;
    gallery.dataset.revealReady = 'true';
    const figures = [...gallery.querySelectorAll('.about-poster')];
    for (const img of gallery.querySelectorAll('img')) img.draggable = false;
    // Deterrence only. Screenshots and direct resource access remain possible.
    for (const name of ['contextmenu','dragstart']) gallery.addEventListener(name, e => {
      if (e.target.closest('img, .about-poster a')) e.preventDefault();
    });
    if (reduce.matches || !('IntersectionObserver' in window)) return;
    if (observer) observer.disconnect();
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        entry.target.classList.remove('about-reveal-pending'); observer.unobserve(entry.target);
      }
    }, {threshold:.08, rootMargin:'0px 0px -24px 0px'});
    figures.forEach((figure,i) => {
      figure.style.setProperty('--reveal-delay', (i % 2) * 90 + 'ms');
      figure.classList.add('about-reveal-pending'); observer.observe(figure);
    });
    gallery.addEventListener('focusin', e => e.target.closest('.about-poster')?.classList.remove('about-reveal-pending'));
  }
  reduce.addEventListener?.('change', () => {
    if (reduce.matches) {
      observer?.disconnect(); document.querySelectorAll('.about-reveal-pending').forEach(e => e.classList.remove('about-reveal-pending'));
    }
  });
  new MutationObserver(init).observe(document.body,{childList:true,subtree:true});
  init();
})();
