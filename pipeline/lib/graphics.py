"""Pillow templates -> PNG at 2x resolution. Every card carries the on-screen source line."""
import json, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PIPE = Path(__file__).resolve().parents[1]
B = json.loads((PIPE / "brand" / "brand.json").read_text())
SS = B["supersample"]; W, H = B["w"] * SS, B["h"] * SS

def font(size, weight="Regular"):
    f = ImageFont.truetype(str(PIPE / "brand" / B["font"]), size * SS)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f

def background(seed=0):
    img = Image.new("RGB", (W, H), B["bg"]); d = ImageDraw.Draw(img)
    glow = Image.new("RGB", (W, H), B["bg"]); g = ImageDraw.Draw(glow)
    cx, cy = (W * (0.25 + 0.5 * ((seed * 37) % 10) / 10), H * 0.35)
    g.ellipse([cx - W * 0.45, cy - H * 0.6, cx + W * 0.45, cy + H * 0.6], fill=B["bg2"])
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220 * SS)), 0.9); d = ImageDraw.Draw(img)
    for x in range(0, W, 120 * SS): d.line([(x, 0), (x, H)], fill=B["bg"], width=1)
    return img

def fit_text(d, text, max_w, size, weight, max_lines):
    while size > 18:
        f = font(size, weight); lines = []
        for para in text.split("\n"):
            words, cur = para.split(), ""
            for w in words:
                cand = (cur + " " + w).strip()
                if d.textlength(cand, font=f) <= max_w: cur = cand
                else: lines.append(cur); cur = w
            lines.append(cur)
        if len(lines) <= max_lines: return f, lines
        size -= 4
    return font(size, weight), lines

def draw_lines(d, lines, f, x, y, fill, gap=1.18, anchor="la"):
    lh = f.size * gap
    for i, ln in enumerate(lines): d.text((x, y + i * lh), ln, font=f, fill=fill, anchor=anchor)
    return y + len(lines) * lh

def source_line(d, text):
    if not text: return
    f = font(22, "Medium"); x, y = 96 * SS, H - 70 * SS
    d.rectangle([x, y - 4 * SS, x + 6 * SS, y + 26 * SS], fill=B["accent"])
    d.text((x + 20 * SS, y), text, font=f, fill=B["muted"])

def card(template, params, source_text, seed=0, photo=None):
    img = background(seed); d = ImageDraw.Draw(img); M = 160 * SS
    if template == "title_card":
        f, lines = fit_text(d, params["text"], W - 2 * M, 96, "Bold", 3)
        y = H * 0.42 - len(lines) * f.size * 0.6
        d.rectangle([M, y - 40 * SS, M + 120 * SS, y - 30 * SS], fill=B["accent"])
        y = draw_lines(d, lines, f, M, y, B["text"])
        if params.get("sub"):
            f2, l2 = fit_text(d, params["sub"], W - 2 * M, 40, "Regular", 2); draw_lines(d, l2, f2, M, y + 30 * SS, B["muted"])
    elif template == "number_callout":
        f, _ = fit_text(d, params["value"], W - 2 * M, 200, "Bold", 1); y = H * 0.30
        d.text((M, y), params["value"], font=f, fill=B["accent"])
        f2, l2 = fit_text(d, params["label"], W - 2 * M, 52, "Medium", 2); draw_lines(d, l2, f2, M, y + 250 * SS, B["text"])
    elif template == "quote_card":
        d.text((M - 6 * SS, H * 0.10), "„", font=font(200, "Bold"), fill=B["accent"])
        f, lines = fit_text(d, params["quote"], W - 2 * M, 64, "Medium", 4)
        y = draw_lines(d, lines, f, M, H * 0.40, B["text"], gap=1.25)
        if params.get("translation"):
            f2, l2 = fit_text(d, params["translation"], W - 2 * M, 44, "Regular", 3)
            y = draw_lines(d, l2, f2, M, y + 24 * SS, B["accent"], gap=1.2)
        d.text((M, y + 36 * SS), "— " + params.get("by", ""), font=font(34, "Regular"), fill=B["muted"])
    elif template == "source_card":
        x0, y0, x1 = M + 120 * SS, H * 0.22, W - M - 120 * SS
        ft, lt = fit_text(d, params["title"], x1 - x0 - 120 * SS, 58, "Bold", 3)
        fh, lh = fit_text(d, params.get("highlight", ""), x1 - x0 - 120 * SS, 34, "Medium", 2)
        fx, lx = fit_text(d, params.get("translation", ""), x1 - x0 - 120 * SS, 30, "Regular", 2)
        hgt = 110 * SS + len(lt) * ft.size * 1.18 + 70 * SS + (len(lh) * fh.size * 1.2 + 60 * SS if params.get("highlight") else 0) \
              + (len(lx) * fx.size * 1.2 + 20 * SS if params.get("translation") else 0) + 50 * SS
        y0 = (H - hgt) / 2 - 20 * SS; y1 = y0 + hgt
        d.rounded_rectangle([x0, y0, x1, y1], radius=18 * SS, fill="#F4F1EA")
        d.text((x0 + 60 * SS, y0 + 50 * SS), params["publisher"].upper(), font=font(28, "Bold"), fill="#5B6270")
        f, lines = fit_text(d, params["title"], x1 - x0 - 120 * SS, 58, "Bold", 3)
        y = draw_lines(d, lines, f, x0 + 60 * SS, y0 + 110 * SS, "#11151C")
        d.text((x0 + 60 * SS, y + 30 * SS), params.get("date", ""), font=font(28, "Regular"), fill="#5B6270")
        if params.get("highlight"):
            f3, l3 = fit_text(d, params["highlight"], x1 - x0 - 120 * SS, 34, "Medium", 2)
            yy = y + 100 * SS; d.rectangle([x0 + 50 * SS, yy - 8 * SS, x1 - 50 * SS, yy + len(l3) * f3.size * 1.2 + 4 * SS], fill="#F9E3A8")
            yy = draw_lines(d, l3, f3, x0 + 60 * SS, yy, "#11151C")
            if params.get("translation"):
                f4, l4 = fit_text(d, params["translation"], x1 - x0 - 120 * SS, 30, "Regular", 2)
                draw_lines(d, l4, f4, x0 + 60 * SS, yy + 24 * SS, "#5B6270")
    elif template == "timeline":
        items, hi = params["items"], params.get("highlight", len(params["items"]) - 1)
        y = H * 0.55; x0, x1 = M, W - M; d.line([(x0, y), (x1, y)], fill=B["line"], width=6 * SS)
        step = (x1 - x0) / len(items)  # one slot per item, point in its centre: edge labels stay inside the frame
        for i, it in enumerate(items):
            x = x0 + (i + 0.5) * step; on = i == hi; r = (22 if on else 12) * SS
            d.ellipse([x - r, y - r, x + r, y + r], fill=B["accent"] if on else B["muted"])
            d.text((x, y - 70 * SS), it["date"], font=font(44 if on else 34, "Bold"), fill=B["text"] if on else B["muted"], anchor="ms")
            f, lines = fit_text(d, it["label"], step * 0.9, 30, "Regular", 3)
            for k, ln in enumerate(lines): d.text((x, y + 70 * SS + k * f.size * 1.2), ln, font=f, fill=B["text"] if on else B["muted"], anchor="ma")
    elif template == "photo_kenburns" and photo:
        ph = Image.open(photo).convert("RGB")
        if params.get("fit") == "contain":  # documents, screenshots: never crop
            sc = min(W * 0.8 / ph.width, H * 0.7 / ph.height); ph = ph.resize((int(ph.width * sc), int(ph.height * sc)), Image.LANCZOS)
            img.paste(ph, ((W - ph.width) // 2, int((H - ph.height) * 0.42)))
        else:  # full-bleed "cover" crop, focus point optional (0..1)
            sc = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1), Image.LANCZOS)
            fx, fy = params.get("focus", [0.5, 0.5]); x = int((ph.width - W) * fx); y = int((ph.height - H) * fy)
            img = ph.crop((x, y, x + W, y + H))
        shade = Image.new("L", (1, H)); [shade.putpixel((0, i), int(200 * max(0, (i / H - 0.62) / 0.38) ** 1.4)) for i in range(H)]
        img = Image.composite(Image.new("RGB", (W, H), B["bg"]), img, shade.resize((W, H))); d = ImageDraw.Draw(img)
        if params.get("credit"): d.text((W - 40 * SS, H - 40 * SS), params["credit"], font=font(20), fill=B["muted"], anchor="rs")
    elif template == "clip_placeholder":  # where a licensed / approved quotation clip will be inserted
        d.rectangle([0, 0, W, H], fill="#161D2B")
        cx, cy, r = W / 2, H * 0.36, 70 * SS
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=B["accent"], width=6 * SS)
        d.polygon([(cx - 22 * SS, cy - 36 * SS), (cx - 22 * SS, cy + 36 * SS), (cx + 40 * SS, cy)], fill=B["accent"])
        d.text((cx, cy + 120 * SS), "KLIP – vložit po schválení práv", font=font(30, "Bold"), fill=B["accent"], anchor="ma")
        d.text((cx, cy + 170 * SS), params.get("ref", ""), font=font(26, "Regular"), fill=B["muted"], anchor="ma")
        if params.get("sub"):  # Czech subtitle line, like the final clip will have
            f, lines = fit_text(d, params["sub"], W - 2 * M, 44, "SemiBold", 2)
            y0 = H - 220 * SS
            for k, ln in enumerate(lines):
                tw = d.textlength(ln, font=f); y = y0 + k * f.size * 1.25
                d.rectangle([cx - tw / 2 - 18 * SS, y - 8 * SS, cx + tw / 2 + 18 * SS, y + f.size * 1.1], fill="#000000")
                d.text((cx, y), ln, font=f, fill="#FFFFFF", anchor="ma")
    elif template == "kinetic":  # one huge statement, optional highlighted word
        f, lines = fit_text(d, params["text"], W - 2 * M, 140, "Black" if True else "Bold", 3)
        y = H / 2 - len(lines) * f.size * 0.62
        hl = params.get("highlight", "").lower()
        for ln in lines:
            x = M
            for w in ln.split(" "):
                col = B["accent"] if hl and w.lower().strip(".,?!:") == hl else B["text"]
                d.text((x, y), w, font=f, fill=col); x += d.textlength(w + " ", font=f)
            y += f.size * 1.12
    else:  # broll_generic / fallback: big keyword
        f, lines = fit_text(d, params.get("text", ""), W - 2 * M, 80, "SemiBold", 3); draw_lines(d, lines, f, M, H * 0.4, B["text"])
    source_line(d, source_text)
    return img
