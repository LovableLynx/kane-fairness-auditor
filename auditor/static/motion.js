// Fairness Auditor: small, dependency-free interaction layer.
(() => {
  window.__motionReady = true;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, el = document) => el.querySelector(s);
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---- mobile nav
  const toggle = $(".nav-toggle"), links = $("#nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => toggle.setAttribute("aria-expanded", String(links.classList.toggle("open"))));
    links.addEventListener("click", (e) => { if (e.target.closest("a")) { links.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); } });
  }

  // ---- reveal-on-scroll (stepped), stamps, meters, strips
  const watch = document.querySelectorAll(".reveal, .stamp[data-animate], .meter[data-animate], .strips");
  if (reduce || !("IntersectionObserver" in window)) watch.forEach((n) => n.classList.add("in"));
  else {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -8% 0px" });
    watch.forEach((n) => io.observe(n));
  }

  // ---- count-up numbers
  const count = (n) => {
    const end = parseFloat(n.dataset.count), dec = parseInt(n.dataset.decimals || "0", 10);
    if (reduce || !isFinite(end)) { n.textContent = isFinite(end) ? end.toFixed(dec) : n.textContent; return; }
    const t0 = performance.now(), dur = 900;
    const tick = (t) => { const p = Math.min(1, (t - t0) / dur); n.textContent = (end * (1 - Math.pow(1 - p, 3))).toFixed(dec); if (p < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  };
  const counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window) {
    const io2 = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { count(e.target); io2.unobserve(e.target); } }));
    counters.forEach((n) => io2.observe(n));
  } else counters.forEach(count);

  // ---- pipeline: light each step in turn, forever (static when reduced motion)
  const pipes = document.querySelectorAll("#pipeline .pipe");
  if (pipes.length && !reduce) {
    let k = 0;
    setInterval(() => { pipes.forEach((p, i) => p.classList.toggle("lit", i === k % pipes.length)); k++; }, 1100);
  }

  // ---- hero replay: types each twin's name, both tools re-score
  const demo = $("#twin-demo");
  if (demo) {
    const twins = JSON.parse(demo.dataset.twins || "[]");
    const nameEl = $(".twin-name .txt", demo);
    const rows = { biased: $('[data-tool="biased"]', demo), fair: $('[data-tool="fair"]', demo) };
    let i = 0;
    const paint = (t) => ["biased", "fair"].forEach((k) => {
      const row = rows[k], s = t[k]; if (!row || !s) return;
      $(".score", row).textContent = s.score.toFixed(3);
      const b = $(".badge", row); b.textContent = s.selected ? "SHORTLIST" : "REJECT"; b.className = "badge " + (s.selected ? "ok" : "no");
      if (!reduce) { row.classList.remove("flash"); void row.offsetWidth; row.classList.add("flash"); }
    });
    const type = (name, done) => {
      if (reduce) { nameEl.textContent = name; done(); return; }
      let n = 0; nameEl.textContent = "";
      const step = () => { nameEl.textContent = name.slice(0, ++n); n < name.length ? setTimeout(step, 45) : done(); };
      step();
    };
    const next = () => { const t = twins[i++ % twins.length]; if (t) type(t.name, () => paint(t)); };
    if (twins.length) { next(); if (!reduce) setInterval(next, 2800); }
  }

  // ---- Twin Lab
  const lab = $("#twin-lab");
  if (lab) {
    const data = JSON.parse(lab.dataset.lab || "null");
    if (data && data.candidates.length) {
      let ci = data.start || 0, vi = 0, timer = null;
      const cvEl = $("#lab-cv"), candEl = $("#lab-cand"), namesEl = $("#lab-names"), toolsEl = $("#lab-tools"), fileEl = $("#lab-file");
      const groupLabel = (v) => `${v.gender === "female" ? "F" : "M"} · GROUP ${v.group}${v.slot ? " · PLACEBO" : ""}`;

      // build tool rows once
      const rows = {};
      data.tools.forEach((t) => {
        const r = el("div", "tool-row");
        r.innerHTML = `<div class="tname">${esc(t.name)}<small>${esc(t.role)}</small></div>
          <div class="bar" role="img"><i></i><span class="cut" style="left:${(t.cutoff / t.max) * 100}%"></span></div>
          <div class="val">0.000</div><span class="badge">—</span><div class="swing"></div>`;
        toolsEl.appendChild(r); rows[t.key] = r;
      });

      const renderCand = () => {
        const c = data.candidates[ci];
        candEl.textContent = c.id.toUpperCase() + ` · ${ci + 1}/${data.candidates.length}`;
        namesEl.innerHTML = "";
        c.variants.forEach((v, j) => {
          const b = el("button", "name-chip" + (v.slot ? " ph" : ""));
          b.type = "button"; b.setAttribute("aria-pressed", "false");
          b.innerHTML = `${esc(v.name)}<small>${groupLabel(v)}</small>`;
          b.addEventListener("click", () => { stop(); select(j); });
          namesEl.appendChild(b);
        });
        // swing per tool across this candidate's names
        data.tools.forEach((t) => {
          const s = c.variants.map((v) => v.tools[t.key].score);
          const sw = Math.max(...s) - Math.min(...s);
          const flips = new Set(c.variants.map((v) => v.tools[t.key].selected)).size > 1;
          const sEl = $(".swing", rows[t.key]);
          sEl.className = "swing" + (sw >= 0.05 ? " big" : "");
          sEl.innerHTML = `swing <b>${sw.toFixed(3)}</b>${flips ? " · decision flips" : " · decision stable"}`;
        });
        select(Math.min(vi, c.variants.length - 1));
      };

      const select = (j) => {
        const c = data.candidates[ci], v = c.variants[j]; vi = j;
        [...namesEl.children].forEach((b, k) => b.setAttribute("aria-pressed", String(k === j)));
        const cv = v.cv || "";
        const first = cv.split("\n")[0];
        cvEl.innerHTML = cv ? `<mark>${esc(first)}</mark>` + esc(cv.slice(first.length)) : esc(v.name);
        fileEl.textContent = v.name.toUpperCase().replace(/[^A-Z]+/g, "_") + ".TXT";
        data.tools.forEach((t) => {
          const s = v.tools[t.key], r = rows[t.key];
          const bar = $(".bar", r); bar.className = "bar " + (s.selected ? "ok" : "no");
          bar.setAttribute("aria-label", `${t.name} score ${s.score.toFixed(3)}, ${s.selected ? "shortlisted" : "rejected"}`);
          $(".bar > i", r).style.width = Math.min(100, (s.score / t.max) * 100) + "%";
          $(".val", r).textContent = s.score.toFixed(3);
          const b = $(".badge", r); b.textContent = s.selected ? "SHORTLIST" : "REJECT"; b.className = "badge " + (s.selected ? "ok" : "no");
        });
      };

      const play = $("#lab-play");
      const stop = () => { if (timer) { clearInterval(timer); timer = null; play.setAttribute("aria-pressed", "false"); play.textContent = "▶ Auto-swap"; } };
      play.addEventListener("click", () => {
        if (timer) return stop();
        play.setAttribute("aria-pressed", "true"); play.textContent = "❚❚ Pause";
        timer = setInterval(() => select((vi + 1) % data.candidates[ci].variants.length), reduce ? 2400 : 1300);
      });
      $("#lab-prev").addEventListener("click", () => { ci = (ci - 1 + data.candidates.length) % data.candidates.length; renderCand(); });
      $("#lab-next").addEventListener("click", () => { ci = (ci + 1) % data.candidates.length; renderCand(); });
      renderCand();
    }
  }

  // ---- terminal: print lines one by one when scrolled into view
  const term = $("#term");
  if (term && !reduce && "IntersectionObserver" in window) {
    const lines = [...term.querySelectorAll(".tl")];
    term.classList.add("typing");
    const io3 = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      io3.disconnect();
      let n = 0;
      const step = () => {
        if (n >= lines.length) return;
        const l = lines[n++];
        l.classList.add("shown");
        const pause = l.classList.contains("cmd") ? 520 : l.classList.contains("verdict") ? 700 : 170;
        setTimeout(step, pause);
      };
      step();
    }), { threshold: 0.35 });
    io3.observe(term);
  }

  // ---- copy buttons
  document.querySelectorAll("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(btn.dataset.copy); const o = btn.textContent; btn.textContent = "Copied ✓"; setTimeout(() => (btn.textContent = o), 1400); } catch (_) { /* clipboard blocked */ }
  }));
})();
