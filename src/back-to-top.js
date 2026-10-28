/* Songs alone gets a quiet return-to-top control, including its filtered views. */
(() => {
  const control = () => location.pathname.endsWith('/tracks.html')
    ? document.getElementById('songs-back-to-top') : null;
  let scheduled = false;
  function update() {
    scheduled = false;
    const button = control();
    if (button) button.hidden = window.scrollY < Math.max(500, window.innerHeight * .65);
  }
  function schedule() {
    if (!scheduled) { scheduled = true; window.requestAnimationFrame(update); }
  }
  window.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', schedule, {passive: true});
  window.addEventListener('pageshow', schedule);
  document.addEventListener('click', event => {
    const button = control();
    if (!button || !button.contains(event.target)) return;
    event.preventDefault();
    const heading = document.querySelector('main h1');
    if (heading) {
      heading.setAttribute('tabindex', '-1');
      heading.focus({preventScroll: true});
      heading.addEventListener('blur', () => heading.removeAttribute('tabindex'), {once: true});
    }
    window.scrollTo({top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
  update();
})();
