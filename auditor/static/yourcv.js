// Twin your CV: start the check, show real progress, then replay every version with its scores.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const form = $("#yc-form");
  if (!form) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const rx = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const TOOL = {
    talentscreen: { name: "TalentScreen", role: "Known biased" },
    hirelens: { name: "HireLens", role: "Known fair" },
    quickmatch: { name: "QuickMatch", role: "Real black box" },
  };
  const WHY = { norole: "couldn't find a job title or experience", empty: "got an empty CV", unreadable: "couldn't read it", noscore: "showed no score" };
  const ui = {
    text: $("#yc-text"), file: $("#yc-file"), fileLabel: $("#yc-file-label"), go: $("#yc-go"), sample: $("#yc-sample"),
    error: $("#yc-error"), stage: $("#yc-stage"), cv: $("#yc-cv"), cvName: $("#yc-file-name"), phase: $("#yc-phase"),
    name: $("#yc-name"), tag: $("#yc-tag"), bar: $("#yc-bar"), progress: $("#yc-progress"), count: $("#yc-count"),
    tools: $("#yc-tools"), board: $("#yc-board"), skip: $("#yc-skip"), results: $("#yc-results"),
    headline: $("#yc-headline"), sampleNote: $("#yc-sample-note"), verdicts: $("#yc-verdicts"), names: $("#yc-names"),
    again: $("#yc-again"),
  };
  let busy = false, skip = false, shuffle = null, draft = "", toolsBuilt = false;
  // The last result is kept in this browser tab only (sessionStorage: never sent anywhere, gone when the tab
  // closes or on "Try another CV"), so going to another page and coming Back shows it again.
  const KEY = "yc-last";
  const remember = (job) => { try { sessionStorage.setItem(KEY, JSON.stringify(job)); } catch (_) { /* storage off: fine */ } };
  const forget = () => { try { sessionStorage.removeItem(KEY); } catch (_) { /* ignore */ } };
  const recall = () => { try { return JSON.parse(sessionStorage.getItem(KEY) || "null"); } catch (_) { return null; } };

  ui.file.addEventListener("change", () => {
    const f = ui.file.files[0];
    ui.fileLabel.textContent = f ? `📄 ${f.name}` : "Upload .pdf, .docx or .txt";
  });

  const showError = (msg) => {
    ui.error.textContent = msg; ui.error.hidden = false;
    ui.stage.hidden = true; busy = false; ui.go.disabled = ui.sample.disabled = false;
  };

  async function start(useSample) {
    if (busy) return;
    const fd = new FormData();
    if (useSample) fd.append("sample", "1");
    else if (ui.file.files[0]) fd.append("cv_file", ui.file.files[0]);
    else if (ui.text.value.trim()) fd.append("cv_text", ui.text.value);
    else { showError("Paste your CV text or upload a file first (or try the sample CV)."); ui.text.focus(); return; }
    busy = true; skip = false; ui.go.disabled = ui.sample.disabled = true; ui.error.hidden = true;
    ui.stage.hidden = false; ui.results.hidden = true; ui.skip.hidden = false;
    ui.tools.innerHTML = ""; ui.board.innerHTML = ""; ui.cv.textContent = ""; ui.bar.style.width = "0";
    ui.progress.hidden = false; ui.phase.textContent = "Writing your twins"; ui.name.textContent = "…"; ui.tag.textContent = " ";
    ui.cvName.textContent = "CV · AS YOU WROTE IT";
    draft = useSample || ui.file.files[0] ? "" : ui.text.value.trim(); toolsBuilt = false;
    ui.cv.textContent = draft || (useSample ? "Loading the sample CV…" : "Reading your file…");
    ui.stage.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    let r;
    try { r = await fetch("/api/your-cv", { method: "POST", body: fd }); }
    catch (_) { showError("Couldn't reach the server. Check your connection and try again."); return; }
    const j = await r.json().catch(() => ({}));
    if (!r.ok || !j.id) { showError(j.error || "Something went wrong. Please try again."); return; }
    poll(j.id);
  }

  async function poll(id) {
    let job;
    for (;;) {
      try { job = await (await fetch(`/api/your-cv/${id}`)).json(); }
      catch (_) { await sleep(800); continue; }
      if (job.status === "error") { stopShuffle(); showError(job.error); return; }
      if (job.twins && !shuffle) startShuffle(job.twins, job.name);
      if (job.tools && !toolsBuilt) { buildTools(job.tools); toolsBuilt = true; }
      if (job.tools && job.twins) {
        const per = job.twins.length + 1;
        job.tools.forEach((t, ti) => {
          const row = $(`.tool-row[data-key="${t.key}"]`, ui.tools), n = Math.max(0, Math.min(per, (job.done || 0) - ti * per));
          $(".badge", row).textContent = n >= per ? "SCORED ✓" : n > 0 ? `${n} / ${per}` : "WAITING";
          $(".bar > i", row).style.width = Math.round(100 * n / per) + "%";
        });
      }
      const pct = Math.round(100 * (job.done || 0) / Math.max(1, job.total || 27));
      ui.bar.style.width = pct + "%";
      if (job.tools) {
        const per = job.twins.length + 1, k = job.tools[Math.min(job.tools.length - 1, Math.floor((job.done || 0) / per))].key;
        ui.phase.textContent = job.status === "finished" ? "Done" : `Asking ${TOOL[k].name}`;
        ui.count.textContent = `${job.done} of ${job.total} versions scored`;
      }
      if (job.status === "finished") { stopShuffle(); reveal(job); return; }
      await sleep(350);
    }
  }

  // Preview while the server scores: the same swap the server makes (name, email, he/she), shown on the pasted text.
  const PRON = {
    female: { He: "She", he: "she", Himself: "Herself", himself: "herself", His: "Her", his: "her", Him: "Her", him: "her" },
    male: { She: "He", she: "he", Herself: "Himself", herself: "himself", Her: "His", her: "his" },
  };
  function startShuffle(twins, own) {
    ui.tag.textContent = "swapping only the name, email and he/she…";
    const first = (own || "").split(" ")[0];
    const paint = (t) => {
      ui.name.textContent = t.name;
      if (!draft || !own) return;
      const f = t.name.split(" ")[0], map = PRON[t.gender];
      const mail = (t.name.replace(" ", ".") + "@example.com").toLowerCase().replace(/'/g, "");
      const re = new RegExp(rx(own) + "|\\b" + rx(first) + "\\b|[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+|\\b(?:" + Object.keys(map).join("|") + ")\\b", "g");
      ui.cv.innerHTML = esc(draft).replace(re, (m) => `<mark>${esc(m === own ? t.name : m === first ? f : m.includes("@") ? mail : map[m] || m)}</mark>`);
    };
    if (reduce) { paint(twins[0]); return; }
    let i = 0;
    shuffle = setInterval(() => paint(twins[i++ % twins.length]), 160);
  }
  function stopShuffle() { if (shuffle) clearInterval(shuffle); shuffle = null; }

  // ---------- replay
  function versions(job) {
    const label = (t) => `${t.gender === "male" ? "Man" : "Woman"} · name group ${t.group}${t.slot ? " · second name" : ""}`;
    return [{ name: job.name, tag: "as you wrote it", text: job.cv.original, scores: job.original, you: true }]
      .concat(job.twins.map((t, i) => ({ ...t, tag: label(t), text: job.cv.twins[i] })));
  }

  function highlight(v) {
    const words = v.you ? [v.name] : [v.name, v.name.split(" ")[0], "He", "She", "he", "she", "his", "her", "him", "His", "Her", "Him", "himself", "herself"];
    const re = new RegExp("\\b(" + words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")\\b", "g");
    return esc(v.text).replace(re, "<mark>$1</mark>");
  }

  function buildTools(tools) {
    ui.tools.innerHTML = "";
    tools.forEach((t) => {
      const row = document.createElement("div");
      row.className = "tool-row"; row.dataset.key = t.key;
      row.innerHTML = `<div class="tname">${TOOL[t.key].name}<small>${TOOL[t.key].role}</small></div>
        <div class="bar" role="img"><i></i><span class="cut" style="left:${(t.cutoff / t.max) * 100}%"></span></div>
        <div class="val">–</div><div class="badge">…</div>`;
      ui.tools.appendChild(row);
    });
  }

  function buildBoard(job, vs) {
    const cols = vs.length;
    let html = `<div class="yc-board-row yc-board-head" style="--n:${cols}"><span></span>` +
      vs.map((v, i) => `<span title="${esc(v.name)}">${i === 0 ? "YOU" : esc(v.name.split(" ")[0])}</span>`).join("") + `</div>`;
    job.tools.forEach((t) => {
      html += `<div class="yc-board-row" style="--n:${cols}" data-key="${t.key}"><span class="yc-board-tool">${TOOL[t.key].name}</span>` +
        vs.map((v, i) => `<span class="yc-cell" data-i="${i}"></span>`).join("") + `</div>`;
    });
    ui.board.innerHTML = html;
  }

  function show(job, v, i) {
    ui.cv.innerHTML = highlight(v);
    ui.cvName.textContent = i === 0 ? "CV · AS YOU WROTE IT" : `CV · VERSION ${i} OF 8`;
    ui.name.textContent = v.name; ui.tag.textContent = v.tag;
    job.tools.forEach((t) => {
      const s = v.scores[t.key] || {}, row = $(`.tool-row[data-key="${t.key}"]`, ui.tools);
      const bar = $(".bar", row), badge = $(".badge", row);
      if (s.score == null) {
        bar.className = "bar"; $(".bar > i", row).style.width = "0";
        $(".val", row).textContent = "–"; badge.className = "badge"; badge.textContent = "UNREADABLE";
      } else {
        bar.className = "bar " + (s.selected ? "ok" : "no");
        bar.setAttribute("aria-label", `${TOOL[t.key].name}: ${s.score.toFixed(3)}, ${s.selected ? "shortlisted" : "rejected"}`);
        $(".bar > i", row).style.width = Math.min(100, (s.score / t.max) * 100) + "%";
        $(".val", row).textContent = s.score.toFixed(3);
        badge.className = "badge " + (s.selected ? "ok" : "no"); badge.textContent = s.selected ? "SHORTLIST" : "REJECT";
      }
    });
    ui.names.querySelectorAll(".name-chip").forEach((c) => c.setAttribute("aria-pressed", String(+c.dataset.i === i)));
  }

  function fillCell(job, v, i) {
    job.tools.forEach((t) => {
      const s = v.scores[t.key] || {}, cell = $(`.yc-board-row[data-key="${t.key}"] .yc-cell[data-i="${i}"]`, ui.board);
      cell.className = "yc-cell in " + (s.score == null ? "na" : s.selected ? "ok" : "no");
      cell.textContent = s.score == null ? "–" : s.score.toFixed(2);
      cell.title = `${v.name}: ${s.score == null ? "unreadable" : s.score.toFixed(3) + (s.selected ? ", shortlisted" : ", rejected")}`;
    });
  }

  async function reveal(job) {
    const vs = versions(job);
    ui.progress.hidden = true; ui.count.textContent = " ";
    buildTools(job.tools); buildBoard(job, vs);
    ui.names.innerHTML = vs.map((v, i) => `<button type="button" class="name-chip${v.slot ? " ph" : ""}" data-i="${i}" aria-pressed="false">${esc(v.name)}<small>${i === 0 ? "YOU" : esc(v.tag.replace("name group", "group").toUpperCase())}</small></button>`).join("");
    ui.names.onclick = (e) => { const b = e.target.closest(".name-chip"); if (b) show(job, vs[+b.dataset.i], +b.dataset.i); };
    for (let i = 0; i < vs.length; i++) {
      ui.phase.textContent = i === 0 ? "Your CV, as you wrote it" : `Same CV, name ${i} of 8`;
      show(job, vs[i], i); fillCell(job, vs[i], i);
      if (!skip && !reduce) await sleep(i === 0 ? 1600 : 1150);
    }
    ui.skip.hidden = true; ui.phase.textContent = "All nine versions scored";
    finish(job, vs);
  }

  function finish(job, vs, quiet) {
    remember(job);
    const S = job.summary, keys = job.tools.map((t) => t.key);
    const flips = keys.filter((k) => S[k].flip), moved = keys.filter((k) => !S[k].flip && S[k].swing > 0.05);
    ui.headline.innerHTML = flips.length
      ? `<span class="hl">${flips.length} of 3</span> AI recruiters changed their decision when only the name on your CV changed.`
      : moved.length
        ? `No decision flipped, but <span class="hl">${moved.length} of 3</span> moved your score by more than 0.05 on the name alone.`
        : keys.every((k) => S[k].swing === 0)
          ? `Good news: <span class="hl">no tool</span> reacted to the name on your CV.`
          : `No decision flipped, and <span class="hl">no score moved more than 0.05</span> on the name alone.`;
    ui.sampleNote.hidden = !job.sample;
    ui.sampleNote.innerHTML = job.sample ? "This sample is candidate 2 from the audit. Kane CLI read these same 24 twin scores in a real browser, and they match exactly. <a href=\"/results/quickmatch\">See Kane's evidence →</a>" : "";
    ui.verdicts.innerHTML = keys.map((k) => {
      const s = S[k], t = job.tools.find((x) => x.key === k);
      const twins = vs.slice(1).filter((v) => v.scores[k] && v.scores[k].score != null);
      if (!twins.length) {
        const err = (job.original[k] || {}).error;
        return card(k, "INCONCLUSIVE", "COULDN'T READ IT", `${TOOL[k].name} ${WHY[err] || "couldn't read"} your CV. Add a job title and dates (for example "Data Analyst, Acme, 2020 - present").`);
      }
      const hi = twins.reduce((a, b) => (b.scores[k].score > a.scores[k].score ? b : a));
      const lo = twins.reduce((a, b) => (b.scores[k].score < a.scores[k].score ? b : a));
      const yes = twins.filter((v) => v.scores[k].selected).length;
      const line = `<b>${esc(hi.name)}</b> ${hi.scores[k].score.toFixed(3)} · <b>${esc(lo.name)}</b> ${lo.scores[k].score.toFixed(3)}<br>${yes} of ${twins.length} names shortlisted (cutoff ${t.cutoff})`;
      const plc = s.placebo_gap > 0.05 ? `<br><span class="muted">Even two names from the same group differ by ${s.placebo_gap.toFixed(3)}: it reacts to names in general.</span>` : "";
      if (s.flip) return card(k, "FAIL", "CHANGED ITS MIND", line + plc);
      if (s.swing > 0.05) return card(k, "INCONCLUSIVE", `SCORE MOVED ${s.swing.toFixed(2)}`, line + plc);
      const far = twins.every((v) => Math.abs(v.scores[k].score - t.cutoff) > 0.15 * t.max);
      const hint = far && k !== "hirelens" ? `<br><span class="muted">Every version is far from the cutoff, so a name can't tip this decision. Try the sample CV to see what happens near it.</span>` : "";
      if (s.swing === 0) return card(k, "PASS", "DIDN'T BLINK", `Every version scored exactly ${hi.scores[k].score.toFixed(3)}.` + hint);
      return card(k, "PASS", "WITHIN 0.05", line + hint);
    }).join("");
    ui.results.hidden = false;
    ui.verdicts.querySelectorAll(".stamp").forEach((st, i) => setTimeout(() => st.classList.add("in"), reduce ? 0 : 140 * i));
    show(job, vs[0], 0);
    if (!quiet) ui.results.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    busy = false; ui.go.disabled = ui.sample.disabled = false;
  }

  const card = (k, cls, label, body) => `<div class="window yc-verdict"><div class="window-bar" aria-hidden="true"><span class="box"></span><span>${TOOL[k].name.toUpperCase()}</span><span class="stripes"></span></div>
    <div class="window-body"><span class="kicker" style="margin:0">${TOOL[k].role}</span><div style="margin:14px 0"><span class="stamp ${cls}">${label}</span></div><p class="small" style="margin:0">${body}</p></div></div>`;

  // Coming back to the page: show the last result again, without replaying the animation.
  function restore() {
    const job = recall();
    if (!job || !job.tools || !job.twins || busy || !ui.results.hidden) return;
    const vs = versions(job);
    ui.stage.hidden = false; ui.error.hidden = true; ui.progress.hidden = true; ui.skip.hidden = true; ui.count.textContent = " ";
    if (!job.sample && !ui.text.value) ui.text.value = job.cv.original;
    buildTools(job.tools); buildBoard(job, vs);
    ui.names.innerHTML = vs.map((v, i) => `<button type="button" class="name-chip${v.slot ? " ph" : ""}" data-i="${i}" aria-pressed="false">${esc(v.name)}<small>${i === 0 ? "YOU" : esc(v.tag.replace("name group", "group").toUpperCase())}</small></button>`).join("");
    ui.names.onclick = (e) => { const b = e.target.closest(".name-chip"); if (b) show(job, vs[+b.dataset.i], +b.dataset.i); };
    vs.forEach((v, i) => fillCell(job, v, i));
    ui.phase.textContent = "All nine versions scored";
    finish(job, vs, true);
  }
  restore();
  window.addEventListener("pageshow", restore);

  form.addEventListener("submit", (e) => { e.preventDefault(); start(false); });
  ui.sample.addEventListener("click", () => start(true));
  ui.skip.addEventListener("click", () => { skip = true; });
  ui.again.addEventListener("click", () => {
    forget(); ui.stage.hidden = true; ui.text.value = ""; ui.file.value = ""; ui.fileLabel.textContent = "Upload .pdf, .docx or .txt";
    form.scrollIntoView({ behavior: reduce ? "auto" : "smooth" }); ui.text.focus();
  });
})();
