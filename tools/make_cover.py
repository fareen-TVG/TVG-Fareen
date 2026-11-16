"""Make a blog cover image for an article.

    python3 tools/make_cover.py content/blog/<slug>.md

Centred text design: dark background with a purple spotlight glow, the
logo, an orange label, a big title, a subtitle and the website address.
Saves Images/blog/<slug>.jpg at 1200x630 (the size used for link previews).

Optional fields in the article header:
  cover_tag:      short label, e.g. Speaker roundup
  cover_title:    big title, e.g. 10 Motivational Speakers
  cover_subtitle: line under it, e.g. for your sales kick-off in India
"""
import os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
FONTS = '/usr/share/fonts/opentype/inter/'
INK = (20, 8, 31)
ORANGE = (255, 140, 0)


def font(name, size):
    return ImageFont.truetype(FONTS + name, size)


def wrap(draw, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def background():
    y, x = np.mgrid[0:H, 0:W].astype(float)
    base = np.array(INK, float)
    img = np.broadcast_to(base, (H, W, 3)).copy()
    for cx, cy, rx, ry, col, k in [(600, -40, 820, 560, (157, 59, 232), 0.9),
                                   (600, 700, 520, 260, (255, 140, 0), 0.18)]:
        r = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
        t = (np.clip(1 - r, 0, 1) ** 1.8 * k)[..., None]
        img = img + (np.array(col, float) - img) * t
    return Image.fromarray(img.clip(0, 255).astype('uint8'), 'RGB')


def make(md_path):
    slug = os.path.splitext(os.path.basename(md_path))[0]
    text = open(md_path, encoding='utf-8').read()
    meta = dict(re.findall(r'^(\w+):\s*(.+?)\s*$', text.split('---')[1], re.M))

    canvas = background()
    d = ImageDraw.Draw(canvas)
    cx = W // 2
    hq = os.path.join(ROOT, 'Images', 'logo-hq.png')
    logo = Image.open(hq if os.path.exists(hq) else os.path.join(ROOT, 'Images', 'logo.webp')).convert('RGBA')
    lh = 84
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)

    tag = meta.get('cover_tag', 'TalentVerse Global blog').upper()
    ft = font('Inter-Bold.otf', 21)
    tw = d.textlength(tag, font=ft)

    title = meta.get('cover_title', meta.get('title', '')).upper()
    size = 84
    while True:
        fh = font('InterDisplay-Black.otf', size)
        lines = wrap(d, title, fh, 1000)
        if len(lines) <= 2 or size <= 48:
            break
        size -= 4
    line_h = int(size * 1.04)
    sub = meta.get('cover_subtitle', '')
    fs = font('Inter-Medium.otf', 32)

    # total height of the stack, so it sits in the middle of the image
    stack = lh + 30 + 42 + 26 + len(lines) * line_h + (14 + 40 if sub else 0) + 28 + 10
    y = (H - stack) // 2 - 10
    canvas.paste(logo, (cx - logo.width // 2, y), logo)
    y += lh + 30
    d.rounded_rectangle((cx - tw / 2 - 19, y, cx + tw / 2 + 19, y + 42), 21, fill=ORANGE)
    d.text((cx, y + 21), tag, font=ft, fill=INK, anchor='mm')
    y += 42 + 26
    for line in lines:
        d.text((cx, y), line, font=fh, fill=(255, 255, 255), anchor='ma')
        y += line_h
    if sub:
        y += 14
        d.text((cx, y), sub, font=fs, fill=(226, 212, 245), anchor='ma')
        y += 40
    d.rounded_rectangle((cx - 70, y + 28, cx + 70, y + 38), 5, fill=ORANGE)

    fw = font('Inter-SemiBold.otf', 20)
    d.text((cx, H - 34), 'talentverseglobal.com', font=fw, fill=(200, 184, 225), anchor='ms')

    out = os.path.join(ROOT, 'Images', 'blog', slug + '.jpg')
    canvas.save(out, quality=88, optimize=True, progressive=True)
    print(out)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        make(f)
