"""2D motion-design shots drawn with Pillow frame by frame, finished like the 3D shots (grain, CA, vignette).

map_zoom  – stylised map from Natural Earth (public domain) with an eased zoom, highlighted country,
            pulsing points, labels and an animated arrow.
auction   – own mock-up of an online auction (no logos): running price and bidder count, then a bar
            comparison of two amounts.
Usage: python -m lib.motion2d <shot> <out.mp4> '<params json>'   (run from pipeline/)
"""
import json, math, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .fx3d import W, H, FPS, ease, finish, writer
from .graphics import B, PIPE

SS = 2                                     # supersample, frames are drawn at 2x and downscaled
GEO = Path("/mnt/project-files/youtube/env/geo")

def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
BG, BG2, TEXT, MUTED, ACCENT, LINE = (hexrgb(B[k]) for k in ("bg", "bg2", "text", "muted", "accent", "line"))

_FONTS = {}
def font(px, weight="Bold"):
    key = (int(px * SS), weight)
    if key not in _FONTS:
        f = ImageFont.truetype(str(PIPE / "brand" / B["font"]), key[0])
        try: f.set_variation_by_name(weight)
        except Exception: pass
        _FONTS[key] = f
    return _FONTS[key]

STILL = None   # set by __main__ from params["still"]: render only the frame at that time to <out>.png

def emit(wtr, img, t, seed, out):
    fr = to_frame(img, t, seed)
    if STILL is not None:
        if abs(t - STILL) < 0.5 / FPS: cv2.imwrite(str(out) + ".png", fr)
        return
    wtr.stdin.write(fr.tobytes())

def to_frame(img, t, seed):
    a = cv2.cvtColor(np.asarray(img.resize((W, H), Image.LANCZOS)), cv2.COLOR_RGB2BGR)
    return finish(a, t, grain=0.03, ca=1.5, vignette=0.5, seed=seed)

# ---------------------------------------------------------------- maps
def load_polys(bbox, highlight=None):
    """Polygons (lon/lat arrays) of countries intersecting bbox; returns [(name, [ring arrays])]."""
    lo0, la0, lo1, la1 = bbox; out = []
    for fn in ("ne_10m_admin_0_countries.geojson", "ne_10m_minor_islands.geojson"):
        p = GEO / fn
        if not p.exists(): continue
        for f in json.loads(p.read_text())["features"]:
            g = f["geometry"]; name = f["properties"].get("NAME", "") if "countries" in fn else ""
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            rings = []
            for poly in polys:
                r = np.array(poly[0], float)
                if r[:, 0].max() < lo0 or r[:, 0].min() > lo1 or r[:, 1].max() < la0 or r[:, 1].min() > la1: continue
                rings.append(r)
            if rings: out.append((name, rings))
    return out

def map_zoom(out, p):
    """p: dur, start=[lon,lat,span_deg], end=[...], zoom=[t0,t1] (s), highlight (country NAME), labels=[{text,lon,lat,t,size,dx,dy}],
    points=[{lon,lat,t}], arrow={from:[lon,lat], to:[lon,lat], t0, t1}, question={lon,lat,t} (a '?' next to a point)."""
    dur = p["dur"]; n = int(round(dur * FPS)); (sx, sy, ss), (ex, ey, es) = p["start"], p["end"]
    z0, z1 = p.get("zoom", [0.4, dur * 0.7])
    pad = max(ss, es) * 1.2
    bbox = (min(sx, ex) - pad, min(sy, ey) - pad, max(sx, ex) + pad, max(sy, ey) + pad)
    polys = load_polys(bbox); hl = p.get("highlight")
    w, h = W * SS, H * SS
    wtr = writer(str(out))
    for i in range(n):
        t = i / FPS
        if STILL is not None and abs(t - STILL) >= 0.5 / FPS: continue
        k = ease((t - z0) / max(z1 - z0, 1e-6))
        cx, cy = sx + (ex - sx) * k, sy + (ey - sy) * k
        span = math.exp(math.log(ss) + (math.log(es) - math.log(ss)) * k)   # constant-speed zoom
        kx = w / span                                        # pixels per degree of longitude×cos(lat)
        coslat = math.cos(math.radians(cy))
        def P(lon, lat): return ((lon - cx) * coslat * kx + w / 2, -(lat - cy) * kx + h / 2)
        img = Image.new("RGB", (w, h), BG); d = ImageDraw.Draw(img)
        g = 1 if span < 3 else (2 if span < 8 else 5)       # graticule every g degrees
        for lon in range(int(cx - span) // g * g, int(cx + span) + g, g):
            x, _ = P(lon, cy); d.line([(x, 0), (x, h)], fill=(20, 28, 44), width=SS)
        for lat in range(int(cy - span) // g * g, int(cy + span) + g, g):
            _, y = P(cx, lat); d.line([(0, y), (w, y)], fill=(20, 28, 44), width=SS)
        for name, rings in polys:
            on = hl and name == hl
            for r in rings:
                xs = (r[:, 0] - cx) * coslat * kx + w / 2; ys = -(r[:, 1] - cy) * kx + h / 2
                if xs.max() < 0 or xs.min() > w or ys.max() < 0 or ys.min() > h: continue
                pts = list(zip(xs.tolist(), ys.tolist()))
                if len(pts) < 3: continue
                d.polygon(pts, fill=(38, 52, 76) if on else BG2, outline=ACCENT if on else LINE, width=2 * SS if on else SS)
        # arrow
        a = p.get("arrow")
        if a and t >= a["t0"]:
            u = ease((t - a["t0"]) / (a["t1"] - a["t0"]))
            (x0, y0), (x1, y1) = P(*a["from"]), P(*a["to"])
            mx, my = (x0 + x1) / 2 - (y1 - y0) * 0.25, (y0 + y1) / 2 + (x1 - x0) * 0.25   # curved
            pts = [((1 - s) ** 2 * x0 + 2 * (1 - s) * s * mx + s * s * x1, (1 - s) ** 2 * y0 + 2 * (1 - s) * s * my + s * s * y1)
                   for s in np.linspace(0, u, 60)]
            d.line(pts, fill=ACCENT, width=6 * SS, joint="curve")
            if u > 0.02:
                (px, py), (qx, qy) = pts[-2], pts[-1]; ang = math.atan2(qy - py, qx - px); L = 30 * SS
                d.polygon([(qx, qy), (qx - L * math.cos(ang - 0.45), qy - L * math.sin(ang - 0.45)),
                           (qx - L * math.cos(ang + 0.45), qy - L * math.sin(ang + 0.45))], fill=ACCENT)
        # points with pulse
        glow = Image.new("RGB", (w, h), (0, 0, 0)); gd = ImageDraw.Draw(glow)
        for pt in p.get("points", []):
            if t < pt.get("t", 0): continue
            x, y = P(pt["lon"], pt["lat"]); a_in = min(1, (t - pt.get("t", 0)) / 0.3)
            for ph in (0, 0.5):
                q = ((t * 0.8 + ph) % 1.0); r = (14 + 70 * q) * SS
                d.ellipse([x - r, y - r, x + r, y + r], outline=tuple(int(c * (1 - q) * a_in + b * (1 - (1 - q) * a_in)) for c, b in zip(ACCENT, BG2)), width=3 * SS)
            r = 13 * SS * a_in; d.ellipse([x - r, y - r, x + r, y + r], fill=ACCENT)
            gd.ellipse([x - 3 * r, y - 3 * r, x + 3 * r, y + 3 * r], fill=ACCENT)
        img = Image.fromarray(np.clip(np.asarray(img, np.int16) + (np.asarray(glow.filter(ImageFilter.GaussianBlur(30 * SS)), np.int16) * 0.5).astype(np.int16), 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        q = p.get("question")
        if q and t >= q["t"]:
            x, y = P(q["lon"], q["lat"]); s = ease((t - q["t"]) / 0.4)
            d.text((x + 60 * SS, y - 20 * SS), "?", font=font(150 * (0.6 + 0.4 * s)), fill=ACCENT, anchor="ls")
        for lb in p.get("labels", []):
            t0 = lb.get("t", 0); t1 = lb.get("t_end", dur + 1)
            if not (t0 <= t < t1): continue
            al = min(1, (t - t0) / 0.4, (t1 - t) / 0.4)
            x, y = P(lb["lon"], lb["lat"]); x += lb.get("dx", 0) * SS; y += lb.get("dy", 0) * SS
            f = font(lb.get("size", 54)); col = tuple(int(c * al + b * (1 - al)) for c, b in zip(TEXT, BG))
            tw = d.textlength(lb["text"], font=f); anchor = lb.get("anchor", "mm")
            x = min(max(x, 90 * SS + (tw / 2 if anchor == "mm" else 0)), w - 90 * SS - (tw / 2 if anchor == "mm" else tw))
            y = min(max(y, 80 * SS + f.size / 2), h - 80 * SS - f.size / 2)     # keep labels inside the title-safe area
            d.text((x + 3 * SS, y + 3 * SS), lb["text"], font=f, fill=BG, anchor=anchor)
            d.text((x, y), lb["text"], font=f, fill=col, anchor=anchor)
        emit(wtr, img, t, 11, out)
    wtr.stdin.close(); wtr.wait()
    return n

# ---------------------------------------------------------------- auction
def money(v): return f"{int(round(v)):,}".replace(",", " ") + " $"

def auction(out, p):
    """p: dur, split (s, end of the auction part), final (price), bidders, item, bars=[[value,label],[value,label]]."""
    dur, split = p["dur"], p.get("split", 5.8); n = int(round(dur * FPS)); w, h = W * SS, H * SS
    wtr = writer(str(out))
    for i in range(n):
        t = i / FPS
        if STILL is not None and abs(t - STILL) >= 0.5 / FPS: continue
        img = Image.new("RGB", (w, h), BG); d = ImageDraw.Draw(img)
        if t < split:
            u = ease(min(1, t / (split * 0.85)))
            # window chrome (own generic design, no brand)
            X0, Y0, X1, Y1 = 240 * SS, 130 * SS, 1680 * SS, 950 * SS
            d.rounded_rectangle([X0, Y0, X1, Y1], 28 * SS, fill=(24, 32, 48), outline=LINE, width=2 * SS)
            d.rounded_rectangle([X0, Y0, X1, Y0 + 70 * SS], 28 * SS, fill=(30, 40, 60)); d.rectangle([X0, Y0 + 40 * SS, X1, Y0 + 70 * SS], fill=(30, 40, 60))
            for k, c in enumerate(((235, 94, 85), (242, 177, 52), (98, 196, 110))):
                d.ellipse([X0 + (36 + 34 * k) * SS - 10 * SS, Y0 + 35 * SS - 10 * SS, X0 + (36 + 34 * k) * SS + 10 * SS, Y0 + 35 * SS + 10 * SS], fill=c)
            d.rounded_rectangle([X0 + 160 * SS, Y0 + 16 * SS, X1 - 60 * SS, Y0 + 54 * SS], 18 * SS, fill=(18, 24, 36))
            d.text((X0 + 185 * SS, Y0 + 35 * SS), "aukce · online", font=font(22, "Regular"), fill=MUTED, anchor="lm")
            # item box
            d.rounded_rectangle([X0 + 60 * SS, Y0 + 120 * SS, X0 + 560 * SS, Y1 - 60 * SS], 20 * SS, fill=(18, 24, 36))
            d.text(((X0 + 310 * SS), (Y0 + Y1) / 2 + 30 * SS), p.get("item_mark", "FYRE"), font=font(96), fill=ACCENT, anchor="mm")
            d.text(((X0 + 310 * SS), (Y0 + Y1) / 2 + 110 * SS), p.get("item_sub", "značka a práva"), font=font(30, "Regular"), fill=MUTED, anchor="mm")
            tx = X0 + 640 * SS
            d.text((tx, Y0 + 160 * SS), p.get("item", "Značka FYRE"), font=font(60), fill=TEXT, anchor="ls")
            d.text((tx, Y0 + 250 * SS), "Aktuální nabídka", font=font(34, "Regular"), fill=MUTED, anchor="ls")
            d.text((tx, Y0 + 400 * SS), money(p["final"] * u), font=font(130), fill=ACCENT, anchor="ls")
            nb = int(round(p["bidders"] * u))
            d.text((tx, Y0 + 500 * SS), f"{nb} přihazujících", font=font(46, "SemiBold"), fill=TEXT, anchor="ls")
            # progress bar = time left
            d.rounded_rectangle([tx, Y0 + 580 * SS, X1 - 80 * SS, Y0 + 600 * SS], 10 * SS, fill=(18, 24, 36))
            d.rounded_rectangle([tx, Y0 + 580 * SS, tx + (X1 - 80 * SS - tx) * max(0.02, 1 - u), Y0 + 600 * SS], 10 * SS, fill=ACCENT)
            if u >= 0.999:
                d.text((tx, Y0 + 680 * SS), "Konečná cena", font=font(40, "SemiBold"), fill=TEXT, anchor="ls")
        else:
            u = ease(min(1, (t - split) / 2.2)); bars = [b + [None] * (3 - len(b)) for b in p["bars"]]; (v1, l1, _), (v2, l2, _) = bars
            base = 900 * SS; top = 150 * SS; full = base - top; scale = full / max(v1, v2)
            for k, (v, lab, shown) in enumerate(bars):
                cx = (660 if k == 0 else 1260) * SS; bw = 260 * SS
                hgt = max(6 * SS, v * scale * (u if k else min(1, u * 3)))
                col = ACCENT if k == 0 else (200, 70, 60)
                d.rectangle([cx - bw / 2, base - hgt, cx + bw / 2, base], fill=col)
                al = min(1, max(0, (t - split - (0.3 if k == 0 else 1.6)) / 0.4))
                ct = tuple(int(c * al + b * (1 - al)) for c, b in zip(TEXT, BG)); cm = tuple(int(c * al + b * (1 - al)) for c, b in zip(MUTED, BG))
                d.text((cx, base - hgt - 30 * SS), shown or money(v), font=font(64), fill=ct, anchor="ms")
                d.text((cx, base + 60 * SS), lab, font=font(36, "Regular"), fill=cm, anchor="ms")
            d.line([(360 * SS, base), (1560 * SS, base)], fill=LINE, width=3 * SS)
        emit(wtr, img, t, 21, out)
    wtr.stdin.close(); wtr.wait()
    return n

if __name__ == "__main__":
    shot, out, params = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]); STILL = params.get("still")
    n = {"map_zoom": map_zoom, "auction": auction}[shot](out, params)
    print(json.dumps({"shot": shot, "out": out, "frames": n}))
