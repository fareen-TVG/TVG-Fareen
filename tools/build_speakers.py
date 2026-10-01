"""Generate the speaker directory, speaker profiles, topic pages and sitemap.

Run from the repository root after editing data/speakers.json:

    python3 tools/build_speakers.py

Shared header/footer markup is copied from about.html, so edit the nav or
footer there and re-run this script to update the generated pages.
"""
import html
import json
import os
import re

SITE = 'https://talentverseglobal.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data = json.load(open(os.path.join(ROOT, 'data', 'speakers.json')))
CATS = {c['slug']: c['name'] for c in data['categories']}
SPEAKERS = data['speakers']

ORG = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": SITE + "/#organization",
    "name": "TalentVerse Global",
    "url": SITE + "/",
    "logo": SITE + "/Images/icon-512.png",
    "email": "unlock@talentverseglobal.com",
    "telephone": "+919820984063",
}

TOPIC_INTROS = {
    'government-policy': 'Diplomats, parliamentarians and economists who explain policy, geopolitics and India’s place in the world.',
    'business-leadership': 'Founders, CEOs and strategists who share what it really takes to build, scale and lead.',
    'sports': 'Champions and coaches who bring the discipline, resilience and teamwork of elite sport to your stage.',
    'defence': 'Decorated officers and veterans who speak on courage, leadership under pressure and national security.',
    'authors': 'Bestselling authors, journalists and thinkers who turn big ideas and stories into memorable talks.',
    'health-wellbeing': 'Doctors, nutritionists and wellness experts who help teams perform better and live healthier.',
    'spiritual': 'Spiritual leaders and mindfulness teachers who speak on purpose, stress and inner balance.',
    'celebrities': 'Actors and filmmakers who bring star power, storytelling and personal journeys to your event.',
    'digital-creators': 'Creators and entrepreneurs who understand today’s audiences, money and the creator economy.',
    'comedians': 'Stand-up comedians who bring clean, relatable humour to corporate events and celebrations.',
    'chefs': 'Celebrity and Michelin-starred chefs who speak on creativity, entrepreneurship and food culture.',
}


def esc(s):
    return html.escape(s, quote=True)


def initials(name):
    words = [w for w in re.sub(r'\(.*?\)', '', name).replace('.', ' ').split()
             if w.lower() not in ('dr', 'chef', 'lt', 'gen', 'general', 'major', 'captain', 'colonel', 'retd', 'swami', 'sri', 'bk')]
    return (words[0][0] + (words[-1][0] if len(words) > 1 else '')).upper() if words else '?'


def first_sentence(text, limit=155):
    s = text.split('. ')[0].rstrip('.') + '.'
    return s if len(s) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'


# ── shared chrome, taken from about.html ──
about = open(os.path.join(ROOT, 'about.html')).read()
HEADER = about[about.index('<body>'):about.index('<main id="main">')]
HEADER = HEADER.replace(' class="active" aria-current="page"', '')
FOOTER = about[about.index('</main>'):]


def relink(markup, prefix):
    if not prefix:
        return markup
    return re.sub(r'(href|src)="(?!https?:|#|mailto:|tel:|/)([^"]+)"', lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"', markup)


def page(path, title, desc, body, ld=(), og_image='Images/og-image.jpg', active=None):
    depth = path.count('/')
    prefix = '../' * depth
    url = SITE + '/' + path
    ld_html = '\n'.join('  <script type="application/ld+json">\n%s\n  </script>' % json.dumps(x, ensure_ascii=False, indent=2) for x in (ORG,) + tuple(ld))
    header = HEADER
    if active:
        header = header.replace(f'<li><a href="{active}">', f'<li><a href="{active}" class="active" aria-current="page">', 1)
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="index, follow" />
  <meta name="theme-color" content="#7C3AED" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="TalentVerse Global" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}/{og_image}" />
  <meta property="og:locale" content="en_IN" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{SITE}/{og_image}" />

  <link rel="icon" type="image/png" href="favicon.png" />
  <link rel="apple-touch-icon" href="Images/apple-touch-icon.png" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/styles.css" />
{ld_html}
</head>
{header}<main id="main">
{body}
  </main>
"""
    out = relink(out, prefix) + relink(FOOTER[len('</main>'):].lstrip('\n'), prefix)
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(out)


def crumbs(*items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + '/' + u}
                                for i, (n, u) in enumerate(items)]}


def photo_html(s, cls, lazy=True, eager_priority=False):
    if s['photo']:
        attrs = ' loading="lazy"' if lazy else (' fetchpriority="high"' if eager_priority else '')
        return f'<img class="{cls}" src="{s["photo"]}" alt="{esc(s["name"])}"{attrs} />'
    return f'<div class="{cls} initials" aria-hidden="true">{esc(initials(s["name"]))}</div>'


def card(s):
    # Links are root-relative here; page() rewrites them for pages in subfolders.
    return f"""      <a class="roster-card" href="speakers/{s['slug']}.html" data-topic="{s['category']}" data-name="{esc(s['name'].lower())}">
        <div class="roster-photo">{photo_html(s, 'roster-img')}</div>
        <div class="roster-body">
          <div class="slc-topic">{esc(CATS[s['category']])}</div>
          <h2 class="roster-name">{esc(s['name'])}</h2>
          <p class="roster-title">{esc(s['title'])}</p>
        </div>
      </a>"""


# ── directory ──
filters = '\n'.join(
    ['      <button type="button" class="filter-btn active" aria-pressed="true" onclick="filterSpeakers(this, \'all\')">All</button>'] +
    [f'      <button type="button" class="filter-btn" aria-pressed="false" onclick="filterSpeakers(this, \'{c}\')">{esc(n)}</button>' for c, n in CATS.items()])
directory = f"""    <div class="page-hero">
      <div class="eyebrow">Our Roster</div>
      <h1 class="display">600+ Speakers<br><span class="accent-text">for Every Stage</span></h1>
      <p>Diplomats, sporting legends, founders, actors, comedians and chefs — find the right voice for your conference, offsite or celebration, then enquire in one click.</p>
    </div>

    <div class="filters">
      <label class="search-box"><span class="visually-hidden">Search speakers</span><input type="search" id="speaker-search" placeholder="Search by name or topic…" autocomplete="off" /></label>
{filters}
    </div>

    <div class="speakers-list">
      <p class="roster-count" id="roster-count" aria-live="polite">{len(SPEAKERS)} speakers</p>
      <div class="roster-grid" id="speakers-grid">
{chr(10).join(card(s) for s in sorted(SPEAKERS, key=lambda x: x['photo'] is None))}
      </div>
      <p class="roster-empty" id="roster-empty" hidden>No speakers match that search. <a href="contact.html">Tell us what you need</a> and we’ll find the right person.</p>
    </div>

    <div class="cta-banner">
      <h2 class="display">Can't find who<br>you're looking for?</h2>
      <a class="btn-primary" href="contact.html" style="font-size:0.9rem;padding:1rem 2.4rem;">Talk to Our Team →</a>
    </div>"""
page('speakers.html', 'Book Keynote Speakers in India | TalentVerse Global Speaker Roster',
     'Book keynote speakers, celebrities, sports legends, comedians and chefs for corporate events in India. Browse the TalentVerse Global roster and enquire for availability.',
     directory, ld=[crumbs(('Home', ''), ('Speakers', 'speakers.html'))], active='speakers.html')

# ── profiles ──
by_cat = {}
for s in SPEAKERS:
    by_cat.setdefault(s['category'], []).append(s)

for s in SPEAKERS:
    cat = CATS[s['category']]
    related = [r for r in by_cat[s['category']] if r['slug'] != s['slug']][:4]
    q = s['name'].replace(' ', '%20')
    body = f"""    <div class="profile">
      <div>
        {photo_html(s, 'profile-photo', lazy=False, eager_priority=True)}
      </div>
      <div>
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="speakers.html">Speakers</a> / <a href="topics/{s['category']}.html">{esc(cat)}</a> / {esc(s['name'])}</nav>
        <div class="eyebrow">{esc(cat)}</div>
        <h1 class="display">{esc(s['name'])}</h1>
        <div class="slc-role">{esc(s['title'])}</div>
        <p>{esc(s['bio'])}</p>
        <div class="hero-btns">
          <a class="btn-primary" href="contact.html?speaker={q}">Enquire about {esc(s['name'])} →</a>
          <a class="btn-ghost" href="topics/{s['category']}.html">See all {esc(cat)}</a>
        </div>
      </div>
    </div>
"""
    if related:
        body += f"""
    <section class="section related">
      <h2 class="display" style="font-size:clamp(1.6rem,3vw,2.2rem);margin-bottom:2rem;">Similar speakers</h2>
      <div class="roster-grid">
{chr(10).join(card(r) for r in related)}
      </div>
    </section>
"""
    body += f"""
    <div class="cta-banner">
      <h2 class="display">Want {esc(s['name'])}<br><span class="accent-text">at your event?</span></h2>
      <a class="btn-primary" href="contact.html?speaker={q}" style="font-size:0.9rem;padding:1rem 2.4rem;">Check Availability →</a>
    </div>"""
    person = {"@type": "Person", "name": s['name'], "jobTitle": s['title'], "description": s['bio']}
    if s['photo']:
        person['image'] = SITE + '/' + s['photo']
    page(f"speakers/{s['slug']}.html",
         f"Book {s['name']} as a Speaker | TalentVerse Global",
         f"Book {s['name']} — {s['title']} — for your next event. {first_sentence(s['bio'], 100)}"[:300],
         body,
         ld=[crumbs(('Home', ''), ('Speakers', 'speakers.html'), (cat, f"topics/{s['category']}.html"), (s['name'], f"speakers/{s['slug']}.html")),
             {"@context": "https://schema.org", "@type": "ProfilePage", "url": f"{SITE}/speakers/{s['slug']}.html", "mainEntity": person}],
         og_image=s['photo'] or 'Images/og-image.jpg')

# ── topic pages ──
for cslug, cname in CATS.items():
    group = by_cat[cslug]
    body = f"""    <div class="page-hero">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="speakers.html">Speakers</a> / {esc(cname)}</nav>
      <div class="eyebrow">{len(group)} speakers</div>
      <h1 class="display">{esc(cname)} <span class="accent-text">Speakers</span></h1>
      <p>{esc(TOPIC_INTROS[cslug])}</p>
    </div>

    <div class="speakers-list">
      <div class="roster-grid">
{chr(10).join(card(s) for s in group)}
      </div>
    </div>

    <div class="cta-banner">
      <h2 class="display">Need help choosing<br>the right <span class="accent-text">speaker?</span></h2>
      <a class="btn-primary" href="contact.html" style="font-size:0.9rem;padding:1rem 2.4rem;">Get a Free Shortlist →</a>
    </div>"""
    page(f"topics/{cslug}.html",
         f"{cname} Speakers to Book in India | TalentVerse Global",
         f"Book {cname.lower()} speakers for corporate events, conferences and summits. {TOPIC_INTROS[cslug]}",
         body, ld=[crumbs(('Home', ''), ('Speakers', 'speakers.html'), (cname, f'topics/{cslug}.html'))])

# ── sitemap ──
static = [('', '1.0', 'weekly'), ('speakers.html', '0.9', 'weekly'), ('contact.html', '0.8', 'yearly'),
          ('about.html', '0.6', 'yearly'), ('journal.html', '0.5', 'monthly')]
urls = static + [(f'topics/{c}.html', '0.8', 'monthly') for c in CATS] + [(f"speakers/{s['slug']}.html", '0.7', 'monthly') for s in SPEAKERS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, p, c in urls:
    sm += f"  <url><loc>{SITE}/{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n"
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm + '</urlset>\n')

print(f"Built speakers.html, {len(SPEAKERS)} profiles, {len(CATS)} topic pages, sitemap with {len(urls)} URLs")
