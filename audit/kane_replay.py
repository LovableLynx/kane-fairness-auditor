"""Replay a Kane-verified audit for free: run the Playwright test Kane CLI exported, offline.

Every Kane run leaves code-export/test.py in its session folder: the exact steps Kane took, with the
locators and the score-reading JavaScript it generated. With TestMu "smart" mode off it is plain
Playwright, so it costs no Kane credits. This script:

  1. takes Kane's exported test for a verified candidate (kane-tests/<target>_<candidate>/, saved with --save),
  2. strips the values Kane stored, so every number must be read from the page again,
  3. replays the test against the tool (optionally at another URL),
  4. compares the fresh readings with Kane's verified ones.

What it can and cannot do: Kane locates the score by the text it saw (e.g. the element reading "0.216"),
and offline there is no self-healing. So the replay CONFIRMS a tool still gives exactly the readings Kane
verified, for free; if anything changed it cannot read the new value, and says so: run Kane again.
It never reports a reading it did not take from the page.

    pip install -r requirements-replay.txt && python -m playwright install chromium
    python audit/kane_replay.py --save --target quickmatch --candidate cand02    # once, after a Kane run
    python audit/kane_replay.py --target quickmatch --candidate cand02           # every commit, 0 credits

Exit codes: 0 every reading confirmed, the Kane verdict stands; 1 not confirmed, re-run Kane.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
import twin_audit as ta  # noqa: E402


TESTS = ROOT / "kane-tests"


def save(checkpoint: Path, dest: Path) -> None:
    """Copy Kane's exported test and its verified readings into the repo, so CI can replay them."""
    cp, source = load_export(checkpoint)
    if "select_option" in source:
        raise SystemExit("this Kane run changed a page setting; not saving it as a reference")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "test.py").write_text(source, encoding="utf-8")
    keep = {k: cp.get(k) for k in ("candidate", "test_url", "credits", "fingerprint")}
    keep["twins"] = [{k: t[k] for k in ("gender", "group", "slot", "name", "file", "score", "decision", "selected")}
                     for t in cp["twins"]]
    (dest / "kane.json").write_text(json.dumps(keep, indent=1), encoding="utf-8")
    print(f"saved {dest.relative_to(ROOT)} (Kane evidence: {cp.get('test_url')})")


def load_export(checkpoint: Path) -> tuple[dict, str]:
    cp = json.loads(checkpoint.read_text(encoding="utf-8"))
    if not cp.get("evidence"):
        raise SystemExit(f"{checkpoint.name}: no Kane session recorded")
    export = Path(cp["evidence"]).parents[1] / "code-export" / "test.py"
    if not export.is_file():
        raise SystemExit(f"Kane's exported test not found at {export}")
    return cp, export.read_text(encoding="utf-8")


def prepare(source: str, url: str | None) -> str:
    # Drop the values Kane stored at authoring time: the replay must read every number itself.
    source, n = re.subn(r"^(\s*)variables=\{.*?\},\s*$", r"\1variables={},", source, count=1, flags=re.M)
    if n != 1:
        raise SystemExit("could not find the stored variables in Kane's export; refusing to replay")
    if url:
        old = re.search(r'page\.goto\("([^"]+)"\)', source)
        if old:
            source = source.replace(old.group(1), url)
    return source


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--placebo", action="store_true", default=True)
    ap.add_argument("--cache", default=str(ROOT / "reports" / "kane-cache"))
    ap.add_argument("--url", help="replay against this URL instead of the one Kane used")
    ap.add_argument("--json", help="write the comparison here")
    ap.add_argument("--save", action="store_true", help="store Kane's exported test for this candidate in kane-tests/")
    args = ap.parse_args()

    dest = TESTS / f"{args.target}_{args.candidate}"
    if args.save:
        save(Path(args.cache) / f"{args.target}_local_short_p_{args.candidate}.json", dest)
        return 0
    if not (dest / "test.py").is_file():
        raise SystemExit(f"no saved Kane test at {dest}; run with --save after a Kane-verified run")
    cp = json.loads((dest / "kane.json").read_text(encoding="utf-8"))
    source = (dest / "test.py").read_text(encoding="utf-8")
    os.environ.setdefault("TESTMU_SMART", "0")      # offline: no vision, no healing, no credits
    for k in cp["twins"]:  # the same CV files Kane was given, instead of fetching them from TestMu's cloud
        key = ta.TwinResult(k["gender"], k["group"], k["slot"], k["name"], k["file"]).key
        os.environ[f"TESTMU_VAR_cv_{key}"] = (ROOT / k["file"]).read_text(encoding="utf-8")
    os.environ.setdefault("TESTMU_HEADLESS", "true")
    import testmu  # noqa: E402  (installed from requirements-replay.txt)
    from testmu._v4 import _vars  # noqa: E402
    from playwright.async_api._generated import Browser  # noqa: E402

    # Offline, Kane's vision clicks fall back to the pixel position Kane recorded on its 1920x1080 screen,
    # so the replay page must have the same size (headless ignores --window-size).
    _new_context = Browser.new_context

    async def new_context(self, *a, **kw):
        if not kw.get("viewport"):
            kw["viewport"] = {"width": 1920, "height": 1080}
        return await _new_context(self, *a, **kw)
    Browser.new_context = new_context

    # Live, Kane's vision step took seconds to look at the page, so the page had always settled before its
    # click. The exported script clicks at once; wait for the page to finish loading first, as Kane did.
    import testmu._v4 as v4  # noqa: E402
    _coords = v4.get_vision_coordinates

    async def get_vision_coordinates(page, *a, **kw):
        try:
            await page.wait_for_load_state("load", timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:  # noqa: BLE001 - a slow page still gets its recorded click
            pass
        await page.wait_for_timeout(800)
        return await _coords(page, *a, **kw)
    v4.get_vision_coordinates = get_vision_coordinates

    ns: dict = {"__name__": "kane_export"}
    exec(compile(prepare(source, args.url), "kane_export_test.py", "exec"), ns)  # Kane's own generated test
    _vars._variable_store.clear()
    try:
        testmu.run(ns["test"])
    except Exception as e:  # noqa: BLE001 - a failed step still leaves the values read before it
        print(f"replay stopped: {type(e).__name__}: {e}", file=sys.stderr)
    store = dict(_vars._variable_store)

    # Readings Kane took with its vision AI (vision_query) cannot be replayed offline: never count them as confirmed.
    vision = set(re.findall(r"set_var\('(\w+)', await testmu\.vision_query\(", source))

    def check(name: str, got, want) -> str:
        if name in vision:
            return "vision"
        return "confirmed" if got is not None and got == want else "changed"

    rows, counts = [], {"confirmed": 0, "vision": 0, "changed": 0}
    for k in cp["twins"]:
        t = ta.TwinResult(k["gender"], k["group"], k["slot"], k["name"], k["file"])
        raw = store.get(f"score_{t.key}")
        m = ta.NUM_RE.search(str(raw)) if raw is not None else None
        score = round(ta.normalise(float(m.group())), 6) if m else None
        decision = store.get(f"decision_{t.key}")
        s = check(f"score_{t.key}", score, round(k["score"], 6))
        d = check(f"decision_{t.key}", ta.to_selected(decision), k["selected"])
        counts[s] += 1
        counts[d] += 1
        rows.append({"name": t.name, "kane": [k["score"], k["decision"]], "replay": [score, decision], "score": s, "decision": d})
    label = {"confirmed": "=", "vision": "Kane vision AI, not replayable", "changed": "CHANGED"}
    for r in rows:
        print(f"{r['name']:<20} score Kane {r['kane'][0]!s:<6} replay {r['replay'][0]!s:<6} {label[r['score']]:<6} | "
              f"decision Kane {str(r['kane'][1]):<26} replay {str(r['replay'][1]):<26} {label[r['decision']]}")
    total = sum(counts.values())
    print(f"\nreadings re-read from the page and identical to Kane's: {counts['confirmed']}/{total}"
          f"  (read by Kane's vision AI, not replayable offline: {counts['vision']}; changed or unreadable: {counts['changed']})")
    ok = counts["changed"] == 0 and counts["confirmed"] > 0
    if ok:
        print(f"CONFIRMED: every reading that can be replayed is unchanged since Kane verified it ({cp.get('test_url')}). 0 Kane credits.")
    else:
        print("NOT CONFIRMED: the tool's output or page changed since Kane verified it. Re-run the Kane audit.")
    if args.json:
        Path(args.json).write_text(json.dumps({"target": args.target, "candidate": args.candidate, "kane_test_url": cp.get("test_url"),
                                               "url": args.url, "rows": rows, "counts": counts,
                                               "result": "CONFIRMED" if ok else "NOT CONFIRMED"}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
