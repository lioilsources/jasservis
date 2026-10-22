#!/usr/bin/env python3
"""Photos for the site, for @claude: from the Firmy.cz profile or attached in an issue.

  firmy-foto.py seznam              offers on the profile: title, price, photo URL (TSV)
  firmy-foto.py stahni <url> <name> download one photo and save it for the site:
                                    <name>.jpg   max 1280 px wide (page photo)
                                    <name>-s.jpg 600x380 crop (tile on overview pages)
                                    into jasservis.cz/wp-content/uploads/<YYYY>/<MM>/
  firmy-foto.py ulozit <file> <name> the same for a photo the owner attached to an issue
                                    or comment (claude-code-action downloads those
                                    into /tmp/github-images/)

Only photos from Seznam's image CDN (dNN-a.sdn.cz) or from the attachments folder
are accepted and they are written only into the uploads folder, so @claude can be allowed to run this without general web or
file-system access. Needs Pillow.
"""
import html
import io
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

PROFILE = "https://www.firmy.cz/detail/12996882-j-s-servis-jaroslav-mateju-statenice-cerny-vul.html"
CDN = re.compile(r"^https://d\d+-a\.sdn\.cz/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.(?:jpe?g|png|webp)$")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jasservis.cz")
MAX_BYTES = 20 * 1024 * 1024
ATTACHMENTS = "/tmp/github-images"
UA = {"User-Agent": "Mozilla/5.0 (jasservis.cz photo sync)"}


def fetch(url, host=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            if host and urllib.parse.urlsplit(r.geturl()).hostname != host:
                sys.exit("chyba: úložiště přesměrovalo jinam, fotku nestahuju")
            data = r.read(MAX_BYTES + 1)
    except urllib.error.URLError as e:
        sys.exit(f"chyba: nepodařilo se stáhnout {url}: {getattr(e, 'code', '')} {getattr(e, 'reason', e)}")
    if len(data) > MAX_BYTES:
        sys.exit(f"chyba: soubor je větší než {MAX_BYTES // 2**20} MB")
    return data


def seznam():
    page = fetch(PROFILE).decode("utf-8", "replace")
    blocks = re.split(r'class="item(?: hidden)? item-marketOffer"', page)[1:]
    if not blocks:
        sys.exit("chyba: na profilu jsem nenašel žádné nabídky (změnila se stránka Firmy.cz?)")
    print("nazev\tcena\tfoto")
    for b in blocks:
        def field(pat):
            m = re.search(pat, b)
            return html.unescape(html.unescape(m.group(1))).strip() if m else "-"
        img = field(r'<img src="([^"?]+)')
        print("\t".join((field(r'class="offerTitle">([^<]*)'), field(r'class="offerPrice">([^<]*)'),
                         img if CDN.match(img) else "-")))


def check_name(name):
    if not NAME.match(name) or len(name) > 60:
        sys.exit("chyba: název jen malými písmeny bez diakritiky, číslice a pomlčky, např. servis-klimatizaci")


def stahni(url, name):
    url = url.split("?", 1)[0]  # without ?fl=… the CDN serves the original size
    if not CDN.match(url):
        sys.exit("chyba: beru jen fotky z https://dNN-a.sdn.cz/ (úložiště Firmy.cz)")
    check_name(name)
    uloz(fetch(url, urllib.parse.urlsplit(url).hostname), name)


def ulozit(path, name):
    real = os.path.realpath(path)
    if os.path.dirname(real) != os.path.realpath(ATTACHMENTS) or not os.path.isfile(real):
        sys.exit(f"chyba: beru jen přílohy ze zadání, tedy soubory přímo v {ATTACHMENTS}/")
    check_name(name)
    if os.path.getsize(real) > MAX_BYTES:
        sys.exit(f"chyba: soubor je větší než {MAX_BYTES // 2**20} MB")
    with open(real, "rb") as f:
        uloz(f.read(), name)


def uloz(data, name):
    from PIL import Image, ImageOps

    try:
        im = Image.open(io.BytesIO(data))
    except Exception:
        sys.exit("chyba: soubor není obrázek, který umím přečíst")
    # MPO = JPEG with extra frames, which many phone cameras write
    if im.format not in ("JPEG", "MPO", "PNG", "WEBP"):
        sys.exit(f"chyba: nečekaný formát {im.format}")
    im = ImageOps.exif_transpose(im).convert("RGB")

    big = im if im.width <= 1280 else im.resize((1280, round(im.height * 1280 / im.width)), Image.LANCZOS)
    tile = ImageOps.fit(im, (600, 380), Image.LANCZOS)

    today = date.today()
    rel = f"wp-content/uploads/{today:%Y}/{today:%m}"
    folder = os.path.normpath(os.path.join(ROOT, rel))
    os.makedirs(folder, exist_ok=True)
    for img, suffix in ((big, ""), (tile, "-s")):
        path = os.path.join(folder, f"{name}{suffix}.jpg")
        existed = os.path.exists(path)
        img.save(path, "JPEG", quality=85, optimize=True, progressive=True)
        note = " (přepsáno)" if existed else ""
        print(f"{rel}/{name}{suffix}.jpg\t{img.width}x{img.height}{note}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["seznam"]:
        seznam()
    elif len(args) == 3 and args[0] == "stahni":
        stahni(args[1], args[2])
    elif len(args) == 3 and args[0] == "ulozit":
        ulozit(args[1], args[2])
    else:
        sys.exit(__doc__)
