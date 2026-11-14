// Fairness Auditor: small, dependency-free interaction layer.
(() => {
  window.__motionReady = true;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Mobile nav toggle
  const toggle = document.querySelector(".nav-toggle");
  const links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Stepped reveal + stamps + meters when they scroll into view
  const targets = document.querySelectorAll(".reveal, .stamp[data-animate], .meter[data-animate]");
  if (reduce || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    targets.forEach((el) => io.observe(el));
  }

  // Count-up numbers: <span data-count="0.845" data-decimals="3">
  const counters = document.querySelectorAll("[data-count]");
  const run = (el) => {
    const end = parseFloat(el.dataset.count), dec = parseInt(el.dataset.decimals || "0", 10);
    const prefix = el.dataset.prefix || "", suffix = el.dataset.suffix || "";
    if (reduce) { el.textContent = prefix + end.toFixed(dec) + suffix; return; }
    const t0 = performance.now(), dur = 900;
    const tick = (t) => {
      const p = Math.min(1, (t - t0) / dur), v = end * (1 - Math.pow(1 - p, 3));
      el.textContent = prefix + v.toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if ("IntersectionObserver" in window) {
    const io2 = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (e.isIntersecting) { run(e.target); io2.unobserve(e.target); }
    }));
    counters.forEach((el) => io2.observe(el));
  } else counters.forEach(run);

  // Hero twin demo: one CV, names swap, two tools score it
  const demo = document.getElementById("twin-demo");
  if (demo) {
    const twins = JSON.parse(demo.dataset.twins);
    const nameEl = demo.querySelector(".twin-name .txt");
    const rows = { biased: demo.querySelector('[data-tool="biased"]'), fair: demo.querySelector('[data-tool="fair"]') };
    let i = 0;
    const paint = (t) => {
      for (const k of ["biased", "fair"]) {
        const row = rows[k], s = t[k];
        row.querySelector(".score").textContent = s.score.toFixed(3);
        const b = row.querySelector(".badge");
        b.textContent = s.selected ? "SHORTLIST" : "REJECT";
        b.className = "badge " + (s.selected ? "ok" : "no");
        if (!reduce) { row.classList.remove("flash"); void row.offsetWidth; row.classList.add("flash"); }
      }
    };
    const type = (name, done) => {
      if (reduce) { nameEl.textContent = name; done(); return; }
      let n = 0; nameEl.textContent = "";
      const step = () => { nameEl.textContent = name.slice(0, ++n); n < name.length ? setTimeout(step, 45) : done(); };
      step();
    };
    const next = () => {
      const t = twins[i % twins.length]; i++;
      type(t.name, () => paint(t));
    };
    next();
    if (!reduce) setInterval(next, 2600);
  }

  // Copy buttons
  document.querySelectorAll("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(btn.dataset.copy); const o = btn.textContent; btn.textContent = "Copied ✓"; setTimeout(() => (btn.textContent = o), 1400); } catch (_) { /* clipboard blocked */ }
  }));
})();
