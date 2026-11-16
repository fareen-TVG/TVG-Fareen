"""Make a blog cover image for an article.

    python3 tools/make_cover.py content/blog/<slug>.md

Full-width text design: dark background with a purple spotlight glow, the
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
    for cx, cy, rx, ry, col, k in [(1020, 60, 640, 560, (157, 59, 232), 0.95),
                                   (1150, 640, 420, 300, (255, 140, 0), 0.22)]:
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
    hq = os.path.join(ROOT, 'Images', 'logo-hq.png')
    logo = Image.open(hq if os.path.exists(hq) else os.path.join(ROOT, 'Images', 'logo.webp')).convert('RGBA')
    lh = 92
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    canvas.paste(logo, (70, 56), logo)

    tag = meta.get('cover_tag', 'TalentVerse Global blog').upper()
    ft = font('Inter-Bold.otf', 21)
    tw = d.textlength(tag, font=ft)
    y = 206
    d.rounded_rectangle((70, y, 70 + tw + 38, y + 42), 21, fill=ORANGE)
    d.text((89, y + 9), tag, font=ft, fill=INK)

    title = meta.get('cover_title', meta.get('title', '')).upper()
    size = 84
    while True:
        fh = font('InterDisplay-Black.otf', size)
        lines = wrap(d, title, fh, 900)
        if len(lines) <= 2 or size <= 48:
            break
        size -= 4
    y += 70
    for line in lines:
        d.text((70, y), line, font=fh, fill=(255, 255, 255))
        y += int(size * 1.04)

    sub = meta.get('cover_subtitle', '')
    if sub:
        fs = font('Inter-Medium.otf', 32)
        y += 10
        d.text((70, y), sub, font=fs, fill=(226, 212, 245))
        y += 44
    d.rounded_rectangle((70, y + 22, 70 + 140, y + 32), 5, fill=ORANGE)

    fw = font('Inter-SemiBold.otf', 22)
    site = 'talentverseglobal.com'
    d.text((W - 70 - d.textlength(site, font=fw), H - 62), site, font=fw, fill=(226, 212, 245))

    out = os.path.join(ROOT, 'Images', 'blog', slug + '.jpg')
    canvas.save(out, quality=88, optimize=True, progressive=True)
    print(out)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        make(f)
