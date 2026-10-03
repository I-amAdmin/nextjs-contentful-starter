"""Embrya maternity-leggings Meta ad reel: 20s, 1080x1920, 30fps, frame-rendered and piped to ffmpeg.
Captions sit inside the Reels safe area (y ~ 260-1250, centered, < 900px wide) and read without sound."""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

D = os.path.dirname(os.path.abspath(__file__))
IMG = f"{D}/img"
FD = f"{D}/../fonts/fontsource-heebo-5.3.0/package/files"
LOGO = f"{D}/../img/logo.png"
W, H, FPS, TOTAL = 1080, 1920, 30, 20.0
NF = int(TOTAL * FPS)
HE = lambda w, s: ImageFont.truetype(f"{FD}/heebo-hebrew-{w}-normal.woff", s)
LA = lambda w, s: ImageFont.truetype(f"{FD}/heebo-latin-{w}-normal.woff", s)
CREAM = (246, 239, 232)
INK = (58, 40, 36)
BLUSH = (226, 160, 138)
rng = np.random.default_rng(11)

clamp = lambda p: min(1.0, max(0.0, p))
ease_io = lambda p: 0.5 - 0.5 * math.cos(math.pi * clamp(p))
ease_out = lambda p: 1 - (1 - clamp(p)) ** 3


def elastic(p):
    p = clamp(p)
    if p in (0.0, 1.0):
        return p
    return 2 ** (-10 * p) * math.sin((p * 10 - 0.75) * 2 * math.pi / 3) + 1


N = {k: f"{k}-720x960.jpg" for k in ["ZOE_NOIR-SF411_LG411_8small", "ZOE_TERRACOTTA-SF411_04small", "LIBERTY5", "LIBERTY4",
                                       "LIBERTY1", "IMG_5838", "IMG_6460", "IMG_2475", "IMG_2422", "IMG_4508", "IMG_1658",
                                       "IMG_1786", "IMG_1767", "IMG_1604", "IMG_1522", "navy", "light-grey", "legging1", "רכיבה1", "רכיבה2"]}
N["brown_straight"] = "טייץ-ישר-חום-קטן-720x960.jpg"
N["brown_biker"] = "brown_biker_user.jpg"   # supplied by the client for the "לספורט" beat


def grade(im):
    a = np.asarray(im).astype(np.float32) / 255
    a = a * 0.96 + 0.035                                   # gentle lift: soft, airy
    a = (a - 0.5) * 1.03 + 0.5
    a *= np.array([1.02, 1.0, 0.975])                      # warm
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


_cache = {}


def shot_img(name, cx=0.5, box=None):
    key = (name, cx, box)
    if key not in _cache:
        src = Image.open(f"{IMG}/{N.get(name, name)}").convert("RGB")
        if box:
            x0, y0, cw = box
        else:
            cw = src.height * 9 / 16; x0 = (src.width - cw) * cx; y0 = 0
        ch = cw * 16 / 9
        im = src.resize((W * 2, H * 2), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
        if box:
            im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
        _cache[key] = grade(im)
    return _cache[key]


def kb(img, t, d, z0, z1, punch=True, pan=(0, 0)):
    p = ease_io(t / d)
    z = z0 + (z1 - z0) * p
    if punch:
        z *= 1 + 0.08 * (1 - ease_out(t / 0.4))
    iw, ih = img.size; cw, ch = iw / z, ih / z
    x = (iw - cw) / 2 + pan[0] * (iw - cw) / 2 * (2 * p - 1)
    y = (ih - ch) / 2 + pan[1] * (ih - ch) / 2 * (2 * p - 1)
    return img.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


# ---------- captions: white pill, bold first line ----------
_pill = {}


def pill(lines, big=88, small=62, bg=(255, 255, 255, 236), fg=INK, maxw=860):
    key = (tuple(lines), big, small, bg)
    if key in _pill:
        return _pill[key]
    tmp = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    while True:   # shrink until every line fits the safe width
        fonts = [HE(800, big)] + [HE(500, small)] * (len(lines) - 1)
        bbs = [tmp.textbbox((0, 0), s, font=f) for s, f in zip(lines, fonts)]
        if max(b[2] - b[0] for b in bbs) <= maxw or big < 40:
            break
        big, small = int(big * 0.94), int(small * 0.94)
    gap = 18
    tw = max(b[2] - b[0] for b in bbs); th = sum(b[3] - b[1] for b in bbs) + gap * (len(lines) - 1)
    pw, ph = tw + 110, th + 80
    im = Image.new("RGBA", (pw + 80, ph + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, 40 + pw, 50 + ph), ph // 2 if len(lines) == 1 else 44, fill=(60, 30, 20, 70))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + pw, 40 + ph), ph // 2 if len(lines) == 1 else 44, fill=bg)
    y = 40 + 40
    for (s, f), b in zip(zip(lines, fonts), bbs):
        d.text((40 + (pw - (b[2] - b[0])) // 2 - b[0], y - b[1]), s, font=f, fill=fg)
        y += b[3] - b[1] + gap
    _pill[key] = im
    return im


def put(fr, im, t, d, cy, stretch=False):
    """elastic pop-in (optionally rubber-band stretch on x), quick fade-out at the end"""
    if t <= 0:
        return
    q = elastic(t / 0.55)
    out = 1 - ease_out((t - (d - 0.22)) / 0.22) if t > d - 0.22 else 1
    if stretch:
        sx = 1 + 0.55 * (1 - q) if t < 0.55 else q
        sx = max(0.05, 0.4 + 0.6 * q + 0.25 * math.sin(clamp(t / 0.5) * math.pi) * (1 - clamp(t / 0.5)))
        sy = max(0.05, 0.6 + 0.4 * q)
    else:
        sx = sy = max(0.05, 0.7 + 0.3 * q)
    p = im.resize((max(1, int(im.width * sx)), max(1, int(im.height * sy))), Image.BICUBIC)
    a = min(1, t / 0.15) * out
    if a < 1:
        p.putalpha(p.getchannel("A").point(lambda v, k=a: int(v * k)))
    fr.paste(p, (int(W / 2 - p.width / 2), int(cy - p.height / 2)), p)


# ---------- segments ----------
def single(name, cx=0.5, box=None, z=(1.0, 1.07), pan=(0, 0), cap=None, cy=0.30, cap_at=0.2, punch=True):
    img = shot_img(name, cx, box)
    pm = pill(cap) if cap else None
    def r(t, d):
        fr = kb(img, t, d, z[0], z[1], punch, pan)
        if pm:
            put(fr, pm, t - cap_at, d - cap_at, H * cy)
        return fr
    return r


def hook():
    """3x3 mosaic pops in tile by tile, then the centre tile grows to full frame under a rubber-band headline"""
    names = ["ZOE_NOIR-SF411_LG411_8small", "IMG_1786", "LIBERTY5", "navy", "LIBERTY4", "רכיבה1",
             "ZOE_TERRACOTTA-SF411_04small", "IMG_2422", "brown_straight"]
    tiles = [shot_img(n).resize((W // 3, H // 3), Image.LANCZOS) for n in names]
    center = shot_img("LIBERTY4")
    head = pill(["הטייץ שגדל איתך"], big=104)
    def r(t, d):
        fr = Image.new("RGB", (W, H), CREAM)
        g = 10
        grow = ease_io((t - 0.95) / 0.75)
        for i, tl in enumerate(tiles):
            q = elastic((t - 0.06 * i) / 0.45)
            if q <= 0 or (i == 4):
                continue
            tw, th = int((W // 3 - g) * q), int((H // 3 - g) * q)
            if tw < 2 or th < 2:
                continue
            cxp = (i % 3) * (W // 3) + W // 6; cyp = (i // 3) * (H // 3) + H // 6
            im = tl.resize((tw, th), Image.BILINEAR)
            if grow > 0:   # outer tiles get pushed out as the centre grows
                cxp += int((cxp - W / 2) * grow * 1.4); cyp += int((cyp - H / 2) * grow * 1.4)
            fr.paste(im, (cxp - tw // 2, cyp - th // 2))
        # centre tile
        q = elastic((t - 0.24) / 0.45)
        if q > 0:
            x0 = W / 3 + g / 2; y0 = H / 3 + g / 2; x1 = 2 * W / 3 - g / 2; y1 = 2 * H / 3 - g / 2
            x0, y0, x1, y1 = [a + (b - a) * grow for a, b in zip((x0, y0, x1, y1), (0, 0, W, H))]
            cw_, ch_ = (x1 - x0) * min(q, 1.05), (y1 - y0) * min(q, 1.05)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            zoom = 1 + 0.10 * (1 - grow)
            sw, sh = center.width / zoom, center.height / zoom
            im = center.resize((max(2, int(cw_)), max(2, int(ch_))), Image.BILINEAR,
                               box=((center.width - sw) / 2, (center.height - sh) / 2, (center.width + sw) / 2, (center.height + sh) / 2))
            fr.paste(im, (int(mx - cw_ / 2), int(my - ch_ / 2)))
        put(fr, head, t - 0.30, 99, H * 0.30, stretch=True)
        return fr
    return r


def beats(words_imgs, cy=0.32):
    """'לעבודה, ליומיום, לספורט ולבית' — one word per hard cut, punch-zoom on each"""
    n = len(words_imgs)
    items = [(shot_img(nm, cx), pill([w], big=120)) for w, nm, cx in words_imgs]
    def r(t, d):
        k = min(n - 1, int(t / (d / n)))
        lt = t - k * d / n
        img, pm = items[k]
        fr = kb(img, lt, d / n, 1.12, 1.18, True)
        put(fr, pm, lt, 99, H * cy)
        return fr
    return r


def split2(a, b, cap, cy=0.30):
    A = shot_img(a, 0.5).resize((W, H)); B = shot_img(b, 0.5).resize((W, H))
    pm = pill(cap)
    def r(t, d):
        fr = Image.new("RGB", (W, H), CREAM)
        p = ease_out(t / 0.3); hw = W // 2 - 5
        drift = int(30 * ease_io(t / d))
        fr.paste(A.crop((W // 4, 0, W // 4 + hw, H)), (0, int(-H * (1 - p)) - drift + 15))
        fr.paste(B.crop((W // 4, 0, W // 4 + hw, H)), (W - hw, int(H * (1 - p)) + drift - 15))
        put(fr, pm, t - 0.35, d - 0.35, H * cy)
        return fr
    return r


def strip(names, cap, cy=0.30):
    """fast colour/print montage under a pinned caption"""
    imgs = [shot_img(nm, cx) for nm, cx in names]
    pm = pill(cap)
    def r(t, d):
        k = min(len(imgs) - 1, int(t / (d / len(imgs))))
        lt = t - k * d / len(imgs)
        fr = kb(imgs[k], lt, d / len(imgs), 1.05, 1.1, True)
        put(fr, pm, t - 0.1, d - 0.1, H * cy)
        return fr
    return r


def endcard():
    bg = Image.new("RGB", (W, H), CREAM)
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((W / 2 - 700, 80, W / 2 + 700, 1480), fill=120)
    bg = Image.composite(Image.new("RGB", (W, H), (240, 222, 210)), bg, glow.filter(ImageFilter.GaussianBlur(190)))
    lg = Image.open(LOGO).convert("RGBA"); lw = 800; lh = round(lg.height * lw / lg.width)
    a = lg.getchannel("A").resize((lw, lh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))
    logo = Image.new("RGBA", (lw, lh), (35, 28, 26, 0)); logo.putalpha(a)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tx)
    for s, f, c, y in [("טייצים להריון", HE(500, 72), INK, 960), ("embrya.co.il", LA(300, 50), (110, 80, 66), 1060)]:
        bb = d.textbbox((0, 0), s, font=f); d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), s, font=f, fill=c + (255,))
    cta = pill(["לכל הדגמים באתר"], big=64, bg=BLUSH + (255,), fg=(255, 255, 255))

    def r(t, d_):
        fr = bg.copy().convert("RGBA")
        p1 = ease_out(t / 1.2); sc = 1.12 - 0.12 * p1
        l = logo.resize((round(lw * sc), round(lh * sc)), Image.LANCZOS)
        if p1 < 1:
            l = l.filter(ImageFilter.GaussianBlur(14 * (1 - p1)))
        l.putalpha(l.getchannel("A").point(lambda v, k=min(1, t / 0.8): int(v * k)))
        fr.alpha_composite(l, ((W - l.width) // 2, 690 - l.height // 2))
        p2 = ease_out((t - 0.9) / 0.7)
        if p2 > 0:
            tt = tx.copy(); tt.putalpha(tx.getchannel("A").point(lambda v, k=p2: int(v * k)))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(tt, (0, round(22 * (1 - p2)))); fr.alpha_composite(lay)
        out = fr.convert("RGB")
        if t > 1.5:   # CTA pill pops, then breathes gently
            ct = t - 1.5
            if ct <= 0.6:
                put(out, cta, ct, 99, 1210)
            else:
                s = 1 + 0.03 * math.sin((ct - 0.6) * 2 * math.pi / 1.1)
                c2 = cta.resize((int(cta.width * s), int(cta.height * s)), Image.BICUBIC)
                out.paste(c2, (W // 2 - c2.width // 2, 1210 - c2.height // 2), c2)
        return out
    return r


# ---------- transitions ----------
def rubber(a, b, p):
    """elastic stretch: b springs out of a vertical slit with overshoot, a squeezes away"""
    q = elastic(p)
    fr = a.copy()
    sa = max(0.02, 1 - ease_out(p * 1.4))
    if sa > 0.03:
        fr = Image.new("RGB", (W, H), CREAM)
        sq = a.resize((max(2, int(W * sa)), H), Image.BILINEAR); fr.paste(sq, ((W - sq.width) // 2, 0))
    w = max(2, int(W * q))
    if w >= 2:
        bb = b.resize((w, H), Image.BILINEAR)
        if w > W:
            bb = bb.crop(((w - W) // 2, 0, (w - W) // 2 + W, H))
        fr.paste(bb, ((W - bb.width) // 2, 0))
    return fr


def whip(direction=1):
    def f(a, b, p):
        e = ease_io(p); off = int(W * e) * direction
        fr = Image.new("RGB", (W, H)); fr.paste(a, (-off, 0)); fr.paste(b, (W * direction - off, 0))
        k = 1 + int(26 * math.sin(math.pi * p))
        return fr.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR) if k > 1 else fr
    return f


def soft_flash(a, b, p):
    w = max(0, 1 - abs(p - 0.5) * 2.6)
    base = a if p < 0.5 else b
    return Image.blend(base, Image.new("RGB", (W, H), (255, 244, 236)), w * 0.9)


def cut(a, b, p):
    return b


# ---------- timeline (all captions quoted/condensed from the product pages; see notes) ----------
SEG = [
    (hook(), 2.3, cut, 0.0),
    (single("LIBERTY4", z=(1.0, 1.08), cap=["חגורת בטן נוחה", "שמתאימה את עצמה לגוף לאורך כל ההריון"], punch=False), 2.4, rubber, 0.45),
    (single("ZOE_NOIR-SF411_LG411_8small", cx=0.45, cap=["חופש תנועה מלא", "ונוחות לאורך כל היום"]), 2.2, whip(1), 0.30),
    (single("ZOE_TERRACOTTA-SF411_04small", cx=0.5, z=(1.08, 1.0), cap=["רך במיוחד", "מחבק בעדינות את הבטן"]), 2.2, rubber, 0.45),
    (single("IMG_1658", box=(170, 0, 380), z=(1.0, 1.1), cap=["התפרים עוברים מתחת לבטן", "ולא לוחצים"], cy=0.55), 2.2, soft_flash, 0.25),
    (beats([("לעבודה", "navy", 0.5), ("ליומיום", "IMG_1786", 0.5), ("לספורט", "brown_biker", 0.5), ("ולבית", "LIBERTY5", 0.5)]), 2.4, rubber, 0.45),
    (split2("ZOE_NOIR-SF411_LG411_8small", "ZOE_TERRACOTTA-SF411_04small", ["מתאים לאורך כל ההיריון", "וגם אחריו"]), 2.4, whip(-1), 0.30),
    (strip([("IMG_2422", .5), ("light-grey", .5), ("IMG_1767", .5), ("legging1", .5), ("IMG_1604", .5), ("brown_straight", .5)],
           ["מגוון גזרות", "אורכים והדפסים"]), 1.9, rubber, 0.45),
    (endcard(), None, None, 0),
]
END = 4.0
fixed = -sum(s[3] for s in SEG[:-1])
flex = sum(s[1] for s in SEG[:-1])
k = (TOTAL - END - fixed) / flex
SEG = [(r, d * k, tr, td) for r, d, tr, td in SEG[:-1]] + [(SEG[-1][0], END, None, 0)]
assert all(s[3] < s[1] for s in SEG[:-1])
starts, t0 = [], 0.0
for s in SEG:
    starts.append(t0); t0 += s[1] - s[3]

# finishing layers
GRAIN = [Image.fromarray(np.clip(rng.normal(128, 6, (H // 2, W // 2)), 0, 255).astype(np.uint8)).resize((W, H)).convert("RGB") for _ in range(6)]
VIG = Image.new("L", (W, H), 0); ImageDraw.Draw(VIG).ellipse((-300, -240, W + 300, H + 240), fill=255)
VIG = VIG.filter(ImageFilter.GaussianBlur(220)).point(lambda v: int(255 - (255 - v) * 0.35))
LEAK = Image.new("RGB", (W, H), (0, 0, 0)); ld = ImageDraw.Draw(LEAK)
ld.ellipse((-200, -100, 700, 800), fill=(255, 178, 140)); ld.ellipse((500, 1100, 1400, 2100), fill=(255, 205, 170))
LEAK = LEAK.filter(ImageFilter.GaussianBlur(200))


def frame(n):
    t = n / FPS
    i = max(k for k in range(len(SEG)) if starts[k] <= t + 1e-9)
    if i > 0 and t < starts[i - 1] + SEG[i - 1][1]:
        i -= 1
    r, d, tr, td = SEG[i]
    cur = r(t - starts[i], d)
    if tr is not None and td > 0 and t >= starts[i] + d - td:
        p = (t - (starts[i] + d - td)) / td
        cur = tr(cur, SEG[i + 1][0](t - starts[i + 1], SEG[i + 1][1]), p)
    # blush light leak breathing in around transitions (screen blend)
    lk = 0.0
    for s in starts[1:]:
        lk = max(lk, 0.32 * max(0, 1 - abs(t - s) / 0.45))
    if lk > 0:
        cur = Image.blend(cur, ImageChops.screen(cur, LEAK), lk)
    if t < starts[-1] + 0.3:
        cur = ImageChops.overlay(cur, GRAIN[n % len(GRAIN)])
    return Image.composite(cur, Image.new("RGB", (W, H), (20, 12, 10)), VIG)


def main():
    only = os.environ.get("FRAMES")
    if only:
        for n in map(int, only.split(",")):
            frame(n).save(f"{D}/f{n:03d}.jpg", quality=90)
        return
    out = f"{D}/embrya_maternity_leggings_ad.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-maxrate", "14M", "-bufsize", "28M",
                          "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for n in range(NF):
        p.stdin.write(frame(n).tobytes())
    p.stdin.close(); p.wait()
    for k_, s in enumerate(SEG):
        print(f"{starts[k_]:6.2f}s  dur {s[1]:.2f}  -> {getattr(s[2], '__name__', s[2])}")


if __name__ == "__main__":
    main()
