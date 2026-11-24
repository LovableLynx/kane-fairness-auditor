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

  // Exhibit B: drive a real hiring tool inside the frame, picked by the visitor (one at a time). Pauses when scrolled
  // away or the tab is hidden and carries on from the same moment; never touches the browser history or the tools' lists.
  const shell = document.getElementById("d-shell");
  if (shell) {
    const stage = document.getElementById("d-stage"), cam = document.getElementById("d-cam"), frame = document.getElementById("d-frame");
    const cur = document.getElementById("d-cursor"), ring = document.getElementById("d-ring"), cap = document.getElementById("d-cap"), url = document.getElementById("d-url");
    const tabs = [...document.querySelectorAll(".d-tab")];
    let visible = false, started = false, scale = 1, FW = 1280, FH = 760, pos = [0, 0], run = 0, tool = "talentscreen";
    const STOP = {};
    const host = location.host;
    let camState = [1, 0, 0];
    const camTo = (z, fx, fy, instant) => {
      camState = [z, fx, fy];
      const s = scale * z, w = stage.clientWidth, h = stage.clientHeight;
      const tx = z === 1 ? 0 : Math.min(0, Math.max(w - FW * s, w / 2 - fx * s));
      const ty = z === 1 ? 0 : Math.min(0, Math.max(h - FH * s, h / 2 - fy * s));
      if (instant) cam.style.transition = "none";
      cam.style.transform = `translate(${tx}px, ${ty}px) scale(${s})`;
      if (instant) { void cam.offsetWidth; cam.style.transition = ""; }
    };
    const layout = () => {
      const w = stage.clientWidth;
      FW = w < 700 ? 420 : 1280; FH = w < 700 ? 720 : 760; scale = w / FW;
      frame.style.width = FW + "px"; frame.style.height = FH + "px";
      stage.style.height = Math.round(FH * scale) + "px";
      camTo(...camState, true);
    };
    const wait = (ms, my) => new Promise((res, rej) => {
      let left = ms, last = performance.now();
      const tick = () => {
        if (my !== run) return rej(STOP);
        const now = performance.now();
        if (visible && !document.hidden) left -= now - last;
        last = now;
        if (left <= 0) res(); else setTimeout(tick, 100);
      };
      tick();
    });
    const doc = () => frame.contentDocument;
    const load = (path, my) => new Promise((res, rej) => {
      if (my !== run) return rej(STOP);
      frame.onload = () => { frame.onload = null; my === run ? res() : rej(STOP); };
      if (frame.contentWindow && frame.contentWindow.location.href !== "about:blank") frame.contentWindow.location.replace(path);
      else frame.src = path;
      url.textContent = host + path;
    });
    const say = (t) => { cap.textContent = t; };
    const moveTo = async (sel, my) => {
      const el = doc() && doc().querySelector(sel);
      if (!el) return null;
      const win = frame.contentWindow, r0 = el.getBoundingClientRect();
      win.scrollTo(0, Math.max(0, win.scrollY + r0.top - FH * 0.45));
      const r = el.getBoundingClientRect();
      pos = [r.left + r.width / 2, r.top + r.height / 2];
      cur.style.transform = `translate(${pos[0] - 4}px, ${pos[1] - 3}px)`;
      await wait(1000, my);
      return el;
    };
    const tap = async (sel, my, press = true) => {
      const el = await moveTo(sel, my);
      if (!el) return null;
      ring.style.left = pos[0] + "px"; ring.style.top = pos[1] + "px";
      ring.classList.remove("go"); void ring.offsetWidth; ring.classList.add("go");
      await wait(250, my);
      if (press) el.click();
      return el;
    };
    const submit = async (sel, my) => {     // press the button, but post it ourselves: no history entry, marked as the demo
      const btn = await tap(sel, my, false);
      const form = btn && btn.closest("form");
      if (!form) return;
      if (!form.querySelector("input[name=demo]")) {
        const h = doc().createElement("input"); h.type = "hidden"; h.name = "demo"; h.value = "1"; form.appendChild(h);
      }
      const resp = await fetch(form.action || frame.contentWindow.location.href, { method: "POST", body: new FormData(form), credentials: "same-origin" });
      await load(new URL(resp.url).pathname + new URL(resp.url).search, my);
    };
    const text = (sel) => { const e = doc() && doc().querySelector(sel); return e ? e.textContent.replace(/\s+/g, " ").trim() : ""; };
    const focusOn = async (sel, z, my) => {
      const e = doc() && doc().querySelector(sel); if (!e) return;
      const r = e.getBoundingClientRect(); camTo(FW < 700 ? z * .7 : z, r.left + r.width / 2, r.top + r.height / 2);
      await moveTo(sel, my);
    };
    const TOOLS = {
      talentscreen: { name: "TalentScreen", intro: "A recruiter opens TalentScreen, an AI that screens CVs.",
        async apply(k, my) {
          await load("/talentscreen/?role=data-analyst", my); camTo(1, 0, 0);
          await wait(1200, my); await tap(`[data-sample='${k}']`, my); await wait(900, my);
          await submit("button[type=submit]", my); await wait(900, my);
          await focusOn("#match-score", 2.2, my);
          const d = text("#decision").replace(/^Decision:\s*/i, "");
          return [text("#match-score"), d.charAt(0) + d.slice(1).toLowerCase()];
        } },
      hirelens: { name: "HireLens", intro: "A recruiter adds an applicant in HireLens.",
        async apply(k, my) {
          await load("/hirelens/applicants/new?role=data-analyst", my); camTo(1, 0, 0);
          await wait(1200, my); await tap(`[data-sample='${k}']`, my); await wait(900, my);
          await submit("#eval-btn", my); await wait(900, my);
          await focusOn("#fit", 2.0, my);
          return [text("#fit"), text("#recommendation")];
        } },
      quickmatch: { name: "QuickMatch", intro: "A recruiter starts a match in QuickMatch, built on an open-source AI model.",
        async apply(k, my) {
          await load("/quickmatch/", my); camTo(1, 0, 0);
          await wait(1200, my); await submit("button[type=submit]", my);
          await wait(800, my); await tap(`[data-sample='${k}']`, my); await wait(900, my);
          await submit("button[type=submit]", my); await wait(700, my);
          await submit("button[type=submit]", my); await wait(1200, my);
          await focusOn("#similarity", 2.0, my);
          return [text("#similarity"), text("#verdict").replace(/^Verdict:\s*/i, "")];
        } },
    };
    const play = async (my) => {
      const t = TOOLS[tool];
      for (;;) {
        say(t.intro);
        const [s1, d1] = await t.apply("0", my);
        say(`Brendan Kelly: ${s1}. ${d1}.`);
        await wait(3000, my);
        say(t.intro);
        const [s2, d2] = await t.apply("1", my);
        say(s1 === s2 && d1 === d2 ? `Ebony Jones, the exact same CV: ${s2}. ${d2}. Same CV, same answer.`
                                   : `Ebony Jones, the exact same CV: ${s2}. ${d2}. Only the name changed.`);
        await wait(4200, my);
        await load(`/results/${tool}`, my); camTo(1, 0, 0);
        await wait(900, my);
        const st = text(".stamp");
        say(`Kane CLI tested ${t.name} in a real browser. Verdict: ${st || "see the evidence"}.`);
        await focusOn(".stamp", 1.8, my);
        await wait(4200, my);
      }
    };
    const start = () => {
      run += 1; const my = run;
      play(my).catch((e) => { if (e !== STOP) { say("The live demo paused. Pick a tool to start it again."); } });
    };
    tabs.forEach((b) => b.addEventListener("click", () => {
      tool = b.dataset.tool;
      tabs.forEach((x) => { const on = x === b; x.classList.toggle("on", on); x.setAttribute("aria-selected", String(on)); });
      if (started && !reduce) start();
      else if (reduce) { load(`/${tool}/`, ++run).catch(() => {}); say(`Live ${TOOLS[tool].name}. Animation is off because your device prefers reduced motion.`); }
    }));
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      visible = e.isIntersecting;
      if (visible && !started) {
        started = true; layout();
        if (!reduce) start(); else { load("/talentscreen/", ++run).catch(() => {}); say("Live TalentScreen. Animation is off because your device prefers reduced motion."); }
      }
    }), { threshold: 0.3 });
    io.observe(shell);
    window.addEventListener("resize", () => { if (started) layout(); });
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
