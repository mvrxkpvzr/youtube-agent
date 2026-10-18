"""2.5D / 3D motion-design shots rendered frame by frame (numpy + OpenCV) and piped to FFmpeg.

panel3d   – an image (screenshot, document, card) on a plane in 3D space; the camera drifts/rotates,
            with drop shadow, light sweep, depth-of-field, chromatic aberration, grain and vignette.
parallax  – foreground cutout (RGBA) over a background; layers move at different speeds + zoom,
            background is blurred and graded (the "subject pops out" look).
"""
import math, subprocess
import numpy as np, cv2
from .common import ffmpeg

W, H, FPS = 1920, 1080, 25

def ease(t):  # smooth in-out
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))

def rot(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    X = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Y = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Z = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Z @ Y @ X

def project(img_w, img_h, rx, ry, rz, dist, scale, cx=0.0, cy=0.0, f=1600):
    """Return the 4 projected corners of a plane of size img_w x img_h (pixels), centred, rotated, at distance."""
    hw, hh = img_w * scale / 2, img_h * scale / 2
    pts = np.array([[-hw, -hh, 0], [hw, -hh, 0], [hw, hh, 0], [-hw, hh, 0]], float)
    p = pts @ rot(rx, ry, rz).T
    p[:, 2] += dist
    u = f * p[:, 0] / p[:, 2] + W / 2 + cx
    v = f * p[:, 1] / p[:, 2] + H / 2 + cy
    return np.stack([u, v], 1).astype(np.float32), p[:, 2]

def finish(frame, t, grain=0.035, ca=2.0, vignette=0.55, seed=0):
    f = frame.astype(np.float32)
    if ca:  # chromatic aberration: shift R and B in opposite directions, stronger at edges
        M1 = np.float32([[1 + ca / W, 0, -ca / 2], [0, 1 + ca / H, -ca / 2]])
        M2 = np.float32([[1 - ca / W, 0, ca / 2], [0, 1 - ca / H, ca / 2]])
        f[..., 2] = cv2.warpAffine(f[..., 2], M1, (W, H), borderMode=cv2.BORDER_REFLECT)
        f[..., 0] = cv2.warpAffine(f[..., 0], M2, (W, H), borderMode=cv2.BORDER_REFLECT)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    f *= (1 - vignette * np.clip(r - 0.35, 0, 1) ** 1.6)[..., None]
    rng = np.random.default_rng(seed + int(t * 1000))
    f += rng.normal(0, 255 * grain, (H, W, 1)).astype(np.float32)
    return np.clip(f, 0, 255).astype(np.uint8)

_VIG_CACHE = {}

def background(src, darken=0.35, blur=61, tint=(1.0, 0.9, 0.85)):
    bg = cv2.resize(src[..., :3], (W, H), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(bg, (0, 0), blur)
    return np.clip(bg.astype(np.float32) * darken * np.array(tint)[::-1], 0, 255).astype(np.uint8)

def writer(out, fps=FPS):
    return subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                             "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                            stdin=subprocess.PIPE)

def panel3d(img_path, out, dur=4.0, start=(14, -24, -3, 1.0), end=(6, -8, -1, 1.12), bg_path=None, sweep=True, seed=1):
    """start/end = (rx, ry, rz, zoom). Camera eases between them; slight handheld drift added."""
    src = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if src.shape[2] == 4: src = cv2.cvtColor(src, cv2.COLOR_BGRA2BGR)
    h, w = src.shape[:2]
    base_scale = min(W * 0.78 / w, H * 0.72 / h)
    bg = background(cv2.imread(bg_path) if bg_path else src)
    n = int(round(dur * FPS)); p = writer(out)
    for i in range(n):
        t = i / max(n - 1, 1); e = ease(t)
        rx, ry, rz, zoom = [a + (b - a) * e for a, b in zip(start, end)]
        drift = (6 * math.sin(2 * math.pi * (t * 0.7 + 0.1)), 4 * math.sin(2 * math.pi * t * 0.9))
        corners, depth = project(w, h, rx, ry, rz, 1600 / zoom, base_scale, *drift)
        frame = cv2.warpAffine(bg, np.float32([[1 + 0.03 * e, 0, -W * 0.015 * e], [0, 1 + 0.03 * e, -H * 0.015 * e]]), (W, H))
        # drop shadow
        sh = np.zeros((H, W), np.float32)
        cv2.fillConvexPoly(sh, (corners + np.float32([28, 40])).astype(np.int32), 1.0)
        sh = cv2.GaussianBlur(sh, (0, 0), 30)
        frame = (frame.astype(np.float32) * (1 - 0.65 * sh[..., None])).astype(np.uint8)
        # panel
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), corners)
        warped = cv2.warpPerspective(src, M, (W, H), flags=cv2.INTER_LINEAR)
        mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (W, H)).astype(np.float32) / 255
        # depth of field: far edge (larger z) gets blurred
        far = np.argmax(depth); dof = cv2.GaussianBlur(warped, (0, 0), 3.2)
        grad = np.zeros((H, W), np.float32)
        a, b = corners[far], corners[(far + 2) % 4]
        yy, xx = np.mgrid[0:H, 0:W]
        dvec = b - a; L = float(np.hypot(*dvec)) or 1.0
        proj = ((xx - a[0]) * dvec[0] + (yy - a[1]) * dvec[1]) / (L * L)
        grad = np.clip(1 - proj * 1.6, 0, 1) ** 1.5
        warped = (warped * (1 - grad[..., None]) + dof * grad[..., None]).astype(np.float32)
        if sweep:  # moving specular light band
            pos = -0.3 + 1.6 * t
            band = np.exp(-((proj - pos) ** 2) / 0.006) * 0.22
            warped = warped + 255 * band[..., None]
        frame = np.clip(frame * (1 - mask[..., None]) + warped * mask[..., None], 0, 255)
        # thin bright edge
        cv2.polylines(frame, [corners.astype(np.int32)], True, (255, 255, 255), 1, cv2.LINE_AA)
        p.stdin.write(finish(np.clip(frame, 0, 255).astype(np.uint8), t, seed=seed).tobytes())
    p.stdin.close(); p.wait()
    return out

def parallax(fg_rgba_path, bg_path, out, dur=4.0, push=0.10, fg_shift=60, bg_shift=-30, seed=2):
    """Cutout subject (RGBA) moves faster than the blurred, graded background; slow push-in on both."""
    fg = cv2.imread(fg_rgba_path, cv2.IMREAD_UNCHANGED); bgimg = cv2.imread(bg_path)
    bg = cv2.resize(bgimg, (W, H)); bg = cv2.GaussianBlur(bg, (0, 0), 9)
    gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)[..., None]
    bg = np.clip(0.55 * bg + 0.45 * gray, 0, 255) * 0.55  # desaturate + darken
    fh, fw = fg.shape[:2]; s0 = H * 0.86 / fh
    n = int(round(dur * FPS)); p = writer(out)
    for i in range(n):
        t = i / max(n - 1, 1); e = ease(t)
        zb = 1 + push * 0.5 * e; zf = 1 + push * e
        Mb = np.float32([[zb, 0, (1 - zb) * W / 2 + bg_shift * e], [0, zb, (1 - zb) * H / 2]])
        frame = cv2.warpAffine(bg.astype(np.uint8), Mb, (W, H), borderMode=cv2.BORDER_REFLECT).astype(np.float32)
        s = s0 * zf; x = W / 2 - fw * s / 2 + fg_shift * e; y = H - fh * s + 20
        Mf = np.float32([[s, 0, x], [0, s, y]])
        layer = cv2.warpAffine(fg, Mf, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0)).astype(np.float32)
        al = layer[..., 3:4] / 255
        glow = cv2.GaussianBlur(al, (0, 0), 25)[..., None] if al.ndim == 2 else cv2.GaussianBlur(al[..., 0], (0, 0), 25)[..., None]
        frame = frame + 90 * glow * np.array([0.2, 0.7, 1.0])  # rim glow (BGR: warm)
        frame = frame * (1 - al) + layer[..., :3] * al
        p.stdin.write(finish(np.clip(frame, 0, 255).astype(np.uint8), t, seed=seed).tobytes())
    p.stdin.close(); p.wait()
    return out
