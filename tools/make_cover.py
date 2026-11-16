"""Make a blog cover image for an article.

    python3 tools/make_cover.py content/blog/<slug>.md

Layout: dark panel on the left with the logo, an orange label, a big title and
a subtitle; the right half shows the featured speakers in a stage spotlight.
Saves Images/blog/<slug>.jpg at 1200x630 (the size used for link previews).

Optional fields in the article header:
  cover_tag:      short label, e.g. Speaker roundup
  cover_title:    big title, e.g. 10 Motivational Speakers
  cover_subtitle: line under it, e.g. for your sales kick-off
  cover_speakers: up to 3 speaker slugs, lead first (default: first 3 in the article)

Speaker cut-outs come from tools/cutouts/<slug>.png when present (best edges);
otherwise the lavender photo background is keyed out.
"""
import json, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

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


def cutout(slug, photo):
    p = os.path.join(ROOT, 'tools', 'cutouts', slug + '.png')
    if os.path.exists(p):
        return Image.open(p).convert('RGBA')
    im = np.asarray(Image.open(os.path.join(ROOT, photo)).convert('RGB')).astype(float)
    d = np.sqrt(((im - np.array([244, 236, 254.])) ** 2).sum(-1))
    a = (np.clip((d - 18) / 30, 0, 1) * 255).astype('uint8')
    return Image.fromarray(np.dstack([im.astype('uint8'), a]), 'RGBA')


def stage(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(float)
    base = np.array([26, 8, 48.])
    glow = np.array([157, 59, 232.])
    r = np.sqrt(((x - w * 0.5) / (w * 0.75)) ** 2 + ((y - h * 0.05) / (h * 0.95)) ** 2)
    t = np.clip(1 - r, 0, 1)[..., None] ** 1.6
    img = base + (glow - base) * t
    return Image.fromarray(img.clip(0, 255).astype('uint8'), 'RGB')


def make(md_path):
    slug = os.path.splitext(os.path.basename(md_path))[0]
    text = open(md_path, encoding='utf-8').read()
    meta = dict(re.findall(r'^(\w+):\s*(.+?)\s*$', text.split('---')[1], re.M))
    data = json.load(open(os.path.join(ROOT, 'data', 'speakers.json')))
    by = {s['slug']: s for s in data['speakers']}
    in_post = list(dict.fromkeys(re.findall(r'\[\[speaker:([a-z0-9-]+)\]\]', text)))
    chosen = [s.strip() for s in meta.get('cover_speakers', '').split(',') if s.strip()] or in_post[:3]
    chosen = [s for s in chosen if s in by and by[s]['photo']][:3]

    canvas = Image.new('RGB', (W, H), INK)
    # right: stage with speakers
    rw = 600
    right = stage(rw, H).convert('RGBA')
    spots = {1: [(0.5, 0.88, 1.0)],
             2: [(0.32, 0.74, 0.8), (0.66, 0.88, 1.0)],
             3: [(0.2, 0.7, 0.7), (0.8, 0.7, 0.7), (0.5, 0.86, 1.0)]}[max(1, len(chosen))]
    order = chosen[1:] + chosen[:1]           # lead is drawn last, in front
    for s, (cx, scale, bright) in zip(order, spots):
        c = cutout(s, by[s]['photo'])
        h = int(H * 0.93 * scale)
        c = c.resize((int(c.width * h / c.height), h), Image.LANCZOS)
        if bright < 1:
            rgb = ImageEnhance.Brightness(c.convert('RGB')).enhance(bright)
            rgb.putalpha(c.split()[3])
            c = rgb
        glow = Image.new('RGBA', c.size, (200, 150, 255, 0))
        glow.putalpha(c.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.35)))
        x = int(rw * cx - c.width / 2)
        layer = Image.new('RGBA', right.size, (0, 0, 0, 0))
        layer.paste(glow, (x, H - h), glow)
        layer.paste(c, (x, H - h), c)
        right.alpha_composite(layer)
    floor = Image.new('RGBA', (rw, 140), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor)
    for i in range(140):
        fd.line([(0, i), (rw, i)], fill=(14, 4, 26, int(150 * i / 140)))
    right.alpha_composite(floor, (0, H - 140))
    canvas.paste(right.convert('RGB'), (W - rw, 0))

    # left: logo, label, title, subtitle
    d = ImageDraw.Draw(canvas)
    hq = os.path.join(ROOT, 'Images', 'logo-hq.png')
    logo = Image.open(hq if os.path.exists(hq) else os.path.join(ROOT, 'Images', 'logo.webp')).convert('RGBA')
    lh = 92
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    canvas.paste(logo, (60, 52), logo)
    tag = meta.get('cover_tag', 'TalentVerse Global blog').upper()
    ft = font('Inter-Bold.otf', 19)
    tw = d.textlength(tag, font=ft)
    y = 190
    d.rounded_rectangle((60, y, 60 + tw + 34, y + 38), 19, fill=ORANGE)
    d.text((77, y + 8), tag, font=ft, fill=INK)
    title = meta.get('cover_title', meta.get('title', '')).upper()
    size = 62
    while True:
        fh = font('InterDisplay-Black.otf', size)
        lines = wrap(d, title, fh, 490)
        short_first = len(lines) > 1 and len(lines[0]) <= 3
        if (len(lines) <= 3 and not short_first) or size <= 40:
            break
        size -= 4
    y += 62
    for line in lines:
        d.text((60, y), line, font=fh, fill=(255, 255, 255))
        y += int(size * 1.05)
    sub = meta.get('cover_subtitle', '')
    if sub:
        fs = font('Inter-Medium.otf', 28)
        y += 14
        for line in wrap(d, sub, fs, 470):
            d.text((60, y), line, font=fs, fill=(226, 212, 245))
            y += 36
    out = os.path.join(ROOT, 'Images', 'blog', slug + '.jpg')
    canvas.save(out, quality=88, optimize=True, progressive=True)
    print(out, chosen)


if __name__ == '__main__':
    for f in sys.argv[1:]:
        make(f)
