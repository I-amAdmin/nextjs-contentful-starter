import os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
IMG, OUT = f"{S}/img", f"{S}/build"
os.makedirs(OUT, exist_ok=True)
FD = f"{S}/fonts"
HEEBO = lambda w: f"{FD}/fontsource-heebo-5.3.0/package/files/heebo-hebrew-{w}-normal.woff"
CORM = f"{FD}/fontsource-cormorant-garamond-5.3.0/package/files/cormorant-garamond-latin-500-italic.woff"
CORM_R = f"{FD}/fontsource-cormorant-garamond-5.3.0/package/files/cormorant-garamond-latin-400-normal.woff"
HEEBO_LAT = f"{FD}/fontsource-heebo-5.3.0/package/files/heebo-latin-300-normal.woff"
W, H, FPS = 1080, 1920, 30
TOTAL = 25.0
CREAM = (244, 237, 230)

# (file, crop-x 0..1, zoom mode, caption lines [(text, kind)], base duration, transition-to-next, xfade dur)
SHOTS = [
    ("SERENA_TERRACOTTA_4-720x960.png", .50, "out", [("Cache Cœur", "latin"), ("חזיות הנקה מצרפת", "he")], 3.2, "fadewhite", .45),
    ("Skin_latte_SG_postpartum_1-720x960.png", .50, "in", [], 2.1, "smoothleft", .40),
    ("Skin_chocolat_SG_enceinte_6-720x960.png", .45, "panr", [("רכות שעוטפת אותך", "he")], 2.3, "circleopen", .50),
    ("ZOE_VERT-D-EAU-PA411small-720x960.jpg", .50, "in", [("נוחות בלי תפרים", "he")], 2.0, "zoomin", .40),
    ("ZOE_VERT_D_EAU_SF411_3small-720x960.jpg", .50, "out", [], 1.9, "slideup", .40),
    ("ESSENTIEL_BEIGE-SF800_3-scaled-720x960.jpg", .40, "in", [("פתיחה קלה להנקה", "he")], 2.3, "hblur", .40),
    ("ZOE_NOIR-SF411_1small-720x960.jpg", .60, "panl", [], 1.8, "smoothright", .40),
    ("WOMA_PRUNE_SF2003_PL2003_6-scaled-720x960.jpg", .50, "in", [("תמיכה גם בתנועה", "he")], 2.0, "fade", .25),
    ("WOMA_NOIR-SF2003_PA2003_3-scaled-720x960.jpg", .40, "in", [], 1.4, "fade", .25),
    ("WOMA_BLEU-ELECTRIQUE-PA2003_1-scaled-720x960.jpg", .50, "in", [], 1.4, "dissolve", .40),
    ("ZOE_TERRACOTTA_LG411_4small-720x960.jpg", .40, "out", [("מההריון ועד ההנקה", "he")], 2.5, "fade", .60),
    ("ENDCARD", 0, "", [], 4.2, None, 0),
]

# stretch shot durations (except end card) so final length is exactly TOTAL
base = sum(s[4] for s in SHOTS) - sum(s[6] for s in SHOTS)
flex = sum(s[4] for s in SHOTS[:-1])
k = (TOTAL - base + flex) / flex
SHOTS = [s[:4] + (round(s[4] * k, 3) if s[0] != "ENDCARD" else s[4],) + s[5:] for s in SHOTS]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def he(t):  # visual order for pure-Hebrew lines (no shaping needed in Hebrew)
    return t  # Pillow+raqm already applies bidi


def text_layer(lines, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 1380 if len(lines) == 1 else 1250
    items = []
    for t, kind in lines:
        if kind == "latin":
            f = ImageFont.truetype(CORM, 150); s = t
        else:
            f = ImageFont.truetype(HEEBO(500), 84); s = he(t)
        bb = d.textbbox((0, 0), s, font=f)
        items.append((s, f, bb))
    # soft bottom gradient so captions read on light frames
    g = Image.new("L", (1, H), 0)
    for yy_ in range(H):
        g.putpixel((0, yy_), int(110 * max(0, (yy_ - 1050) / (H - 1050)) ** 1.3))
    im.alpha_composite(Image.merge("RGBA", (Image.new("L", (W, H), 30), Image.new("L", (W, H), 18), Image.new("L", (W, H), 12), g.resize((W, H)))))
    # soft shadow pass
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    yy = y
    for s, f, bb in items:
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        sd.text((x, yy - bb[1]), s, font=f, fill=(40, 20, 10, 150))
        yy += (bb[3] - bb[1]) + 46
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(sh)
    yy = y
    for i, (s, f, bb) in enumerate(items):
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x, yy - bb[1]), s, font=f, fill=(255, 250, 245, 255))
        yy += (bb[3] - bb[1]) + 46
        if i == 0 and len(items) > 1:  # thin gold rule between brand name and line
            d.line([(W / 2 - 70, yy - 22), (W / 2 + 70, yy - 22)], fill=(214, 180, 140, 255), width=3)
    im.save(path)


def crop_src(name, cx, path):
    src = Image.open(f"{IMG}/{name}").convert("RGB")
    cw = int(src.height * 9 / 16)
    x0 = int((src.width - cw) * cx)
    src.crop((x0, 0, x0 + cw, src.height)).resize((W * 2, H * 2), Image.LANCZOS).save(path, quality=97)


def logo_hi(path, width=820):
    lg = Image.open(f"{IMG}/logo.png").convert("RGBA")
    a = lg.getchannel("A")
    hgt = round(lg.height * width / lg.width)
    a = a.resize((width, hgt), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    a = a.point(lambda v: max(0, min(255, int((v - 70) * 255 / 120))))  # crisp edges after upscale
    out = Image.new("RGBA", (width, hgt), (35, 28, 26, 0)); out.putalpha(a)
    out.save(path)
    return width, hgt


def endcard():
    bg = Image.new("RGB", (W, H), CREAM)
    # subtle warm radial glow
    glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse((W/2 - 700, 760 - 700, W/2 + 700, 760 + 700), fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    bg = Image.composite(Image.new("RGB", (W, H), (236, 214, 198)), bg, glow)
    bg.save(f"{OUT}/end_bg.png")
    logo_hi(f"{OUT}/end_logo.png")
    # tagline layer
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    rows = [(he("חזיות הנקה והריון"), ImageFont.truetype(HEEBO(400), 58), (90, 62, 50), 1110),
            ("Cache Cœur", ImageFont.truetype(CORM, 96), (166, 98, 72), 1200),
            ("embrya.co.il", ImageFont.truetype(HEEBO_LAT, 50), (90, 62, 50), 1400)]
    for s, f, c, y in rows:
        bb = d.textbbox((0, 0), s, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2 - bb[0], y - bb[1]), s, font=f, fill=c + (255,))
    d.line([(W/2 - 60, 1355), (W/2 + 60, 1355)], fill=(200, 160, 120, 255), width=2)
    t.save(f"{OUT}/end_text.png")


def light_leak():
    im = Image.new("RGB", (W * 2, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    for (cx, cy, r, c) in [(500, 500, 420, (255, 196, 150)), (1500, 1300, 520, (255, 214, 176)), (1000, 900, 300, (250, 176, 132))]:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    im.filter(ImageFilter.GaussianBlur(160)).save(f"{OUT}/leak.png")


GRADE = "eq=contrast=1.04:saturation=1.06:gamma=1.02,colorbalance=rs=.03:gs=.01:bs=-.03:rh=.02:bh=-.02"


def shot_clip(i, s):
    name, cx, mode, cap, dur, *_ = s
    out = f"{OUT}/s{i:02d}.mp4"
    if name != "ENDCARD" and os.path.exists(out) and os.environ.get("REUSE"):
        return out
    n = int(round(dur * FPS))
    if name == "ENDCARD":
        # rendered frame-by-frame: logo eases in from blur + scale, tagline rises in after
        bg = Image.open(f"{OUT}/end_bg.png").convert("RGBA")
        lg = Image.open(f"{OUT}/end_logo.png"); tx = Image.open(f"{OUT}/end_text.png")
        ease = lambda v: 1 - (1 - max(0, min(1, v))) ** 3
        os.makedirs(f"{OUT}/end", exist_ok=True)
        for f in range(n):
            t = f / FPS
            fr = bg.copy()
            p1 = ease(t / 1.3)
            sc = 1.12 - 0.12 * p1
            l = lg.resize((round(lg.width * sc), round(lg.height * sc)), Image.LANCZOS)
            if p1 < 1:
                l = l.filter(ImageFilter.GaussianBlur(14 * (1 - p1)))
            al = l.getchannel("A").point(lambda v, k=min(1, t / 0.9): int(v * k)); l.putalpha(al)
            fr.alpha_composite(l, ((W - l.width) // 2, 840 - l.height // 2))
            p2 = ease((t - 1.1) / 0.8)
            if p2 > 0:
                tt = tx.copy(); tt.putalpha(tx.getchannel("A").point(lambda v, k=p2: int(v * k)))
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(tt, (0, round(24 * (1 - p2))))
                fr.alpha_composite(lay)
            fr.convert("RGB").save(f"{OUT}/end/{f:04d}.png")
        run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{OUT}/end/%04d.png", "-frames:v", str(n),
             "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", out])
        return out
    crop_src(name, cx, f"{OUT}/c{i:02d}.jpg")
    # smooth ken-burns: work on 2x frame, ease-in-out progress p
    p = f"(0.5-0.5*cos(PI*on/{n}))"
    z = {"in": f"1.0+0.10*{p}", "out": f"1.10-0.10*{p}", "panr": "1.10", "panl": "1.10"}[mode]
    x = {"panr": f"(iw-iw/zoom)*{p}", "panl": f"(iw-iw/zoom)*(1-{p})"}.get(mode, "(iw-iw/zoom)/2")
    zp = f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d={n}:s={W}x{H}:fps={FPS}"
    inputs = ["-loop", "1", "-framerate", str(FPS), "-i", f"{OUT}/c{i:02d}.jpg"]
    if cap:
        text_layer(cap, f"{OUT}/t{i:02d}.png")
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", f"{OUT}/t{i:02d}.png"]
        st = 0.35 if i else 0.5
        fc = (f"[0:v]scale={W*2}:{H*2},{zp},{GRADE},format=rgba[b];"
              f"[1:v]format=rgba,fade=in:st={st}:d=0.6:alpha=1,fade=out:st={dur-0.75:.2f}:d=0.4:alpha=1[t];"
              f"[b][t]overlay=x=0:y='36*max(0,1-(t-{st})/0.7)^2':eval=frame,format=yuv420p[v]")
    else:
        fc = f"[0:v]scale={W*2}:{H*2},{zp},{GRADE},format=yuv420p[v]"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n),
         "-c:v", "libx264", "-crf", "12", "-preset", "medium", out])
    return out


def main():
    endcard(); light_leak()
    clips = [shot_clip(i, s) for i, s in enumerate(SHOTS)]
    # xfade chain
    args, fc, prev, off = [], [], "0:v", 0.0
    for i, c in enumerate(clips):
        args += ["-i", c]
    for i in range(1, len(clips)):
        dur_prev, tr, xd = SHOTS[i - 1][4], SHOTS[i - 1][5], SHOTS[i - 1][6]
        off += dur_prev - xd
        lab = f"x{i}"
        fc.append(f"[{prev}][{i}:v]xfade=transition={tr}:duration={xd}:offset={off:.3f}[{lab}]")
        prev = lab
    # finishing: drifting light leak (screen), film grain, soft vignette
    nleak = len(clips)
    args += ["-loop", "1", "-framerate", str(FPS), "-t", str(TOTAL), "-i", f"{OUT}/leak.png"]
    leak_alpha = "if(lt(T,1.6),0.32*(1-T/1.6),0)+if(between(T,9,11),0.35*sin(PI*(T-9)/2),0)+if(between(T,18.2,19.8),0.30*sin(PI*(T-18.2)/1.6),0)"
    fc.append(f"[{nleak}:v]format=rgb24,crop={W}:{H}:x='(iw-{W})*t/{TOTAL}':y=0[lk]")
    fc.append(f"[{prev}]format=rgb24[base]")
    fc.append(f"[base][lk]blend=all_mode=screen:all_expr='A*(1-({leak_alpha}))+(255-(255-A)*(255-B)/255)*({leak_alpha})'[lb]")
    fc.append(f"[lb]noise=alls=3:allf=t,vignette=angle=PI/5:mode=forward,format=yuv420p[v]")
    run(["ffmpeg", "-y", *args, "-filter_complex", ";".join(fc), "-map", "[v]", "-t", str(TOTAL), "-r", str(FPS),
         "-c:v", "libx264", "-crf", "19", "-maxrate", "16M", "-bufsize", "32M", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", f"{S}/embrya_cache_coeur_reel.mp4"])
    for s in SHOTS: print(f"{s[0][:40]:42s} {s[4]:.2f}s -> {s[5]}")


if __name__ == "__main__":
    main()
