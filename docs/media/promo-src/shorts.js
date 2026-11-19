// Shared timeline for the short post videos. Deterministic: render(t) draws frame t (seconds).
// Scenes: window.S = [[id, start, end], ...]. Inside a scene, attributes drive the animation:
//   data-at="t"                fade/slide in at t
//   data-type="t" [data-cps]   type the element's text from t
//   data-count="v" data-at     count up to v (data-dec decimals, data-pre / data-suf)
//   data-stamp="t"             stamp in at t
//   data-w="pct" data-at       bar grows to pct% from t
//   data-strike="t"            line through at t
// window.extra(t) runs last for anything custom.
(function () {
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const ease = x => 1 - Math.pow(1 - clamp(x), 3);
  const $$ = s => [...document.querySelectorAll(s)];
  window.clamp = clamp; window.ease = ease;
  $$('[data-type]').forEach(e => { e.dataset.full = e.textContent; e.textContent = ''; });
  window.render = function (t) {
    const last = S[S.length - 1][0];
    for (const [id, a, b] of S) {
      const el = document.getElementById(id);
      const fin = ease((t - a) / .3), fout = id === last ? 1 : 1 - ease((t - (b - .3)) / .3);
      el.style.opacity = (t >= a && t < b + .01) ? Math.min(fin, fout) : 0;
    }
    $$('[data-at]').forEach(e => {
      if (e.hasAttribute('data-count') || e.hasAttribute('data-w')) return;
      const a = ease((t - +e.dataset.at) / .45);
      e.style.opacity = a; e.style.transform = `translateY(${(1 - a) * 22}px)`;
    });
    $$('[data-type]').forEach(e => {
      const n = Math.max(0, Math.floor((t - +e.dataset.type) * (+e.dataset.cps || 38)));
      e.textContent = e.dataset.full.slice(0, n);
    });
    $$('[data-count]').forEach(e => {
      const p = ease((t - +e.dataset.at) / (+e.dataset.dur || 1.2));
      const from = +(e.dataset.from || 0);
      e.textContent = (e.dataset.pre || '') + (from + (+e.dataset.count - from) * p).toFixed(+e.dataset.dec || 0) + (e.dataset.suf || '');
    });
    $$('[data-stamp]').forEach(e => {
      const s = ease((t - +e.dataset.stamp) / .3);
      e.style.opacity = s; e.style.transform = `rotate(-4deg) scale(${2 - s})`;
    });
    $$('[data-w]').forEach(e => { e.style.width = (+e.dataset.w * ease((t - +e.dataset.at) / 1.0)) + '%'; });
    $$('[data-strike]').forEach(e => { e.style.width = (ease((t - +e.dataset.strike) / .4) * 100) + '%'; });
    if (window.extra) window.extra(t);
  };
})();
