import sys, time, json
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; BASE = "https://kane-fairness-auditor.onrender.com"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5)
    pg.goto(BASE + "/your-cv", timeout=120000); pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{OUT}/tw/form.jpg", type="jpeg", quality=90)
    pg.click("#yc-sample"); t0 = time.time(); ts = []; i = 0
    def snap():
        global i
        pg.evaluate("window.scrollTo(0, document.querySelector('#yc-stage').getBoundingClientRect().top + scrollY - 70)")
        pg.screenshot(path=f"{OUT}/tw/f_{i:04d}.jpg", type="jpeg", quality=90); ts.append(round(time.time() - t0, 3)); i += 1
    while time.time() - t0 < 60:
        if pg.locator("#yc-results:not([hidden])").count():
            break
        snap()
    json.dump(ts, open(f"{OUT}/tw/ts.json", "w"))
    print("frames", i, "secs", ts[-1])
    pg.wait_for_timeout(2500)
    pg.evaluate("window.scrollTo(0, document.querySelector('#yc-results').getBoundingClientRect().top + scrollY - 70)")
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/tw/results.jpg", type="jpeg", quality=90)
    pg.evaluate("scrollBy(0, 600)"); pg.wait_for_timeout(500)
    pg.screenshot(path=f"{OUT}/tw/results2.jpg", type="jpeg", quality=90)
    b.close()
