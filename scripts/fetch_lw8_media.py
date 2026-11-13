#!/usr/bin/env python3
"""Download source media required for VILNIUS TECH HTML Laboratory Work 8."""
import html
import pathlib
import re
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
MEDIA = ROOT / "assets" / "media"
MEDIA.mkdir(parents=True, exist_ok=True)

VIDEO = "https://videos.pexels.com/video-files/7534244/7534244-hd_1920_1080_25fps.mp4"
AUDIO_PAGES = [
    "https://pixabay.com/sound-effects/film-special-effects-quartz-clock-ticking-one-minute-253102/",
    "https://pixabay.com/sound-effects/quartz-clock-ticking-one-minute-253102/"
]
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"}

def download(url, dest, minimum=1000):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=150) as inp, open(dest, "wb") as out:
        while True:
            chunk = inp.read(65536)
            if not chunk:
                break
            out.write(chunk)
    size = dest.stat().st_size
    if size < minimum:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"File too small ({size} bytes), probable error page")
    print(f"Saved {dest.relative_to(ROOT)} ({size} bytes)")

try:
    download(VIDEO, MEDIA / "typing-keyboard.mp4", minimum=100000)
except Exception as exc:
    print(f"Pexels video download failed: {exc}")

audio_path = MEDIA / "quartz-clock-ticking.mp3"
for page in AUDIO_PAGES:
    if audio_path.exists():
        break
    try:
        request = urllib.request.Request(page, headers=HEADERS)
        body = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "replace")
        variants = [body, html.unescape(body).replace("\\/", "/").replace("\\u002F", "/")]
        urls = []
        for source in variants:
            urls += re.findall(r"https?://(?:cdn\.)?pixabay\.com/(?:download/)?audio/[^\s\"'<>]+?\.mp3(?:\?[^\s\"'<>]*)?", source)
        print(f"Found {len(urls)} candidate MP3 URLs on {page}")
        for url in dict.fromkeys(urls):
            try:
                download(html.unescape(url), audio_path, minimum=10000)
                break
            except Exception as exc:
                print(f"MP3 candidate failed: {exc}")
    except Exception as exc:
        print(f"Pixabay source lookup failed: {exc}")

if not audio_path.exists():
    print("Pixabay sound could not be downloaded automatically. Source: " + AUDIO_PAGES[0])
