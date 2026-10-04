"""Embrya maternity-leggings ad — landscape 16:9 (1920x1080) cut for Google Ads / YouTube.
Same story, captions and images as the vertical Meta reel, re-laid out for a wide frame:
portrait photo panels beside a cream type panel, a 4-column beat sequence, and the brand on screen early."""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

D = os.path.dirname(os.path.abspath(__file__))
IMG = f"{D}/img"
FD = f"{D}/../fonts/fontsource-heebo-5.3.0/package/files"
LOGO = f"{D}/../img/logo.png"
W, H, FPS, TOTAL = 1920, 1080, 30, 20.0
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
                                       "IMG_2422", "IMG_1658", "IMG_1786", "IMG_1767", "IMG_1604", "navy", "light-grey",
                                       "legging1", "רכיבה1"]}
N["brown_straight"] = "טייץ-ישר-חום-קטן-720x960.jpg"
N["brown_biker"] = "brown_biker_user.jpg"


def grade(im):
    a = np.asarray(im).astype(np.float32) / 255
    a = a * 0.96 + 0.035
    a = (a - 0.5) * 1.03 + 0.5
    a *= np.array([1.02, 1.0, 0.975])
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


_cache = {}


def panel_src(name, pw, ph, cx=0.5, box=None):
    """photo cropped to the panel aspect, at 1.5x for smooth zooms"""
    key = (name, pw, ph, cx, box)
    if key not in _cache:
        src = Image.open(f"{IMG}/{N.get(name, name)}").convert("RGB")
        asp = pw / ph
        if box:
            x0, y0, cw = box; ch = cw / asp
        else:
            ch = src.height; cw = ch * asp
            if cw > src.width:
                cw = src.width; ch = cw / asp
            x0 = (src.width - cw) * cx; y0 = (src.height - ch) * 0.3
        im = src.resize((int(pw * 1.5), int(ph * 1.5)), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
        if box:
            im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
        _cache[key] = grade(im)
    return _cache[key]


def kb(img, t, d, z0, z1, size, punch=True):
    p = ease_io(t / d)
    z = z0 + (z1 - z0) * p
    if punch:
        z *= 1 + 0.06 * (1 - ease_out(t / 0.4))
    iw, ih = img.size; cw, ch = iw / z, ih / z
    return img.resize(size, Image.BILINEAR, box=((iw - cw) / 2, (ih - ch) / 2, (iw + cw) / 2, (ih + ch) / 2))


def text_w(s, f):
    b = ImageDraw.Draw(Image.new("L", (4, 4))).textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def fit_font(s, w, size, maxw):
    while text_w(s, HE(w, size)) > maxw and size > 30:
        size -= 2
    return HE(w, size)


_lg = None


def logo_img(width):
    global _lg
    if _lg is None:
        _lg = Image.open(LOGO).convert("RGBA")
    lh = round(_lg.height * width / _lg.width)
    a = _lg.getchannel("A").resize((width, lh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.0 if width > 400 else 0.6))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))
    out = Image.new("RGBA", (width, lh), (35, 28, 26, 0)); out.putalpha(a)
    return out


BUG = logo_img(230)


def type_block(fr, x0, x1, head, sub, t, y_mid=540, bug=True):
    """right-aligned Hebrew headline + subline with elastic slide-in; brand bug in the panel corner"""
    d = ImageDraw.Draw(fr)
    maxw = x1 - x0 - 200
    fh = fit_font(head, 800, 112, maxw)
    fs = fit_font(sub, 400, 62, maxw) if sub else None
    right = x1 - 110
    hb = d.textbbox((0, 0), head, font=fh)
    hh = hb[3] - hb[1]
    sh = (d.textbbox((0, 0), sub, font=fs)[3] - d.textbbox((0, 0), sub, font=fs)[1]) if sub else 0
    y = y_mid - (hh + (40 + sh if sub else 0)) // 2
    q = elastic(t / 0.6); a = clamp(t / 0.2)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    off = int(70 * (1 - q))
    ld.text((right - (hb[2] - hb[0]) - hb[0] + off, y - hb[1]), head, font=fh, fill=INK + (int(255 * a),))
    # blush accent bar grows from the right
    bw = int(150 * ease_out((t - 0.15) / 0.5))
    if bw > 0:
        ld.rounded_rectangle((right - bw, y + hh + 16, right, y + hh + 24), 4, fill=BLUSH + (255,))
    if sub:
        a2 = clamp((t - 0.25) / 0.3); q2 = ease_out((t - 0.25) / 0.5)
        sb = ld.textbbox((0, 0), sub, font=fs)
        ld.text((right - (sb[2] - sb[0]) - sb[0], y + hh + 52 - sb[1] + int(20 * (1 - q2))), sub, font=fs, fill=(96, 72, 64, int(255 * a2)))
    if bug:
        lay.alpha_composite(BUG, (x1 - 60 - BUG.width, 60))
    fr.paste(lay, (0, 0), lay)


def bg_cream():
    bg = Image.new("RGB", (W, H), CREAM)
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((W * .35, -300, W * 1.2, H + 300), fill=120)
    return Image.composite(Image.new("RGB", (W, H), (240, 224, 213)), bg, glow.filter(ImageFilter.GaussianBlur(200)))


BG = bg_cream()


# ---------- segments ----------
def feature(name, head, sub, side="left", cx=0.5, box=None, z=(1.0, 1.07)):
    PW = 700
    img = panel_src(name, PW, H, cx, box)
    def r(t, d):
        fr = BG.copy()
        ph = kb(img, t, d, z[0], z[1], (PW, H))
        px = 0 if side == "left" else W - PW
        slide = int((PW + 40) * (1 - ease_out(t / 0.45))) * (-1 if side == "left" else 1)
        fr.paste(ph, (px + slide, 0))
        tx0, tx1 = (PW, W) if side == "left" else (0, W - PW)
        type_block(fr, tx0, tx1, head, sub, t - 0.15)
        return fr
    return r


def hook():
    names = ["ZOE_NOIR-SF411_LG411_8small", "IMG_1786", "LIBERTY5", "navy", "LIBERTY4", "brown_biker",
             "ZOE_TERRACOTTA-SF411_04small", "IMG_2422", "brown_straight", "IMG_1767", "light-grey", "IMG_1604"]
    cols, rows = 6, 2
    tw, th = W // cols, H // rows
    tiles = [panel_src(n, tw, th) for n in names]
    head = "הטייץ שגדל איתך"
    fh = HE(800, 150)
    def r(t, d):
        fr = Image.new("RGB", (W, H), CREAM)
        for i, tl in enumerate(tiles):
            q = elastic((t - 0.05 * i) / 0.45)
            if q <= 0:
                continue
            w_, h_ = max(2, int((tw - 10) * q)), max(2, int((th - 10) * q))
            c = (cols - 1 - i % cols) * tw + tw // 2; rr = (i // cols) * th + th // 2   # fill right-to-left
            fr.paste(kb(tl, t, d, 1.0, 1.08, (w_, h_), punch=False), (c - w_ // 2, rr - h_ // 2))
        # cream veil + rubber-band headline
        v = ease_out((t - 0.75) / 0.4)
        if v > 0:
            veil = Image.new("RGB", (W, H), CREAM)
            fr = Image.blend(fr, veil, 0.62 * v)
            q = elastic((t - 0.8) / 0.6)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            b = ld.textbbox((0, 0), head, font=fh)
            ld.text(((W - (b[2] - b[0])) // 2 - b[0], (H - (b[3] - b[1])) // 2 - b[1] - 40), head, font=fh, fill=INK + (255,))
            sx = max(0.05, 0.35 + 0.65 * q + 0.22 * math.sin(clamp((t - 0.8) / 0.5) * math.pi) * (1 - clamp((t - 0.8) / 0.5)))
            sy = max(0.05, 0.6 + 0.4 * q)
            lay = lay.resize((max(1, int(W * sx)), max(1, int(H * sy))), Image.BICUBIC)
            lay.putalpha(lay.getchannel("A").point(lambda a_, k=clamp((t - 0.8) / 0.15): int(a_ * k)))
            fr.paste(lay, ((W - lay.width) // 2, (H - lay.height) // 2), lay)
            # brand within the first seconds
            lb = logo_img(300); la = clamp((t - 1.2) / 0.4)
            lb.putalpha(lb.getchannel("A").point(lambda a_, k=la: int(a_ * k)))
            fr.paste(lb, ((W - lb.width) // 2, 700), lb)
        return fr
    return r


def beats(items):
    """'לעבודה / ליומיום / לספורט / ולבית' — a column drops in per beat, right to left, and stays"""
    n = len(items); cw = W // n
    cols = [(panel_src(nm, cw, H), w) for w, nm in items]
    f = HE(800, 76)
    def r(t, d):
        fr = Image.new("RGB", (W, H), CREAM)
        step = d / n
        for k, (img, word) in enumerate(cols):
            lt = t - k * step
            if lt <= 0:
                continue
            x = W - (k + 1) * cw
            q = elastic(lt / 0.5)
            y = int(-H * (1 - q))
            ph = kb(img, lt, d - k * step, 1.10, 1.0, (cw - 8, H), punch=True)
            fr.paste(ph, (x + 4, y))
            # word pill at the lower third of its column
            dr = ImageDraw.Draw(fr)
            b = dr.textbbox((0, 0), word, font=f); pw = b[2] - b[0] + 80; phh = b[3] - b[1] + 50
            px = x + (cw - pw) // 2; py = 760 + y
            dr.rounded_rectangle((px, py, px + pw, py + phh), phh // 2, fill=(255, 255, 255))
            dr.text((px + 40 - b[0], py + 25 - b[1]), word, font=f, fill=INK)
        return fr
    return r


def duo(a, b, head, sub):
    PW = 520
    A = panel_src(a, PW, H); B = panel_src(b, PW, H)
    def r(t, d):
        fr = BG.copy()
        p = ease_out(t / 0.45); drift = int(24 * ease_io(t / d))
        fr.paste(kb(A, t, d, 1.0, 1.05, (PW - 6, H), False), (0, int(-H * (1 - p)) - drift + 12))
        fr.paste(kb(B, t, d, 1.05, 1.0, (PW - 6, H), False), (PW + 6, int(H * (1 - p)) + drift - 12))
        type_block(fr, 2 * PW, W, head, sub, t - 0.3)
        return fr
    return r


def strip(names, head, sub):
    PW = 420
    imgs = [panel_src(nm, PW, H) for nm in names]
    def r(t, d):
        fr = BG.copy()
        k = int(t / 0.32)
        for c in range(2):   # two panels on the left cycle through prints/colours, offset in phase
            im = imgs[(k + c * 3) % len(imgs)]
            fr.paste(kb(im, t % 0.32, 0.32, 1.06, 1.1, (PW - 6, H), True), (c * PW, 0))
        type_block(fr, 2 * PW, W, head, sub, t - 0.1)
        return fr
    return r


def endcard():
    logo = logo_img(760)
    f1, f2 = HE(500, 70), LA(300, 48)
    cta_f = HE(700, 58)
    def r(t, d):
        fr = BG.copy().convert("RGBA")
        p1 = ease_out(t / 1.1); sc = 1.1 - 0.1 * p1
        l = logo.resize((round(logo.width * sc), round(logo.height * sc)), Image.LANCZOS)
        if p1 < 1:
            l = l.filter(ImageFilter.GaussianBlur(12 * (1 - p1)))
        l.putalpha(l.getchannel("A").point(lambda v, k=min(1, t / 0.7): int(v * k)))
        fr.alpha_composite(l, ((W - l.width) // 2, 330 - l.height // 2))
        dr = ImageDraw.Draw(fr)
        p2 = ease_out((t - 0.8) / 0.6)
        if p2 > 0:
            for s, f, c, y in [("טייצים להריון", f1, INK, 540), ("embrya.co.il", f2, (110, 80, 66), 630)]:
                b = dr.textbbox((0, 0), s, font=f)
                dr.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1] + int(18 * (1 - p2))), s, font=f, fill=c + (int(255 * p2),))
        if t > 1.3:
            ct = t - 1.3
            s = elastic(ct / 0.5) if ct < 0.6 else 1 + 0.03 * math.sin((ct - 0.6) * 2 * math.pi / 1.1)
            word = "לכל הדגמים באתר"
            b = dr.textbbox((0, 0), word, font=cta_f); pw, ph = b[2] - b[0] + 120, b[3] - b[1] + 60
            pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
            pd.rounded_rectangle((0, 0, pw - 1, ph - 1), ph // 2, fill=BLUSH + (255,))
            pd.text((60 - b[0], 30 - b[1]), word, font=cta_f, fill=(255, 255, 255))
            pill = pill.resize((max(1, int(pw * s)), max(1, int(ph * s))), Image.BICUBIC)
            fr.alpha_composite(pill, ((W - pill.width) // 2, 790 - pill.height // 2))
        return fr.convert("RGB")
    return r


# ---------- transitions ----------
def rubber(a, b, p):
    q = elastic(p)
    sa = max(0.02, 1 - ease_out(p * 1.4))
    fr = Image.new("RGB", (W, H), CREAM)
    if sa > 0.03:
        sq = a.resize((max(2, int(W * sa)), H), Image.BILINEAR); fr.paste(sq, ((W - sq.width) // 2, 0))
    w = max(2, int(W * q))
    bb = b.resize((w, H), Image.BILINEAR)
    if w > W:
        bb = bb.crop(((w - W) // 2, 0, (w - W) // 2 + W, H))
    fr.paste(bb, ((W - bb.width) // 2, 0))
    return fr


def whip(direction=1):
    def f(a, b, p):
        e = ease_io(p); off = int(W * e) * direction
        fr = Image.new("RGB", (W, H)); fr.paste(a, (-off, 0)); fr.paste(b, (W * direction - off, 0))
        k = 1 + int(30 * math.sin(math.pi * p))
        return fr.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR) if k > 1 else fr
    return f


def soft_flash(a, b, p):
    w = max(0, 1 - abs(p - 0.5) * 2.6)
    return Image.blend(a if p < 0.5 else b, Image.new("RGB", (W, H), (255, 244, 236)), w * 0.9)


def cut(a, b, p):
    return b


# ---------- timeline (captions identical to the vertical reel; all sourced from the product pages) ----------
SEG = [
    (hook(), 2.4, rubber, 0.45),
    (feature("LIBERTY4", "חגורת בטן נוחה", "שמתאימה את עצמה לגוף לאורך כל ההריון", "left"), 2.4, whip(-1), 0.30),
    (feature("ZOE_NOIR-SF411_LG411_8small", "חופש תנועה מלא", "ונוחות לאורך כל היום", "right", cx=0.45), 2.2, rubber, 0.45),
    (feature("ZOE_TERRACOTTA-SF411_04small", "רך במיוחד", "מחבק בעדינות את הבטן", "left", z=(1.07, 1.0)), 2.2, whip(1), 0.30),
    (feature("IMG_1658", "התפרים עוברים מתחת לבטן", "ולא לוחצים", "right", box=(150, 0, 420), z=(1.0, 1.1)), 2.2, soft_flash, 0.25),
    (beats([("לעבודה", "navy"), ("ליומיום", "IMG_1786"), ("לספורט", "brown_biker"), ("ולבית", "LIBERTY5")]), 2.6, rubber, 0.45),
    (duo("ZOE_NOIR-SF411_LG411_8small", "ZOE_TERRACOTTA-SF411_04small", "מתאים לאורך כל ההיריון", "וגם אחריו"), 2.4, whip(-1), 0.30),
    (strip(["IMG_2422", "light-grey", "IMG_1767", "legging1", "IMG_1604", "brown_straight"], "מגוון גזרות", "אורכים והדפסים"), 2.0, rubber, 0.45),
    (endcard(), None, None, 0),
]
END = 4.0
fixed = -sum(s[3] for s in SEG[:-1]); flex = sum(s[1] for s in SEG[:-1])
k = (TOTAL - END - fixed) / flex
SEG = [(r, d * k, tr, td) for r, d, tr, td in SEG[:-1]] + [(SEG[-1][0], END, None, 0)]
assert all(s[3] < s[1] for s in SEG[:-1])
starts, t0 = [], 0.0
for s in SEG:
    starts.append(t0); t0 += s[1] - s[3]

GRAIN = [Image.fromarray(np.clip(rng.normal(128, 6, (H // 2, W // 2)), 0, 255).astype(np.uint8)).resize((W, H)).convert("RGB") for _ in range(6)]
VIG = Image.new("L", (W, H), 0); ImageDraw.Draw(VIG).ellipse((-300, -260, W + 300, H + 260), fill=255)
VIG = VIG.filter(ImageFilter.GaussianBlur(200)).point(lambda v: int(255 - (255 - v) * 0.3))
LEAK = Image.new("RGB", (W, H), (0, 0, 0)); ld = ImageDraw.Draw(LEAK)
ld.ellipse((-300, -200, 800, 700), fill=(255, 178, 140)); ld.ellipse((1200, 500, 2200, 1400), fill=(255, 205, 170))
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
    lk = max([0.0] + [0.30 * max(0, 1 - abs(t - s) / 0.45) for s in starts[1:]])
    if lk > 0:
        cur = Image.blend(cur, ImageChops.screen(cur, LEAK), lk)
    if t < starts[-1] + 0.3:
        cur = ImageChops.overlay(cur, GRAIN[n % len(GRAIN)])
    return Image.composite(cur, Image.new("RGB", (W, H), (20, 12, 10)), VIG)


def main():
    only = os.environ.get("FRAMES")
    if only:
        for n in map(int, only.split(",")):
            frame(n).save(f"{D}/w{n:03d}.jpg", quality=90)
        return
    out = f"{D}/embrya_maternity_leggings_ad_16x9.mp4"
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
