/* Informational only: no membership detection or player/cookie configuration changes. */
(function (root) {
  'use strict';
  function create(options) {
    const host = options.host, doc = host.ownerDocument;
    const key = options.key, schedule = options.setTimeout || root.setTimeout.bind(root);
    const cancel = options.clearTimeout || root.clearTimeout.bind(root);
    let used = false, node = null, timer = null;
    function dismiss() { if (timer) cancel(timer); timer = null; if (node) node.remove(); node = null; }
    function arm() { if (timer) cancel(timer); timer = schedule(() => { if (!node?.contains(doc.activeElement)) dismiss(); }, 8000); }
    function show() {
      if (used) return false;
      used = true;
      try { if (options.storage.getItem(key)) return false; options.storage.setItem(key, '1'); } catch (_) { /* In-memory guard remains active. */ }
      node = doc.createElement('aside'); node.className = 'premium-playback-hint';
      node.setAttribute('aria-label', options.english ? 'YouTube Premium information' : 'YouTube Premiumのご案内');
      const copy = doc.createElement('span');
      copy.textContent = options.english ? 'YouTube Premium offers ad-free playback.' : 'YouTube Premiumなら広告なしで再生できます。';
      const small = doc.createElement('small');
      small.textContent = options.english ? 'Requires your Premium sign-in and compatible browser/cookie settings. ' : '加入アカウントへのログイン・ブラウザ設定によります。';
      const link = doc.createElement('a'); link.textContent = options.english ? 'Details' : '詳細';
      link.href = 'https://support.google.com/youtube/answer/7437519?hl=' + (options.english ? 'en' : 'ja'); link.target = '_blank'; link.rel = 'noopener noreferrer';
      small.append(link); copy.append(small);
      const close = doc.createElement('button'); close.type = 'button'; close.textContent = '×';
      close.setAttribute('aria-label', options.english ? 'Dismiss Premium information' : 'Premiumの案内を閉じる');
      close.addEventListener('click', dismiss); node.append(copy, close);
      node.addEventListener('focusin', () => { if (timer) cancel(timer); });
      node.addEventListener('focusout', arm);
      host.append(node); arm(); return true;
    }
    return { show, dismiss };
  }
  root.PremiumPlaybackHint = { create };
  if (typeof module !== 'undefined') module.exports = { create };
})(typeof window !== 'undefined' ? window : globalThis);

// Only an intentional player action triggers the hint; initial cueing is silent.
(() => {
  const panel = document.getElementById('pc-player');
  if (!panel) return;
  const hint = PremiumPlaybackHint.create({host: panel, key: 'premiumcuts-premium-hint-v1', storage: {
    getItem: key => sessionStorage.getItem(key), setItem: (key, value) => sessionStorage.setItem(key, value)
  }});
  let pending = false;
  document.addEventListener('click', event => {
    const control = event.target.closest('[data-play-id],[data-play-all],[data-play-volume],[data-reference-video],[data-queue-id],#pc-toggle,#pc-fold,#pc-close-full');
    if (!control) return;
    if (control.id === 'pc-close-full') { if (pending) { pending = false; hint.show(); } return; }
    if (control.id === 'pc-fold' && panel.dataset.expanded !== 'true') return;
    if (panel.classList.contains('pc-fullscreen')) { pending = true; return; }
    hint.show();
  });
})();
