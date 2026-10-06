"""Week-30 reel built from embrya.co.il product photos: slow bottom-to-top reveal.
0-2s legs (gray tiger leggings) + hook, 2-6s continuous tilt up into the Amit shirt,
6-8s both products with prices, 8-10s the Amit colour range with the store address."""
import os, math, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = f"{D}/assets"
W, H, FPS, T = 1080, 1920, 30, 10
BG = (247, 239, 234)
ease = lambda p: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, p)))
eout = lambda p: 1 - (1 - min(1, max(0, p))) ** 3
lerp = lambda a, b, t: a + (b - a) * t


def font(sz, wt="Bold"):
    f = ImageFont.truetype(f"{A}/Heebo.ttf", sz); f.set_variation_by_name(wt); return f


def load(n): return Image.open(f"{A}/{n}").convert("RGB")


LEG = load("IMG_1804.jpg")            # טייץ להריון – טייגר אפור
SHIRT = load("amit19-scaled.jpg")     # חולצת עמית – אפור כהה
RANGE = [load(n) for n in ["amit19-scaled.jpg", "IMG_4659.jpg", "amit9-scaled.jpg", "amit3.jpg",
                           "amit16-scaled.jpg", "IMG_4391.jpg", "חולצת-מאי1-scaled.jpg"]]


def cam(img, cx, cy, s):
    """frame of img at scale s (out px per src px), centred on (cx,cy) in 0..1 src coords, clamped to the image"""
    iw, ih = img.size
    s = max(s, W / iw, H / ih)
    bw, bh = W / s, H / s
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


def vblur(img, amt):
    if amt < 0.5: return img
    k = int(amt)
    out = img.copy()
    for i in range(1, 6):
        sh = int(k * i / 5)
        out = Image.blend(out, img.transform(img.size, Image.AFFINE, (1, 0, 0, 0, 1, -sh)), 1 / (i + 1))
    return out


def text_box(lines, yc, maxw=900):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rows = []
    for txt, sz, col in lines:
        f = font(sz); cur = ""
        for w in txt.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f, direction="rtl") <= maxw: cur = t
            else: rows.append((cur, f, col, sz)); cur = w
        rows.append((cur, f, col, sz))
    gap = 16; th = sum(int(r[3] * 1.25) for r in rows) + gap * (len(rows) - 1)
    bw = max(d.textlength(r[0], font=r[1], direction="rtl") for r in rows) + 96
    y = yc - th // 2
    d.rounded_rectangle([W / 2 - bw / 2, y - 38, W / 2 + bw / 2, y + th + 38], radius=34, fill=(28, 24, 24, 190))
    for ln, f, col, sz in rows:
        d.text((W / 2, y), ln, font=f, fill=col, anchor="ma", direction="rtl"); y += int(sz * 1.25) + gap
    return L


WHITE, ROSE = (255, 255, 255, 255), (255, 200, 214, 255)
T_HOOK = text_box([("מה לובשים בשבוע 30 כשבחוץ כבר מתחיל להתקרר?", 74, WHITE)], 470)
T_PRICE = text_box([("טייץ ₪109.", 80, WHITE), ("חולצת עמית ₪99 במקום ₪149.", 64, ROSE)], 1600)
T_STORE = text_box([("אחד העם 9, רחובות.", 80, WHITE), ("או באתר.", 66, ROSE)], 1560)


def card(img, w, h, label):
    """photo card with rounded corners, shadow and a small label strip"""
    s = max(w / img.width, h / img.height)
    ph = img.resize((math.ceil(img.width * s), math.ceil(img.height * s)), Image.LANCZOS)
    ph = ph.crop(((ph.width - w) // 2, 0, (ph.width - w) // 2 + w, h))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=36, fill=255)
    c = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("L", (w + 60, h + 60), 0); ImageDraw.Draw(sh).rounded_rectangle([30, 40, w + 30, h + 40], radius=36, fill=90)
    c.putalpha(sh.filter(ImageFilter.GaussianBlur(16)))
    c.paste(ph, (30, 30), m)
    if label:
        d = ImageDraw.Draw(c); f = font(42, "SemiBold")
        tw = d.textlength(label, font=f, direction="rtl")
        d.rounded_rectangle([30 + w / 2 - tw / 2 - 28, h - 70, 30 + w / 2 + tw / 2 + 28, h + 2], radius=24, fill=(255, 255, 255, 235))
        d.text((30 + w / 2, h - 34), label, font=f, fill=(43, 39, 38), anchor="mm", direction="rtl")
    return c


C_SHIRT = card(SHIRT, 470, 700, "חולצת עמית")
C_LEG = card(LEG, 470, 700, "טייץ טייגר אפור")
C_RANGE = [card(im, 400, 600, None) for im in RANGE]


def paste_scaled(base, layer, cx, cy, sc, rot=0):
    l = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BICUBIC)
    if rot: l = l.rotate(rot, Image.BICUBIC, expand=True)
    base.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))


def overlay(img, layer, t, t0, t1):
    if not (t0 <= t < t1): return
    a = min(1, (t - t0) / 0.25) * (min(1, (t1 - t) / 0.2) if t1 < T else 1)
    l = layer.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(l)


def frame(i):
    t = i / FPS
    if t < 2:                                    # phone low by the floor: legs + sneakers only
        img = cam(LEG, 0.5, lerp(0.80, 0.77, t / 2), 2.9)
    elif t < 4.1:                                # tilt up the leggings to the waistband
        e = ease((t - 2) / 2.1)
        img = cam(LEG, 0.5, lerp(0.77, 0.22, e), lerp(2.9, 2.2, e))
        img = vblur(img, 40 * max(0, (t - 3.7) / 0.4))
    elif t < 6:                                  # keep rising: belly -> smiling face in the Amit shirt
        e = eout((t - 4.1) / 1.9)
        img = cam(SHIRT, 0.55, lerp(0.70, 0.27, e), lerp(2.3, 1.9, e))
        img = vblur(img, 40 * max(0, 1 - (t - 4.1) / 0.35))
    elif t < 8:                                  # the full look: both products, prices
        img = Image.new("RGB", (W, H), BG).convert("RGBA")
        p1, p2 = eout((t - 6) / 0.5), eout((t - 6.12) / 0.5)
        drift = (t - 6) * 6
        paste_scaled(img, C_SHIRT, 300, 860 - drift, lerp(0.6, 1.0, p1), 3)
        paste_scaled(img, C_LEG, 780, 900 + drift, lerp(0.6, 1.0, p2), -3)
        img = img.convert("RGB")
    else:                                        # the Amit colour range, sliding like a rail
        img = Image.new("RGB", (W, H), BG).convert("RGBA")
        d = ImageDraw.Draw(img); d.rectangle([0, 548, W, 562], fill=(150, 140, 136))
        off = ease((t - 8) / 2) * 1500
        for k, c in enumerate(C_RANGE):
            x = 330 + k * 430 - off
            if -300 < x < W + 300:
                d.arc([x - 22, 520, x + 22, 566], 180, 360, fill=(110, 104, 100), width=6)
                paste_scaled(img, c, x, 600 + 330, 1.0)
        img = img.convert("RGB")
    img = img.convert("RGBA")
    overlay(img, T_HOOK, t, 0.0, 2.0)
    overlay(img, T_PRICE, t, 6.35, 8.0)
    overlay(img, T_STORE, t, 8.0, T + 0.01)
    return img.convert("RGB")


if __name__ == "__main__":
    out = f"{D}/reels_week30_from_site.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(FPS * T):
        f = frame(n); p.stdin.write(f.tobytes())
        if os.environ.get("CHECK") and n % 30 == 15: f.save(f"{os.environ['CHECK']}/c{n:03d}.jpg", quality=85)
    p.stdin.close(); p.wait(); print(out, p.returncode)
