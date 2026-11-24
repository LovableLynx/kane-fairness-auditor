// Homepage: scroll reveals and number count-ups (one observer, transform/opacity only), the live test (swap the name, see the score Kane read) and the explainer video's sound button.
(() => {
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const rx = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;
  window.__rvReady = true;
  const count = (el) => {
    const to = +el.dataset.count, t0 = performance.now(), dur = 1100;
    if (reduce || !to) { el.textContent = String(to); return; }
    const step = (now) => { const p = Math.min(1, (now - t0) / dur); el.textContent = String(Math.round(to * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      e.target.querySelectorAll("[data-count]").forEach(count);
      if (e.target.dataset.count) count(e.target);
      io.unobserve(e.target);
    }), { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    document.querySelectorAll(".rv").forEach((el) => io.observe(el));
  } else {
    root.classList.remove("js-rv");
  }

  const test = document.getElementById("h-test");
  if (test) {
    const twins = JSON.parse(test.dataset.twins);
    const cv = document.getElementById("h-cv-text"), who = document.getElementById("h-who");
    const score = document.getElementById("h-score"), dec = document.getElementById("h-decision");
    const show = (i) => {
      const t = twins[i], first = t.name.split(" ")[0];
      const words = [t.name, first, "He", "She", "he", "she", "His", "Her", "his", "her", "him", "Him"];
      const re = new RegExp("\\b(" + words.map(rx).join("|") + ")\\b|[\\w.+-]+@[\\w.-]+", "g");
      cv.innerHTML = esc(t.cv).replace(re, (m) => `<mark>${m}</mark>`);
      who.textContent = t.name;
      score.textContent = t.score.toFixed(3);
      dec.textContent = t.selected ? "Shortlisted" : "Rejected";
      dec.className = "m-dec " + (t.selected ? "ok" : "no");
      test.querySelectorAll(".h-name").forEach((b) => {
        const on = +b.dataset.i === i;
        b.classList.toggle("on", on); b.setAttribute("aria-pressed", String(on));
      });
    };
    test.addEventListener("click", (e) => { const b = e.target.closest(".h-name"); if (b) show(+b.dataset.i); });
    show(0);
  }

  // Explainer video: it plays silently on its own; the pulsing button restarts it from the beginning with sound.
  const video = document.getElementById("h-explainer"), btn = document.getElementById("h-sound");
  if (video && btn) {
    const ICON_OFF = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="m23 9-6 6M17 9l6 6"/></svg>';
    const ICON_ON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>';
    const paint = () => {
      const muted = video.muted;
      btn.innerHTML = (muted ? ICON_OFF : ICON_ON) + `<span>${muted ? "Tap for sound" : "Sound on"}</span>`;
      btn.setAttribute("aria-label", muted ? "Play the video with sound from the start" : "Mute the video");
      btn.classList.toggle("waiting", muted && !btn.dataset.used);
    };
    btn.addEventListener("click", () => {
      if (video.muted) {
        btn.dataset.used = "1";
        video.muted = false; video.loop = false; video.currentTime = 0; video.controls = true;
        video.play().catch(() => {});
      } else {
        video.muted = true;
      }
      paint();
    });
    video.addEventListener("volumechange", paint);
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { video.removeAttribute("autoplay"); video.pause(); video.controls = true; }
    else {
      // Some browsers wait for a nudge before autoplaying, even muted: start it silently once it can play,
      // and keep it playing whenever it is on screen (until the visitor turns the sound on).
      video.muted = true;
      const start = () => { if (video.muted && video.paused) video.play().catch(() => {}); };
      video.addEventListener("canplay", start);
      if ("IntersectionObserver" in window) {
        new IntersectionObserver((es) => es.forEach((e) => {
          if (!video.muted) return;
          if (e.isIntersecting) start(); else video.pause();
        }), { threshold: 0.25 }).observe(video);
      }
      start();
    }
    paint();
  }
})();
