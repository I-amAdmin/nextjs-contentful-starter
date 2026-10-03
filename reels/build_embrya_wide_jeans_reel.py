"""Embrya maternity-jeans reel: 25s, 1080x1920, 30fps, rendered frame-by-frame and piped to ffmpeg."""
import os, math, subprocess, random
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
CREAM = (244, 237, 230)
GOLD = (222, 164, 72)
INDIGO = (28, 44, 82)
rng = np.random.default_rng(7)

ease_out = lambda p: 1 - (1 - min(1, max(0, p))) ** 3
ease_io = lambda p: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, p)))


# ---------- assets ----------
def denim_texture(w, h):
    """procedural indigo twill: diagonal weave + slub noise + light fading"""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    twill = 0.5 + 0.5 * np.sin((x + y * 0.55) * 2 * math.pi / 7.0)
    slub = np.repeat(rng.normal(0, 1, (h // 3 + 1, 1)), 3, axis=0)[:h] * np.ones((1, w))
    noise = rng.normal(0, 1, (h, w))
    fade = np.exp(-(((x - w * .55) / (w * .6)) ** 2 + ((y - h * .45) / (h * .5)) ** 2))
    v = 0.55 * twill + 0.12 * slub + 0.10 * noise + 0.35 * fade
    v = (v - v.min()) / (v.max() - v.min())
    base = np.array(INDIGO, np.float32); light = np.array((92, 120, 168), np.float32)
    rgb = base + (light - base) * v[..., None]
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))


DENIM = denim_texture(W, H)


def stitch_line(draw, x0, y0, x1, y1, p=1.0, color=GOLD, width=5, dash=26, gap=16):
    L = math.hypot(x1 - x0, y1 - y0) * p
    ux, uy = (x1 - x0) / math.hypot(x1 - x0, y1 - y0), (y1 - y0) / math.hypot(x1 - x0, y1 - y0)
    s = 0.0
    while s < L:
        e = min(s + dash, L)
        draw.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=color, width=width)
        s += dash + gap


def patch(lines, angle=-4):
    """leather jeans-label patch with stitched border; lines=[(text, font)]"""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    sizes = [tmp.textbbox((0, 0), t, font=f) for t, f in lines]
    tw = max(b[2] - b[0] for b in sizes); th = sum(b[3] - b[1] for b in sizes) + 22 * (len(lines) - 1)
    pw, ph = tw + 120, th + 90
    im = Image.new("RGBA", (pw + 60, ph + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((34, 40, 34 + pw, 40 + ph), 22, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    # leather fill with grain
    leather = np.zeros((ph, pw, 3), np.float32) + np.array((176, 122, 78), np.float32)
    leather += rng.normal(0, 7, (ph, pw, 1))
    yy = np.linspace(0, 1, ph)[:, None, None]
    leather *= (1.06 - 0.16 * yy)
    lim = Image.fromarray(np.clip(leather, 0, 255).astype(np.uint8)).convert("RGBA")
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), 22, fill=255)
    lim.putalpha(mask)
    im.alpha_composite(lim, (30, 30))
    d = ImageDraw.Draw(im)
    o, r = 30 + 16, 30 + 16
    for (a, b, c, e) in [(o, r, 30 + pw - 16, r), (30 + pw - 16, r, 30 + pw - 16, 30 + ph - 16),
                         (30 + pw - 16, 30 + ph - 16, o, 30 + ph - 16), (o, 30 + ph - 16, o, r)]:
        stitch_line(d, a, b, c, e, color=(246, 214, 160), width=3, dash=14, gap=9)
    y = 30 + 45
    for (t, f), bb in zip(lines, sizes):
        x = 30 + (pw - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x + 2, y - bb[1] + 2), t, font=f, fill=(92, 52, 26, 200))   # debossed edge
        d.text((x, y - bb[1]), t, font=f, fill=(58, 30, 14, 255))
        y += bb[3] - bb[1] + 22
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)


def load_shot(name, cx=0.5, aspect=9 / 16, scale=2):
    src = Image.open(f"{IMG}/{name}").convert("RGB")
    cw = int(src.height * aspect)
    x0 = int((src.width - cw) * cx)
    c = src.crop((x0, 0, x0 + cw, src.height))
    tw = int(W * scale * (aspect / (9 / 16))) if aspect < 9 / 16 else W * scale
    return c.resize((tw, H * scale), Image.LANCZOS)


def grade(im):
    a = np.asarray(im).astype(np.float32) / 255
    a = (a - 0.5) * 1.06 + 0.5                       # contrast
    lum = a.mean(axis=2, keepdims=True)
    shadow = np.clip(1 - lum * 2.2, 0, 1)
    a += shadow * np.array([-0.012, 0.0, 0.03])      # cool indigo shadows, highlights untouched
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


# ---------- shot renderers (return RGB W x H for local time t, duration d) ----------
def kb(img, t, d, z0, z1, pan=(0, 0), punch=False):
    p = ease_io(t / d)
    z = z0 + (z1 - z0) * p
    if punch:
        z *= 1 + 0.10 * (1 - ease_out(t / 0.35))
    iw, ih = img.size
    cw, ch = iw / z, ih / z
    x = (iw - cw) / 2 + pan[0] * (iw - cw) / 2 * (2 * p - 1)
    y = (ih - ch) / 2 + pan[1] * (ih - ch) / 2 * (2 * p - 1)
    return img.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))


def single(name, cx=0.5, z=(1.0, 1.07), pan=(0, 0), punch=True, cap=None, cap_at=0.25, cap_pos=(0.5, 0.80)):
    img = grade(load_shot(name, cx))
    def r(t, d):
        fr = kb(img, t, d, z[0], z[1], pan, punch)
        if cap is not None:
            put_patch(fr, cap, t - cap_at, d - cap_at, cap_pos)
        return fr
    return r


def detail(name, box, z=(1.0, 1.08), pan=(0, 0), cap=None, cap_at=0.25, cap_pos=(0.5, 0.80)):
    """macro insert cut from a region of the photo; box=(x0, y0, width) in source px, height follows 9:16"""
    src = Image.open(f"{IMG}/{name}").convert("RGB")
    x0, y0, cw = box; ch = cw * 16 / 9
    img = src.resize((W * 2, H * 2), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    img = grade(img.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2)))
    def r(t, d):
        fr = kb(img, t, d, z[0], z[1], pan, True)
        if cap is not None:
            put_patch(fr, cap, t - cap_at, d - cap_at, cap_pos)
        return fr
    return r


def recap():
    """the product page's own line, word-patches stamping in on the beat"""
    head = HE(500, 64)
    items = [patch([(w, HE(800, 96))], angle=a) for w, a in (("לעבודה", -4), ("ליום יום", 3), ("ליציאה", -2))]
    def r(t, d):
        fr = DENIM.copy(); dr = ImageDraw.Draw(fr)
        for y in (250, 280):
            stitch_line(dr, -10, y, W + 10, y, p=ease_out(t / 0.6), width=5)
        s_ = "זה הג׳ינס שתלבשי"
        bb = dr.textbbox((0, 0), s_, font=head)
        k = ease_out(t / 0.4)
        dr.text(((W - (bb[2] - bb[0])) // 2 - bb[0], 470 - bb[1] + int(20 * (1 - k))), s_, font=head, fill=(250, 244, 236))
        for i, pm in enumerate(items):
            q = min(1, max(0, (t - 0.35 - 0.38 * i) / 0.3))
            if q <= 0:
                continue
            sc = 1 + 0.4 * (1 - q) ** 2
            im = pm.resize((int(pm.width * sc), int(pm.height * sc)), Image.BICUBIC)
            im.putalpha(im.getchannel("A").point(lambda v, k=min(1, q * 2): int(v * k)))
            fr.paste(im, ((W - im.width) // 2, 700 + i * 300 - im.height // 2 + 60), im)
        return fr
    return r


def split(a, b, cap=None, cap_pos=(0.5, 0.82)):
    A = grade(load_shot(a, 0.5, aspect=0.28125)); B = grade(load_shot(b, 0.5, aspect=0.28125))
    def r(t, d):
        fr = Image.new("RGB", (W, H), (245, 245, 245))
        p = ease_out(t / 0.55)
        hw = W // 2 - 4
        za = kb(A, t, d, 1.0, 1.06).resize((hw, H)) if False else A.resize((hw, H), Image.BILINEAR)
        zb = B.resize((hw, H), Image.BILINEAR)
        drift = int(40 * ease_io(t / d))
        fr.paste(za, (0, int(-H * (1 - p)) - drift + 20))
        fr.paste(zb, (W - hw, int(H * (1 - p)) + drift - 20))
        dr = ImageDraw.Draw(fr)
        stitch_line(dr, W / 2, 0, W / 2, H, p=p, width=4)
        if cap is not None:
            put_patch(fr, cap, t - 0.35, d - 0.35, cap_pos)
        return fr
    return r


def intro():
    title = patch([("ג׳ינס הריון רחב", HE(800, 112)), ("WIDE LEG MATERNITY DENIM", LA(700, 40))], angle=-3)
    def r(t, d):
        fr = DENIM.copy()
        dr = ImageDraw.Draw(fr)
        # double contrast stitching draws in, like a jeans seam
        p = ease_out(t / 0.9)
        for y in (300, 330):
            stitch_line(dr, -10, y, W + 10, y, p=p, width=5)
        for y in (H - 330, H - 300):
            stitch_line(dr, W + 10, y, -10, y, p=p, width=5)
        # rivets
        if t > 0.6:
            for (x, y) in [(120, 315), (W - 120, 315), (120, H - 315), (W - 120, H - 315)]:
                dr.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(190, 150, 90)); dr.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(120, 88, 48))
        # patch stamps in (scale 1.35 -> 1.0 with overshoot)
        q = min(1, max(0, (t - 0.35) / 0.45))
        if q > 0:
            s = 1 + 0.35 * (1 - q) ** 2 - 0.05 * math.sin(q * math.pi)
            pm = title.resize((int(title.width * s), int(title.height * s)), Image.BICUBIC)
            a = pm.getchannel("A").point(lambda v: int(v * min(1, q * 2))); pm.putalpha(a)
            fr.paste(pm, ((W - pm.width) // 2, (H - pm.height) // 2), pm)
        return fr
    return r


def endcard():
    bg = Image.new("RGB", (W, H), CREAM)
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((W / 2 - 700, 60, W / 2 + 700, 1460), fill=110)
    bg = Image.composite(Image.new("RGB", (W, H), (226, 220, 214)), bg, glow.filter(ImageFilter.GaussianBlur(180)))
    lg = Image.open(LOGO).convert("RGBA"); lw = 820; lh = round(lg.height * lw / lg.width)
    a = lg.getchannel("A").resize((lw, lh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))
    logo = Image.new("RGBA", (lw, lh), (35, 28, 26, 0)); logo.putalpha(a)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tx)
    for s, f, c, y in [("ג׳ינס הריון רחב", HE(500, 70), INDIGO, 1120), ("embrya.co.il", LA(300, 50), (90, 62, 50), 1330)]:
        bb = d.textbbox((0, 0), s, font=f); d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), s, font=f, fill=c + (255,))

    def r(t, d_):
        fr = bg.copy().convert("RGBA")
        p1 = ease_out(t / 1.3); sc = 1.12 - 0.12 * p1
        l = logo.resize((round(lw * sc), round(lh * sc)), Image.LANCZOS)
        if p1 < 1:
            l = l.filter(ImageFilter.GaussianBlur(14 * (1 - p1)))
        l.putalpha(l.getchannel("A").point(lambda v, k=min(1, t / 0.9): int(v * k)))
        fr.alpha_composite(l, ((W - l.width) // 2, 840 - l.height // 2))
        dr = ImageDraw.Draw(fr)
        stitch_line(dr, W / 2 - 150, 1265, W / 2 + 150, 1265, p=ease_out((t - 0.9) / 0.7), color=GOLD, width=4, dash=16, gap=10)
        p2 = ease_out((t - 1.1) / 0.8)
        if p2 > 0:
            tt = tx.copy(); tt.putalpha(tx.getchannel("A").point(lambda v, k=p2: int(v * k)))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(tt, (0, round(24 * (1 - p2))))
            fr.alpha_composite(lay)
        return fr.convert("RGB")
    return r


_patch_cache = {}


def put_patch(fr, cap, t, d, pos):
    if t <= 0:
        return
    key = tuple(cap)
    if key not in _patch_cache:
        lines = [(s, HE(800, 92) if kind == "he" else LA(800, 104)) if i == 0 else
                 (s, HE(500, 50) if kind == "he" else LA(500, 50)) for i, (s, kind) in enumerate(cap)]
        _patch_cache[key] = patch(lines, angle=-5)
    pm = _patch_cache[key]
    q = ease_out(t / 0.3)
    out = 1 - ease_out((t - (d - 0.25)) / 0.25) if t > d - 0.25 else 1
    s = (1.3 - 0.3 * q)
    p = pm.resize((max(1, int(pm.width * s)), max(1, int(pm.height * s))), Image.BICUBIC)
    p.putalpha(p.getchannel("A").point(lambda v, k=min(q * 1.5, 1) * out: int(v * k)))
    fr.paste(p, (int(W * pos[0] - p.width / 2), int(H * pos[1] - p.height / 2)), p)


# ---------- transitions: f(a_img, b_img, p) ----------
def whip(direction=1):
    def f(a, b, p):
        e = ease_io(p); off = int(W * e) * direction
        fr = Image.new("RGB", (W, H))
        fr.paste(a, (-off, 0)); fr.paste(b, (W * direction - off, 0))
        k = 1 + int(28 * math.sin(math.pi * p))          # motion blur peaks mid-whip
        return fr.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR) if k > 1 else fr
    return f


def whip_v(direction=1):
    def f(a, b, p):
        e = ease_io(p); off = int(H * e) * direction
        fr = Image.new("RGB", (W, H))
        fr.paste(a, (0, -off)); fr.paste(b, (0, H * direction - off))
        k = 1 + int(28 * math.sin(math.pi * p))
        return fr.resize((W, max(1, H // k)), Image.BILINEAR).resize((W, H), Image.BILINEAR) if k > 1 else fr
    return f


TEAR = np.cumsum(rng.normal(0, 9, W)); TEAR -= np.linspace(TEAR[0], TEAR[-1], W)
TEAR += 22 * np.sin(np.linspace(0, 9, W))


def tear(a, b, p):
    """denim rips upward: jagged edge with frayed white threads reveals b"""
    e = ease_io(p)
    yline = H * (1 - e) * 1.15 - 80
    ys = np.arange(H)[:, None]
    edge = yline + TEAR[None, :]
    m = (ys > edge).astype(np.uint8) * 255
    fray = ((ys > edge - 26) & (ys <= edge)).astype(np.float32)
    fray *= (rng.random((H, W)) > 0.45)
    A = np.asarray(a).astype(np.float32); B = np.asarray(b).astype(np.float32)
    out = np.where(m[..., None] > 0, B, A)
    out = out * (1 - fray[..., None] * 0.85) + np.array((236, 236, 240)) * fray[..., None] * 0.85
    return Image.fromarray(out.astype(np.uint8))


def denim_wipe(a, b, p):
    """denim panel with seam slides over a, then off revealing b"""
    x = int(W * (1.15 - 2.3 * ease_io(p)))
    base = a if p < 0.5 else b
    fr = base.copy()
    fr.paste(DENIM, (x - W // 2 + 0, 0)) if False else fr.paste(DENIM.crop((0, 0, W, H)), (x - W, 0))
    dr = ImageDraw.Draw(fr)
    for dx in (-60, -30):
        stitch_line(dr, x + dx, 0, x + dx, H, width=5)
    return fr


def flash(a, b, p):
    w = max(0, 1 - abs(p - 0.5) * 4)
    base = a if p < 0.5 else b
    return Image.blend(base, Image.new("RGB", (W, H), (255, 255, 255)), w * 0.85)


def cut(a, b, p):
    return b


# ---------- timeline ----------
he, la = "he", "la"
A, B, C = "IMG_3280.jpg", "IMG_3278.jpg", "IMG_3279.jpg"   # front, side, back
SEG = [  # (renderer, duration, transition-into-next, transition duration)
    (intro(), 2.0, tear, 0.55),
    (single(A, z=(1.0, 1.07)), 1.7, whip(1), 0.30),
    (detail(A, (180, 0, 460), z=(1.0, 1.1), cap=[("חגורת בטן", he), ("מלווה אותך בכל שלבי ההריון", he)], cap_pos=(0.5, 0.82)), 2.3, flash, 0.20),
    (single(B, cx=0.55, z=(1.06, 1.0), cap=[("בד סטרצי רך", he), ("מתאים את עצמו לבטן המשתנה", he)], cap_pos=(0.5, 0.18)), 2.4, whip_v(1), 0.30),
    (detail(B, (150, 290, 440), z=(1.0, 1.08), pan=(0, 0.6), cap=[("גזרה רחבה", he), ("לוק מאוזן ומחמיא", he)], cap_pos=(0.32, 0.20)), 2.2, denim_wipe, 0.55),
    (single(C, cx=0.6, z=(1.0, 1.07), cap=[("חופש תנועה", he), ("לאורך כל היום", he)], cap_pos=(0.32, 0.84)), 2.2, whip(-1), 0.30),
    (detail(C, (240, 60, 400), z=(1.0, 1.08), cap=[("גוון ג׳ינס קלאסי", he), ("משתלב עם כל חולצה", he)], cap_pos=(0.5, 0.82)), 2.2, cut, 0.0),
    (single(A, z=(1.15, 1.2)), 0.27, cut, 0.0),
    (single(B, z=(1.15, 1.2)), 0.27, cut, 0.0),
    (single(C, z=(1.15, 1.2)), 0.75, tear, 0.45),
    (recap(), 1.9, denim_wipe, 0.55),
    (endcard(), None, None, 0),
]

# stretch shots (not the 0.27s beat-drop cuts) so the end card gets END seconds and total is exactly TOTAL
END = 4.2
fixed = sum(s[1] for s in SEG[:-1] if s[1] < 0.5) - sum(s[3] for s in SEG[:-1])
flex = sum(s[1] for s in SEG[:-1] if s[1] >= 0.5)
k = (TOTAL - END - fixed) / flex
SEG = [(r, d * k if d >= 0.5 else d, tr, td) for r, d, tr, td in SEG[:-1]] + [(SEG[-1][0], END, None, 0)]

assert all(s[3] < s[1] for s in SEG[:-1]), 'transition longer than its shot'
starts, t0 = [], 0.0
for s in SEG:
    starts.append(t0); t0 += s[1] - s[3]

GRAIN = [Image.fromarray(np.clip(rng.normal(128, 9, (H // 2, W // 2)), 0, 255).astype(np.uint8)).resize((W, H)).convert("RGB") for _ in range(6)]
VIG = Image.new("L", (W, H), 0); ImageDraw.Draw(VIG).ellipse((-260, -200, W + 260, H + 200), fill=255)
VIG = VIG.filter(ImageFilter.GaussianBlur(220)).point(lambda v: int(255 - (255 - v) * 0.45))


def frame(n):
    t = n / FPS
    i = max(k for k in range(len(SEG)) if starts[k] <= t + 1e-9)
    if i > 0 and t < starts[i - 1] + SEG[i - 1][1]:  # still inside previous shot's outgoing transition
        i -= 1
    r, d, tr, td = SEG[i]
    cur = r(t - starts[i], d)
    # inside the outgoing transition window of segment i?
    if tr is not None and td > 0 and t >= starts[i] + d - td and i + 1 < len(SEG):
        p = (t - (starts[i] + d - td)) / td
        nxt = SEG[i + 1][0](t - starts[i + 1], SEG[i + 1][1])
        cur = tr(cur, nxt, p)
    # finishing: subtle grain + vignette (lighter on the end card)
    g = GRAIN[n % len(GRAIN)]
    cur = ImageChops.overlay(cur, g) if t < starts[-1] + 0.6 else cur
    return Image.composite(cur, Image.new("RGB", (W, H), (0, 0, 0)), VIG)


def main():
    out = os.environ.get("OUT", f"{D}/embrya_wide_maternity_jeans_reel.mp4")
    only = os.environ.get("FRAMES")
    if only:
        for n in map(int, only.split(",")):
            frame(n).save(f"{D}/f{n:03d}.jpg", quality=90)
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-maxrate", "16M", "-bufsize", "32M",
                          "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE)
    for n in range(NF):
        p.stdin.write(frame(n).tobytes())
    p.stdin.close(); p.wait()
    for k, s in enumerate(SEG):
        print(f"{starts[k]:6.2f}s  dur {s[1]:.2f}  -> {getattr(s[2], '__name__', s[2])}")


if __name__ == "__main__":
    main()
