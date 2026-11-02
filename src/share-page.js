// Only builder-generated public title/canonical URL. Never read location, player, filters or storage.
(function () {
'use strict';
function mountSharePanel(root, { nav = navigator, lifecycle = window } = {}) {
  const page = { title: root.dataset.shareTitle, url: root.dataset.shareUrl };
  try {
    const url = new URL(page.url);
    if (!page.title || url.protocol !== 'https:' || url.username || url.password || url.search || url.hash) return null;
  } catch (_) { return null; }
  const share = root.querySelector('[data-share-native]');
  const copy = root.querySelector('[data-share-copy]');
  const status = root.querySelector('[data-share-status]');
  const manual = root.querySelector('[data-share-manual]');
  const input = root.querySelector('[data-share-url]');
  const actions = root.querySelector('[data-share-actions]');
  if (![share, copy, status, manual, input, actions].every(Boolean)) return null;
  const buttons = [share, copy];
  let busy = false, operation = 0;
  input.value = page.url;
  for (const button of buttons) button.disabled = false;
  function setBusy(value) {
    busy = value;
    actions.setAttribute('aria-busy', String(value));
    for (const button of buttons) button.setAttribute('aria-disabled', String(value));
  }
  function fallback(message) {
    status.textContent = message;
    manual.open = true;
    input.focus({ preventScroll: true });
    input.select();
  }
  async function run(kind) {
    if (busy) return;
    const id = ++operation;
    manual.open = false;
    setBusy(true);
    status.textContent = kind === 'share' ? '共有メニューを開いています…' : 'URLをコピーしています…';
    try {
      if (kind === 'share') {
        if (typeof nav.share !== 'function') {
          fallback('この端末では共有メニューを利用できません。URLをコピーするか、下のURLを選択してください。');
          return;
        }
        await nav.share({ title: page.title, url: page.url });
        if (id === operation) status.textContent = '共有操作が完了しました。';
      } else {
        if (typeof nav.clipboard?.writeText !== 'function') {
          fallback('自動コピーを利用できません。下のURLを選択してコピーしてください。');
          return;
        }
        await nav.clipboard.writeText(page.url);
        if (id === operation) status.textContent = 'URLをコピーしました。';
      }
    } catch (error) {
      if (id !== operation) return;
      if (kind === 'share' && error?.name === 'AbortError') {
        status.textContent = '共有をキャンセルしました。';
      } else {
        fallback(kind === 'share'
          ? '共有メニューを開けませんでした。URLをコピーするか、下のURLを選択してください。'
          : 'コピーできませんでした。下のURLを選択してコピーしてください。');
      }
    } finally {
      if (id === operation) setBusy(false);
    }
  }
  const onShare = () => run('share'), onCopy = () => run('copy');
  const reset = () => { operation++; setBusy(false); manual.open = false; status.textContent = ''; };
  share.addEventListener('click', onShare);
  copy.addEventListener('click', onCopy);
  // A restored page must not retain a stale busy flag or announce an old operation.
  lifecycle.addEventListener('pagehide', reset);
  return { reset, destroy() { reset(); share.removeEventListener('click', onShare); copy.removeEventListener('click', onCopy); lifecycle.removeEventListener('pagehide', reset); } };
}
// Keep the footer payload in step with successful persistent-player navigation.
// Read only the destination's builder-generated sharing markup, never browser state.
function createShareManager({ doc = document, nav = navigator, lifecycle = window } = {}) {
  let mounted = [];
  function attach(root) {
    const api = mountSharePanel(root, { nav, lifecycle });
    if (api) mounted.push({ root, api });
    return api;
  }
  for (const root of doc.querySelectorAll('[data-page-share]')) attach(root);
  function clear() {
    for (const { root, api } of mounted) { api.destroy(); root.remove(); }
    mounted = [];
    // Remove any malformed old panel as well, instead of exposing a stale URL.
    for (const root of doc.querySelectorAll('[data-page-share]')) root.remove();
  }
  return {
    syncFromDocument(source) {
      const next = source.querySelector('[data-page-share]');
      clear();
      const footer = doc.querySelector('footer');
      if (!next || !footer) return;
      const root = next.cloneNode(true);
      if (attach(root)) footer.append(root);
    },
    destroy: clear
  };
}
if (typeof document !== 'undefined') {
  window.PremiumShare = createShareManager();
}

if (typeof module === 'object' && module.exports) module.exports = { mountSharePanel, createShareManager };
})();
