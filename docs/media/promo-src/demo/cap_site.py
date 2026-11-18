import sys, time
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; BASE = "https://kane-fairness-auditor.onrender.com"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.goto(BASE + "/healthz", timeout=120000)
    shots = {"landing": "/", "results": "/results", "r_talentscreen": "/results/talentscreen", "r_hirelens": "/results/hirelens",
             "r_quickmatch": "/results/quickmatch", "method": "/method", "tool_talentscreen": "/talentscreen/",
             "tool_hirelens": "/hirelens/", "tool_quickmatch": "/quickmatch/"}
    for k, u in shots.items():
        pg.goto(BASE + u, timeout=120000); pg.wait_for_timeout(2500)
        pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))"); pg.wait_for_timeout(600)
        pg.screenshot(path=f"{OUT}/site/{k}.png", full_page=True); print(k)
    # closed-loop panel and Kane verified panel as element shots
    pg.goto(BASE + "/results/talentscreen"); pg.wait_for_timeout(2000)
    pg.locator("section:has-text('CLOSED_LOOP')").first.screenshot(path=f"{OUT}/site/loop_panel.png")
    # Twin your CV: live sample run, frames every 100 ms
    pg.goto(BASE + "/your-cv"); pg.wait_for_timeout(2000)
    pg.screenshot(path=f"{OUT}/tw/form.png")
    pg.click("#yc-sample"); t0 = time.time(); i = 0
    while time.time() - t0 < 40:
        pg.screenshot(path=f"{OUT}/tw/f_{i:04d}.jpg", type="jpeg", quality=88); i += 1
        if pg.locator("#yc-results:not([hidden])").count() and time.time() - t0 > 3:
            break
    print("run frames", i, round(time.time() - t0, 1))
    pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{OUT}/tw/results_full.png", full_page=True)
    b.close()
