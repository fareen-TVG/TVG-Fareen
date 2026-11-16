"""Make a blog cover collage from the speakers featured in an article.

    python3 tools/make_cover.py content/blog/<slug>.md

Reads every [[speaker:slug]] in the article, lays their photos out as rounded
tiles on the brand purple, and saves Images/blog/<slug>.jpg (1200x630, the
size social networks use for link previews).
"""
import json, os, re, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630


def gradient():
    top, bottom = (157, 59, 232), (98, 14, 176)
    g = Image.new('RGB', (W, H))
    px = g.load()
    for y in range(H):
        for x in range(W):
            t = (x / W * 0.6 + y / H * 0.4)
            px[x, y] = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
    return g


def rounded(img, r):
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.size[0] - 1, img.size[1] - 1), r, fill=255)
    return m


def make(md_path):
    slug = os.path.splitext(os.path.basename(md_path))[0]
    text = open(md_path, encoding='utf-8').read()
    slugs = list(dict.fromkeys(re.findall(r'\[\[speaker:([a-z0-9-]+)\]\]', text)))
    data = json.load(open(os.path.join(ROOT, 'data', 'speakers.json')))
    by = {s['slug']: s for s in data['speakers']}
    photos = [by[s]['photo'] for s in slugs if s in by and by[s]['photo']]
    n = len(photos)
    cols = (n + 1) // 2 if n > 4 else n
    rows = (n + cols - 1) // cols
    gap, pad = 16, 36
    tw = min((W - 2 * pad - (cols - 1) * gap) / cols, ((H - 2 * pad - (rows - 1) * gap) / rows) * 3 / 4)
    th = tw * 4 / 3
    tw, th = int(tw), int(th)
    canvas = gradient()
    for i, p in enumerate(photos):
        r, c = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        row_w = in_row * tw + (in_row - 1) * gap
        x0 = (W - row_w) // 2 + c * (tw + gap)
        y0 = (H - (rows * th + (rows - 1) * gap)) // 2 + r * (th + gap)
        tile = Image.open(os.path.join(ROOT, p)).convert('RGB').resize((tw, th), Image.LANCZOS)
        canvas.paste(tile, (x0, y0), rounded(tile, 18))
    out = os.path.join(ROOT, 'Images', 'blog', slug + '.jpg')
    canvas.save(out, quality=86, optimize=True, progressive=True)
    print(out, n, 'speakers')


if __name__ == '__main__':
    for f in sys.argv[1:]:
        make(f)
