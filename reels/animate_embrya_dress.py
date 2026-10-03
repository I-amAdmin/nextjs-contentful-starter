"""2.5D animation of a single product photo: parallax push-in, breathing, light sheen, bokeh.
Inputs: 13-scaled.jpg (photo), cut13.png (subject cutout), bg13.png (inpainted clean plate)."""
import os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
FD = f"{D}/../fonts/fontsource-heebo-5.3.0/package/files"
W, H, FPS, T = 1080, 1920, 30, 8.0
NF = int(T * FPS)
TITLE = os.environ.get("TITLE") == "1"
rng = np.random.default_rng(3)
ease = lambda p: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, p)))
eout = lambda p: 1 - (1 - min(1, max(0, p))) ** 3

bg = Image.open(f"{D}/bg13_ext.png").convert("RGB")
PADL, PADT = 420, 160            # padding added around the photo in bg13_ext.png
subj = Image.open(f"{D}/cut13_clean.png").convert("RGBA")
SW, SH = subj.size
S0 = 1.42                             # base scale: subject ~1390px tall, room for title below
CX_SRC, FEET_SRC = 330, 1035          # subject centre-x and feet line in source px
OX = W / 2 - CX_SRC * S0              # put subject on the vertical centre line
OY = 1490 - FEET_SRC * S0             # feet line at y=1490

shadow = Image.new("RGBA", subj.size, (40, 30, 30, 0))
shadow.putalpha(subj.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.32)))


def place(img, sx, sy, tx, ty, resample=Image.BICUBIC):
    """draw img scaled (sx,sy) and translated (tx,ty) into a WxH frame"""
    return img.transform((W, H), Image.AFFINE, (1 / sx, 0, -tx / sx, 0, 1 / sy, -ty / sy), resample=resample)


# bokeh particles (behind subject)
N = 34
P = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), r=rng.uniform(5, 18), a=rng.uniform(.10, .30),
          v=rng.uniform(18, 45), ph=rng.uniform(0, 6.28)) for _ in range(N)]
DOT = {}


def dot(r):
    r = int(r)
    if r not in DOT:
        s = r * 4
        im = Image.new("L", (s, s), 0); ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=255)
        DOT[r] = im.filter(ImageFilter.GaussianBlur(r * 0.45))
    return DOT[r]


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
DIAG = (xx * math.cos(math.radians(70)) + yy * math.sin(math.radians(70))) / 1.0
VIG = np.clip(1 - 0.28 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .75)) ** 2), 0, 1)[..., None]

# optional end title
if TITLE:
    lg = Image.open(f"{D}/../img/logo.png").convert("RGBA")
    lw = 520; lh = round(lg.height * lw / lg.width)
    a = lg.getchannel("A").resize((lw, lh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.0))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))
    LOGO = Image.new("RGBA", (lw, lh), (35, 28, 26, 0)); LOGO.putalpha(a)
    TXT = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(TXT)
    f = ImageFont.truetype(f"{FD}/heebo-hebrew-400-normal.woff", 62)
    s = "שמלת בייסיק ש. ארוך טייגר בז׳"
    # the Hebrew subset has no '.', so draw the period with the Latin face right after "ש"
    parts = [("שמלת בייסיק ש", f), (".", ImageFont.truetype(f"{FD}/heebo-latin-400-normal.woff", 62)), (" ארוך טייגר בז׳", f)]
    widths = [d.textbbox((0, 0), t, font=ff)[2] for t, ff in parts]
    x = (W + sum(widths)) / 2   # right-to-left: start from the right edge
    for (t, ff), w_ in zip(parts, widths):
        x -= w_; d.text((x, 40), t, font=ff, fill=(52, 40, 36, 255))
    d.line([(W / 2 - 90, 160), (W / 2 + 90, 160)], fill=(180, 150, 120, 255), width=2)


def frame(n):
    t = n / FPS
    p = ease(t / T)
    # background: gentle push + drift left
    zb = 1 + 0.02 * p
    fr = place(bg, S0 * zb, S0 * zb, OX - PADL * S0 * zb - (zb - 1) * W / 2 - 18 * (2 * p - 1), OY - PADT * S0 * zb - (zb - 1) * H / 2).convert("RGBA")
    # bokeh, drifting upward with a slight sway
    for q in P:
        y = (q["y"] - q["v"] * t) % (H + 80) - 40
        x = q["x"] + 14 * math.sin(t * 0.8 + q["ph"]) - 30 * (2 * p - 1)
        dm = dot(q["r"]); col = Image.new("RGBA", dm.size, (255, 236, 214, 0))
        col.putalpha(dm.point(lambda v, k=q["a"] * (0.6 + 0.4 * math.sin(t * 1.3 + q["ph"])): int(v * k)))
        fr.alpha_composite(col, (int(x - dm.width / 2), int(y - dm.height / 2)))
    # subject: stronger push (closer to camera) + opposite drift = parallax; breathing anchored at the feet
    zs = 1 + 0.045 * p
    br = 1 + 0.0045 * math.sin(2 * math.pi * t / 3.6)
    sx, sy = S0 * zs, S0 * zs * br
    feet_y = OY + FEET_SRC * S0
    tx = W / 2 - CX_SRC * sx + 22 * (2 * p - 1)
    ty = feet_y - FEET_SRC * sy
    fr.alpha_composite(place(shadow, sx, sy, tx + 26, ty + 6))
    sl = place(subj, sx, sy, tx, ty)
    fr.alpha_composite(sl)
    A = np.asarray(fr.convert("RGB")).astype(np.float32)
    # light sheen sweeping across the dress (masked to subject), 1.6s - 3.6s
    if 1.4 < t < 3.9:
        c = -300 + (2400 + 300) * eout((t - 1.4) / 2.5)
        band = np.exp(-((DIAG - c) / 110) ** 2) * 0.30
        m = np.asarray(sl.getchannel("A")).astype(np.float32)[..., None] / 255
        b = band[..., None] * m
        A = A + (255 - A) * b
    # warm grade + soft vignette
    A = A * np.array([1.02, 1.0, 0.975]) * VIG
    out = Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))
    if TITLE and t > 5.2:
        k = eout((t - 5.2) / 0.9)
        o = out.convert("RGBA")
        veil = Image.new("RGBA", (W, H), (244, 237, 230, 0))
        g = Image.linear_gradient("L").resize((W, H)).point(lambda v, k=k: int(max(0, v - 190) * 3.0 * k))
        veil.putalpha(g); o.alpha_composite(veil)
        l = LOGO.copy(); l.putalpha(LOGO.getchannel("A").point(lambda v, k=k: int(v * k)))
        o.alpha_composite(l, ((W - l.width) // 2, 1580 + int(20 * (1 - k))))
        k2 = eout((t - 5.7) / 0.9)
        if k2 > 0:
            tt = TXT.copy(); tt.putalpha(TXT.getchannel("A").point(lambda v, k=k2: int(v * k)))
            o.alpha_composite(tt, (0, 1680 + int(16 * (1 - k2))))
        out = o.convert("RGB")
    return out


def main():
    only = os.environ.get("FRAMES")
    if only:
        for n in map(int, only.split(",")):
            frame(n).save(f"{D}/a{n:03d}.jpg", quality=90)
        return
    out = f"{D}/embrya_dress_tiger_animation{'_title' if TITLE else ''}.mp4"
    pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(NF):
        pr.stdin.write(frame(n).tobytes())
    pr.stdin.close(); pr.wait()
    print(out)


if __name__ == "__main__":
    main()
