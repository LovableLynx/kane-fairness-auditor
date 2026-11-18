"""Write every frame of demo.html to frames/NNNNN.jpg, in chunks with a fresh browser; resumable."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).parent; FPS = 30; DUR = 240; CHUNK = 600
OUT = HERE / "frames"; OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WAIT = "(t) => { render(t); return Promise.all([...document.images].map(i => i.complete && i.naturalWidth ? null : i.decode().catch(() => null))); }"
total = DUR * FPS
with sync_playwright() as p:
    start = 0
    while start < total:
        todo = [i for i in range(start, min(total, start + CHUNK)) if not (OUT / f"{i:05d}.jpg").exists()]
        if todo:
            b = p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files"])
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.goto((HERE / "demo.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1500)
            for i in todo:
                for attempt in range(3):
                    try:
                        pg.evaluate(WAIT, i / FPS)
                        (OUT / f"{i:05d}.jpg").write_bytes(pg.screenshot(type="jpeg", quality=92, timeout=60000)); break
                    except Exception as e:  # noqa: BLE001
                        print("retry", i, type(e).__name__, flush=True)
                        if attempt == 2: raise
            b.close()
        start += CHUNK
        print("done to", min(total, start), flush=True)
