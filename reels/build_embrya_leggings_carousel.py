"""Embrya maternity-leggings Meta carousel: 7 square cards (1080x1080) cut from one continuous panorama,
so a flowing blush line and soft shapes carry across card edges as the viewer swipes."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
IMG = f"{D}/img"
OUT = f"{D}/carousel"; os.makedirs(OUT, exist_ok=True)
FD = f"{D}/../fonts/fontsource-heebo-5.3.0/package/files"
LOGO = f"{D}/../img/logo.png"
S = 1080; NCARD = 7; PW = S * NCARD
HE = lambda w, s: ImageFont.truetype(f"{FD}/heebo-hebrew-{w}-normal.woff", s)
LA = lambda w, s: ImageFont.truetype(f"{FD}/heebo-latin-{w}-normal.woff", s)
CREAM = (246, 239, 232); INK = (58, 40, 36); MUTED = (112, 84, 74); BLUSH = (226, 160, 138); BLUSH_L = (241, 214, 200)

FILES = {
    "liberty_belly": "LIBERTY4-720x960.jpg", "liberty_home": "LIBERTY5-720x960.jpg",
    "zoe_black": "ZOE_NOIR-SF411_LG411_8small-720x960.jpg", "zoe_red": "ZOE_TERRACOTTA-SF411_04small-720x960.jpg",
    "black_7_8": "IMG_1658-720x960.jpg", "navy": "navy-720x960.jpg", "leopard": "IMG_1786-720x960.jpg",
    "brown_biker": "brown_biker_user.jpg", "speckle": "IMG_2422-720x960.jpg", "grey": "light-grey-720x960.jpg",
    "tiger": "IMG_1767-720x960.jpg", "brown_straight": "טייץ-ישר-חום-קטן-720x960.jpg",
}


def grade(im):
    a = np.asarray(im).astype(np.float32) / 255
    a = a * 0.97 + 0.025; a *= np.array([1.015, 1.0, 0.98])
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def photo(key, w, h, cx=0.5, cy=0.35, box=None):
    src = Image.open(f"{IMG}/{FILES[key]}").convert("RGB")
    asp = w / h
    if box:
        x0, y0, cw = box; ch = cw / asp
    else:
        cw, ch = src.width, src.width / asp
        if ch > src.height:
            ch = src.height; cw = ch * asp
        x0 = (src.width - cw) * cx; y0 = (src.height - ch) * cy
    im = src.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    if box:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=2))
    return grade(im)


def arch_mask(w, h, r=None):
    r = r or w // 2
    m = Image.new("L", (w * 2, h * 2), 0); d = ImageDraw.Draw(m)
    d.rectangle((0, r * 2, w * 2, h * 2), fill=255); d.ellipse((0, 0, w * 2, r * 4), fill=255)
    return m.resize((w, h), Image.LANCZOS)


def round_mask(w, h, rad=36):
    m = Image.new("L", (w * 2, h * 2), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), rad * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def shadowed(canvas, im, mask, xy, blur=26, off=(0, 18), alpha=70):
    sh = Image.new("RGBA", (im.width + 120, im.height + 120), (0, 0, 0, 0))
    sm = Image.new("L", sh.size, 0); sm.paste(mask.point(lambda v: v * alpha // 255), (60, 60))
    sh.putalpha(sm.filter(ImageFilter.GaussianBlur(blur)))
    sh2 = Image.new("RGBA", sh.size, (80, 40, 25, 0)); sh2.putalpha(sh.getchannel("A"))
    canvas.alpha_composite(sh2, (xy[0] - 60 + off[0], xy[1] - 60 + off[1]))
    lay = im.convert("RGBA"); lay.putalpha(mask); canvas.alpha_composite(lay, xy)


def wrap(text, font, maxw, draw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textbbox((0, 0), t, font=font)[2] <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines


def text_block(canvas, right, top, head, sub=None, maxw=430, hsize=84, ssize=46, accent=True):
    d = ImageDraw.Draw(canvas)
    fh = HE(800, hsize); y = top
    for ln in wrap(head, fh, maxw, d):
        b = d.textbbox((0, 0), ln, font=fh)
        d.text((right - (b[2] - b[0]) - b[0], y - b[1]), ln, font=fh, fill=INK)
        y += int(hsize * 1.18)
    if accent:
        d.rounded_rectangle((right - 120, y + 8, right, y + 16), 4, fill=BLUSH); y += 50
    if sub:
        fs = HE(400, ssize)
        for ln in wrap(sub, fs, maxw, d):
            b = d.textbbox((0, 0), ln, font=fs)
            d.text((right - (b[2] - b[0]) - b[0], y - b[1]), ln, font=fs, fill=MUTED)
            y += int(ssize * 1.35)
    return y


def logo_img(width):
    lg = Image.open(LOGO).convert("RGBA"); lh = round(lg.height * width / lg.width)
    a = lg.getchannel("A").resize((width, lh), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.0 if width > 300 else 0.6))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))
    o = Image.new("RGBA", (width, lh), (35, 28, 26, 0)); o.putalpha(a); return o


def chip(canvas, xy_center, word, size=52, fill=(255, 255, 255), fg=INK, arrow=False):
    d = ImageDraw.Draw(canvas); f = HE(700, size)
    b = d.textbbox((0, 0), word, font=f); w, h = b[2] - b[0] + 64 + (size if arrow else 0), b[3] - b[1] + 40
    x, y = xy_center[0] - w // 2, xy_center[1] - h // 2
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 36, 30 + w, 36 + h), h // 2, fill=(80, 40, 25, 60))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (x - 30, y - 30))
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=fill)
    d.text((x + w - 32 - (b[2] - b[0]) - b[0], y + 20 - b[1]), word, font=f, fill=fg)
    if arrow:   # drawn chevron pointing left (the font subset has no arrow glyph)
        ax, ay, r = x + 30 + size * 0.3, y + h / 2, size * 0.28
        d.line([(ax + r, ay - r), (ax, ay), (ax + r, ay + r)], fill=fg, width=max(3, size // 10), joint='curve')


# ---------- continuous background across all cards ----------
pano = Image.new("RGBA", (PW, S), CREAM + (255,))
blobs = Image.new("L", (PW, S), 0); bd = ImageDraw.Draw(blobs)
for i in range(NCARD + 1):   # soft blush blobs sitting on the card seams, so each edge "continues"
    cx = i * S + (0 if i % 2 else 60); cy = 260 if i % 2 else 860
    bd.ellipse((cx - 300, cy - 300, cx + 300, cy + 300), fill=150)
blobs = blobs.filter(ImageFilter.GaussianBlur(120))
pano = Image.composite(Image.new("RGBA", (PW, S), BLUSH_L + (255,)), pano, blobs)
# one flowing line through the whole carousel
line = Image.new("RGBA", (PW * 2, S * 2), (0, 0, 0, 0)); ld = ImageDraw.Draw(line)
pts = [(x, S + 300 * math.sin(x / (S * 2) * 2.1 + 0.6) + 120 * math.sin(x / 700)) for x in range(0, PW * 2, 8)]
ld.line(pts, fill=BLUSH + (200,), width=6, joint="curve")
pano.alpha_composite(line.resize((PW, S), Image.LANCZOS))
BUG = logo_img(200)

# ---------- card 1: cover ----------
x0 = 0
a = photo("liberty_belly", 430, 700); b = photo("zoe_red", 360, 600)
shadowed(pano, b, arch_mask(360, 600), (x0 + 70, 330))
shadowed(pano, a, arch_mask(430, 700), (x0 + 330, 250))
d = ImageDraw.Draw(pano)
f = HE(800, 104); t = "הטייץ שגדל איתך"; bb = d.textbbox((0, 0), t, font=f)
d.text((x0 + S - 70 - (bb[2] - bb[0]) - bb[0], 70 - bb[1]), t, font=f, fill=INK)
lg = logo_img(300); pano.alpha_composite(lg, (x0 + S - 70 - lg.width, 215))
f2 = HE(500, 40); t2 = "טייצים להריון"; bb = d.textbbox((0, 0), t2, font=f2)
d.text((x0 + S - 70 - (bb[2] - bb[0]) - bb[0], 300 - bb[1]), t2, font=f2, fill=MUTED)
chip(pano, (x0 + 860, 985), "החליקי לעוד", size=40, fill=BLUSH, fg=(255, 255, 255), arrow=True)

# ---------- cards 2-4, 6: arch photo + feature text ----------
FEATURES = {
    1: ("liberty_belly", "חגורת בטן נוחה", "שמתאימה את עצמה לגוף לאורך כל ההריון", {}),
    2: ("zoe_black", "חופש תנועה מלא", "ונוחות לאורך כל היום", {"cx": 0.45}),
    3: ("black_7_8", "התפרים עוברים מתחת לבטן", "ולא לוחצים", {"box": (150, 0, 420)}),
    5: ("zoe_red", "מתאים לאורך כל ההיריון", "וגם אחריו", {}),
}
for idx, (key, head, sub, kw) in FEATURES.items():
    x0 = idx * S
    pw, ph = 470, 820
    im = photo(key, pw, ph, **kw)
    shadowed(pano, im, arch_mask(pw, ph), (x0 + 70, 150))
    text_block(pano, x0 + S - 70, 330, head, sub, maxw=420)
    pano.alpha_composite(BUG, (x0 + S - 70 - BUG.width, 70))

# ---------- card 5: work / everyday / sport / home ----------
x0 = 4 * S
d = ImageDraw.Draw(pano)
f = HE(800, 64); t = "טייץ אחד לכל היום"; bb = d.textbbox((0, 0), t, font=f)   # header line is ours; the four words are from the product pages
d.text((x0 + S - 70 - (bb[2] - bb[0]) - bb[0], 70 - bb[1]), t, font=f, fill=INK)
cells = [("לעבודה", "navy"), ("ליומיום", "leopard"), ("לספורט", "brown_biker"), ("ולבית", "liberty_home")]
cw, chh, gap = 450, 405, 40
for i, (word, key) in enumerate(cells):
    col, row = i % 2, i // 2
    x = x0 + S - 70 - (col + 1) * cw - col * gap; y = 190 + row * (chh + gap)
    im = photo(key, cw, chh, cy=0.25)
    shadowed(pano, im, round_mask(cw, chh), (x, y), blur=18, off=(0, 12), alpha=60)
    chip(pano, (x + cw // 2, y + chh - 50), word, size=46)

# ---------- card 7: range + CTA ----------
x0 = 6 * S
tiles = ["speckle", "grey", "tiger", "brown_straight"]
tw, th = 230, 360
for i, key in enumerate(tiles):
    col, row = i % 2, i // 2
    x = x0 + 70 + col * (tw + 24); y = 170 + row * (th + 24)
    shadowed(pano, photo(key, tw, th, cy=0.3), round_mask(tw, th, 28), (x, y), blur=16, off=(0, 10), alpha=55)
y = text_block(pano, x0 + S - 70, 230, "מגוון גזרות", "אורכים והדפסים", maxw=430)
lg = logo_img(360); pano.alpha_composite(lg, (x0 + S - 70 - lg.width, y + 60))
d = ImageDraw.Draw(pano); f = LA(300, 40); t = "embrya.co.il"; bb = d.textbbox((0, 0), t, font=f)
d.text((x0 + S - 70 - (bb[2] - bb[0]) - bb[0], y + 160 - bb[1]), t, font=f, fill=MUTED)
chip(pano, (x0 + 800, y + 290), "לכל הדגמים באתר", size=50, fill=BLUSH, fg=(255, 255, 255))

# ---------- slice, number, save ----------
pano = pano.convert("RGB")
for i in range(NCARD):
    card = pano.crop((i * S, 0, (i + 1) * S, S))
    d = ImageDraw.Draw(card); f = LA(400, 30); t = f"{i + 1}/{NCARD}"
    bb = d.textbbox((0, 0), t, font=f); d.text((70 - bb[0], S - 60 - bb[1]), t, font=f, fill=(150, 120, 108))
    card.save(f"{OUT}/embrya_leggings_carousel_{i + 1:02d}.jpg", quality=95, subsampling=0)
# overview strip (cards in Meta's RTL order: card 1 on the right)
ov = Image.new("RGB", (NCARD * 300 + (NCARD + 1) * 16, 332), (230, 226, 222))
for i in range(NCARD):
    c = Image.open(f"{OUT}/embrya_leggings_carousel_{i + 1:02d}.jpg").resize((300, 300), Image.LANCZOS)
    ov.paste(c, (16 + i * 316, 16))
ov.save(f"{OUT}/overview.jpg", quality=90)
print("ok")
