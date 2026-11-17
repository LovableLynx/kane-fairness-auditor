"""Render promo.html deterministically: frame t -> screenshot -> ffmpeg (H.264 MP4).
    python render.py stills 2 8 13 19 23 27 33      # preview PNGs
    python render.py video out.mp4                  # full video
"""
import subprocess, sys
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
FPS = 30
import os
PAGE = os.environ.get("PAGE", "promo.html")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def page_for(p, path, w=1080, h=1350):
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={"width": w, "height": h})
    pg.goto((HERE / path).as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(500)
    return b, pg


def main():
    mode = sys.argv[1]
    with sync_playwright() as p:
        if mode == "stills":
            b, pg = page_for(p, PAGE)
            for t in sys.argv[2:]:
                pg.evaluate(f"render({float(t)})")
                pg.screenshot(path=str(HERE / f"still_{t}.png"))
        elif mode == "cover":
            b, pg = page_for(p, "cover.html", 1500, 1000)
            pg.screenshot(path=str(HERE / sys.argv[2]))
        elif mode == "video":
            b, pg = page_for(p, PAGE)
            dur = pg.evaluate("DUR")
            ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe",
                                   "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                                   "-crf", "18", "-preset", "slow", "-movflags", "+faststart", sys.argv[2]],
                                  stdin=subprocess.PIPE)
            for i in range(int(dur * FPS)):
                pg.evaluate(f"render({i / FPS})")
                ff.stdin.write(pg.screenshot(type="png"))
            ff.stdin.close(); ff.wait()
        b.close()


if __name__ == "__main__":
    main()
