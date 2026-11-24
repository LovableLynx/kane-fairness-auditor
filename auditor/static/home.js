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

  // Exhibit B: drive the real TalentScreen inside the frame. Pauses when scrolled away or the tab is hidden,
  // and carries on from where it stopped when it comes back into view.
  const shell = document.getElementById("d-shell");
  if (shell) {
    const stage = document.getElementById("d-stage"), cam = document.getElementById("d-cam"), frame = document.getElementById("d-frame");
    const cur = document.getElementById("d-cursor"), ring = document.getElementById("d-ring"), cap = document.getElementById("d-cap"), url = document.getElementById("d-url");
    let visible = false, started = false, scale = 1, FW = 1280, FH = 760, pos = [FW * .6, FH * .5];
    const host = location.host;
    const layout = () => {
      const w = stage.clientWidth;
      FW = w < 700 ? 420 : 1280; FH = w < 700 ? 720 : 760;
      scale = w / FW;
      frame.style.width = FW + "px"; frame.style.height = FH + "px";
      stage.style.height = Math.round(FH * scale) + "px";
      camTo(1, 0, 0, true);
    };
    let camState = [1, 0, 0];
    const camTo = (z, fx, fy, instant) => {      // zoom z around point (fx, fy) in frame pixels
      camState = [z, fx, fy];
      const s = scale * z, tx = z === 1 ? 0 : Math.min(0, Math.max(stage.clientWidth - FW * s, stage.clientWidth / 2 - fx * s));
      const ty = z === 1 ? 0 : Math.min(0, Math.max(stage.clientHeight - FH * s, stage.clientHeight / 2 - fy * s));
      if (instant) cam.style.transition = "none";
      cam.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`;
      if (instant) { void cam.offsetWidth; cam.style.transition = ""; }
    };
    const wait = (ms) => new Promise((res) => {
      let left = ms, last = performance.now();
      const tick = () => {
        const now = performance.now();
        if (visible && !document.hidden) left -= now - last;
        last = now;
        if (left <= 0) res(); else setTimeout(tick, 100);
      };
      tick();
    });
    const doc = () => frame.contentDocument;
    const load = (path) => new Promise((res) => {
      frame.onload = () => { frame.onload = null; res(); };
      frame.src = path; url.textContent = host + path;
    });
    const say = (t) => { cap.textContent = t; };
    const moveTo = async (sel) => {
      const el = doc() && doc().querySelector(sel);
      if (!el) return null;
      const win = frame.contentWindow, r0 = el.getBoundingClientRect();   // scroll only inside the frame, never the page
      win.scrollTo(0, Math.max(0, win.scrollY + r0.top - FH * 0.45));
      const r = el.getBoundingClientRect();
      pos = [r.left + r.width / 2, r.top + r.height / 2];
      cur.style.transform = `translate(${pos[0] - 4}px, ${pos[1] - 3}px)`;
      await wait(1000);
      return el;
    };
    const click = async (sel) => {
      const el = await moveTo(sel);
      if (!el) return;
      ring.style.left = pos[0] + "px"; ring.style.top = pos[1] + "px";
      ring.classList.remove("go"); void ring.offsetWidth; ring.classList.add("go");
      await wait(250);
      el.click();
    };
    const apply = async (sample, who) => {
      await load("/talentscreen/?role=data-analyst"); camTo(1, 0, 0);
      say("A recruiter opens TalentScreen, an AI that screens CVs.");
      await wait(1400);
      await click(`[data-sample='${sample}']`);
      say(`${who}'s CV goes in.`);
      await wait(1100);
      const submitted = new Promise((res) => { frame.onload = () => { frame.onload = null; res(); }; });
      await click("button[type=submit]");
      await submitted;
      await wait(900);
      const sc = doc().querySelector("#match-score"), dec = doc().querySelector("#decision");
      const r = sc.getBoundingClientRect();
      camTo(FW < 700 ? 1.5 : 2.2, r.left + 40, r.top - 60);
      await moveTo("#decision");
      return [sc.textContent.trim(), dec.textContent.replace("Decision:", "").trim()];
    };
    const loop = async () => {
      for (;;) {
        const [s1, d1] = await apply("0", "Brendan Kelly");
        say(`Brendan Kelly: ${s1}. ${d1.charAt(0) + d1.slice(1).toLowerCase()}.`);
        await wait(3200);
        const [s2, d2] = await apply("1", "Ebony Jones");
        say(`Ebony Jones, the exact same CV: ${s2}. ${d2.charAt(0) + d2.slice(1).toLowerCase()}. Only the name changed.`);
        await wait(4200);
        await load("/results/talentscreen"); camTo(1, 0, 0);
        say("Kane CLI ran this test in a real browser and caught it: FAIL, biased.");
        await wait(1200);
        const st = doc().querySelector(".stamp"); if (st) { const r = st.getBoundingClientRect(); camTo(FW < 700 ? 1.6 : 1.8, r.left + 120, r.top + 40); }
        await moveTo(".stamp");
        await wait(4200);
      }
    };
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      visible = e.isIntersecting;
      if (visible && !started) { started = true; layout(); if (!reduce) loop(); else { load("/talentscreen/?role=data-analyst"); say("Live TalentScreen. Animation is off because your device prefers reduced motion."); } }
    }), { threshold: 0.3 });
    io.observe(shell);
    window.addEventListener("resize", () => { if (started) { layout(); camTo(...camState, true); } });
  }

  // the narrated version, on demand, with sound
  const dlg = document.getElementById("d-dialog");
  if (dlg) {
    const v = document.getElementById("d-video");
    document.getElementById("d-watch").addEventListener("click", () => { dlg.showModal(); v.currentTime = 0; v.play().catch(() => {}); });
    const close = () => { v.pause(); dlg.close(); };
    document.getElementById("d-close").addEventListener("click", close);
    dlg.addEventListener("click", (e) => { if (e.target === dlg) close(); });
    dlg.addEventListener("close", () => v.pause());
  }
})();
