"""Build the whole TalentVerse Global website.

Run from the repository root:

    python3 tools/build_site.py

Speaker data lives in data/speakers.json. Page copy, navigation and footer
live in this file. Every .html page, plus sitemap.xml, is generated, so edit
here (or the JSON) rather than the HTML output.
"""
import html
import json
import os
import re

SITE = 'https://talentverseglobal.com'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = 'unlock@talentverseglobal.com'
PHONE = '+919820984063'
PHONE_DISPLAY = '+91 98209 84063'
WHATSAPP = 'https://wa.me/919820984063?text=Hi%20TalentVerse%20Global%2C%20I%27d%20like%20to%20book%20a%20speaker.'

data = json.load(open(os.path.join(ROOT, 'data', 'speakers.json')))
CATS = {c['slug']: c['name'] for c in data['categories']}
SPEAKERS = data['speakers']
BY_SLUG = {s['slug']: s for s in SPEAKERS}
BY_CAT = {}
for s in SPEAKERS:
    BY_CAT.setdefault(s['category'], []).append(s)

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
FEATURED = ['navtej-sarna', 'anil-kumble', 'anupam-kher', 'vineeta-singh', 'jonty-rhodes', 'radhika-gupta', 'boman-irani', 'aman-gupta']
HERO_PHOTOS = ['anupam-kher', 'vineeta-singh', 'anil-kumble']

ORG = {
    "@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization",
    "name": "TalentVerse Global", "url": SITE + "/", "logo": SITE + "/Images/icon-512.png",
    "image": SITE + "/Images/og-image.jpg",
    "description": "Speaker bureau booking keynote speakers, celebrities, sports legends, comedians and chefs for events in India.",
    "email": EMAIL, "telephone": PHONE,
    "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": EMAIL, "telephone": PHONE, "areaServed": "IN", "availableLanguage": ["en", "hi"]},
}

NAV = [('speakers.html', 'Speakers'), ('topics.html', 'Topics'), ('how-it-works.html', 'How it works'), ('contact.html', 'Contact')]


def esc(s):
    return html.escape(s, quote=True)


def initials(name):
    words = [w for w in re.sub(r'\(.*?\)', '', name).replace('.', ' ').split()
             if w.lower() not in ('dr', 'chef', 'lt', 'gen', 'general', 'major', 'captain', 'colonel', 'retd', 'swami', 'sri', 'bk')]
    return (words[0][0] + (words[-1][0] if len(words) > 1 else '')).upper() if words else '?'


def first_sentence(text, limit=155):
    s = text.split('. ')[0].rstrip('.') + '.'
    return s if len(s) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'


def crumbs(*items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + '/' + u}
                                for i, (n, u) in enumerate(items)]}


def relink(markup, prefix):
    if not prefix:
        return markup
    return re.sub(r'(href|src)="(?!https?:|#|mailto:|tel:|/)([^"]+)"', lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"', markup)


def header(active):
    on = ' class="active" aria-current="page"'
    links = '\n'.join(f'      <li><a href="{h}"{on if h == active else ""}>{t}</a></li>' for h, t in NAV)
    return f"""<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
  <nav aria-label="Main">
    <a class="nav-logo" href="index.html" aria-label="TalentVerse Global home"><img src="Images/logo.webp" alt="TalentVerse Global" class="site-logo" width="928" height="501" /></a>
    <ul class="nav-links" id="nav-links">
{links}
      <li class="menu-cta"><a href="contact.html">Book a speaker →</a></li>
    </ul>
    <div class="nav-right">
      <a class="btn btn-book nav-cta" href="contact.html">Book a speaker</a>
      <button class="menu-toggle" type="button" aria-label="Open menu" aria-controls="nav-links" aria-expanded="false"><span></span></button>
    </div>
  </nav>
  </header>
"""


def footer(forms):
    topic_links = '\n'.join(f'          <li><a href="topics/{c}.html">{esc(n)}</a></li>' for c, n in list(CATS.items())[:6])
    scripts = ('  <script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js" defer></script>\n' if forms else '')
    scripts += '  <script src="js/main.js" defer></script>\n'
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <a href="index.html" aria-label="TalentVerse Global home"><img src="Images/logo.webp" alt="TalentVerse Global" class="site-logo" width="928" height="501" loading="lazy" /></a>
          <p>We book speakers for your event — keynotes, conferences, offsites and celebrations.</p>
        </div>
        <div>
          <h3>Find speakers</h3>
          <ul>
{topic_links}
          <li><a href="topics.html">All topics →</a></li>
          </ul>
        </div>
        <div>
          <h3>Company</h3>
          <ul>
            <li><a href="how-it-works.html">How it works</a></li>
            <li><a href="join.html">Join our roster</a></li>
            <li><a href="privacy.html">Privacy policy</a></li>
          </ul>
        </div>
        <div>
          <h3>Talk to us</h3>
          <ul>
            <li><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></li>
            <li><a href="{WHATSAPP}" rel="noopener">WhatsApp us</a></li>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          </ul>
        </div>
      </div>
      <p class="copyright">© 2026 TalentVerse Global. All rights reserved.</p>
    </div>
  </footer>

  <div class="action-bar" aria-label="Quick contact">
    <a class="ab-call" href="tel:{PHONE}">Call</a>
    <a class="ab-wa" href="{WHATSAPP}" rel="noopener">WhatsApp</a>
    <a class="ab-book" href="contact.html">Enquire</a>
  </div>

{scripts}</body>
</html>
"""


def page(path, title, desc, body, ld=(), og_image='Images/og-image.jpg', active=None, forms=False, index=True):
    prefix = '../' * path.count('/')
    url = SITE + '/' + ('' if path == 'index.html' else path)
    ld_html = '\n'.join('  <script type="application/ld+json">\n%s\n  </script>' % json.dumps(x, ensure_ascii=False, indent=2) for x in (ORG,) + tuple(ld))
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="{'index, follow' if index else 'noindex, follow'}" />
  <meta name="theme-color" content="#7C18D9" />
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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Nunito:wght@800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/styles.css" />
{ld_html}
</head>
{header(active)}  <main id="main">
{body}
  </main>

{footer(forms)}"""
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(relink(out, prefix))


# ── components ──
def photo(s, cls, lazy=True):
    if s['photo']:
        load = ' loading="lazy"' if lazy else ' fetchpriority="high"'
        return f'<img class="{cls}" src="{s["photo"]}" alt="{esc(s["name"])}"{load} />'
    return f'<div class="{cls} initials" aria-hidden="true">{esc(initials(s["name"]))}</div>'


def card(s):
    return f"""        <a class="roster-card" href="speakers/{s['slug']}.html" data-topic="{s['category']}">
          <div class="roster-photo">{photo(s, 'roster-img')}</div>
          <div class="roster-body">
            <span class="roster-topic">{esc(CATS[s['category']])}</span>
            <h3 class="roster-name">{esc(s['name'])}</h3>
            <p class="roster-title">{esc(s['title'])}</p>
          </div>
        </a>"""


def grid(speakers, grid_id=None):
    gid = f' id="{grid_id}"' if grid_id else ''
    return f'      <div class="roster-grid"{gid}>\n' + '\n'.join(card(s) for s in speakers) + '\n      </div>'


def topic_options():
    return '\n'.join(f'              <option>{esc(n)}</option>' for n in CATS.values()) + '\n              <option>Not sure yet</option>'


HONEYPOT = '<div class="hp-field" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off" /></label></div>'
FORM_ERROR = f'<div class="form-error" role="alert">Sorry, that didn’t send. Please try again, or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</div>'


def field(fid, label, name, kind='text', required=True, placeholder='', autocomplete=''):
    req = ' required' if required else ''
    opt = '' if required else ' <span class="opt">(optional)</span>'
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ''
    ph = f' placeholder="{esc(placeholder)}"' if placeholder else ''
    if kind == 'textarea':
        ctrl = f'<textarea id="{fid}" name="{name}"{ph}{req}></textarea>'
    else:
        ctrl = f'<input id="{fid}" type="{kind}" name="{name}"{ph}{ac}{req} />'
    return f'<div class="form-group"><label for="{fid}">{label}{opt}</label>{ctrl}</div>'


def name_fields(p):
    return f"""<div class="form-row">
            {field(p + '-first', 'First name', 'first_name', autocomplete='given-name')}
            {field(p + '-last', 'Last name', 'last_name', autocomplete='family-name')}
          </div>"""


def enquiry_form(form_id, heading, intro, short=False):
    p = form_id.split('-')[0]
    topic = f"""<div class="form-group"><label for="{p}-topic">Speaker category</label>
            <select id="{p}-topic" name="topic" required>
              <option value="">Choose a category</option>
{topic_options()}
            </select></div>"""
    if short:
        middle = f"""{topic}
          {field(p + '-speaker', 'Speaker you have in mind', 'speaker', required=False, placeholder='e.g. Anil Kumble')}
          {field(p + '-details', 'Tell us about your event', 'event_details', 'textarea', required=False, placeholder='Date, city, audience and what you want them to take away')}"""
    else:
        middle = f"""{field(p + '-org', 'Organisation', 'organisation', placeholder='Your company or event', autocomplete='organization')}
          <div class="form-row">
            {field(p + '-date', 'Event date', 'event_date', 'date')}
            {topic}
          </div>
          {field(p + '-speaker', 'Speaker you have in mind', 'speaker', required=False, placeholder='e.g. Anil Kumble — or leave blank for a shortlist')}
          <details class="more-details">
            <summary>Add more details (optional)</summary>
            <div class="form-row">
              <div class="form-group"><label for="{p}-audience">Audience size <span class="opt">(optional)</span></label>
                <select id="{p}-audience" name="audience_size">
                  <option value="">Choose a range</option>
                  <option>Under 100</option><option>100–500</option><option>500–1,000</option><option>1,000–5,000</option><option>5,000+</option>
                </select></div>
              {field(p + '-budget', 'Budget', 'budget', required=False, placeholder='e.g. ₹5–10 lakh')}
            </div>
            {field(p + '-details', 'Event details', 'event_details', 'textarea', required=False, placeholder='City, format, theme and what you want your audience to take away')}
          </details>"""
    return f"""<div class="form-card">
        <h2>{heading}</h2>
        <p>{intro}</p>
        <form id="{form_id}" data-enquiry>
          {name_fields(p)}
          <div class="form-row">
            {field(p + '-email', 'Email', 'email', 'email', placeholder='you@company.com', autocomplete='email')}
            {field(p + '-phone', 'Phone', 'contact_number', 'tel', placeholder='+91 98765 43210', autocomplete='tel')}
          </div>
          {middle}
          {HONEYPOT}
          <button class="btn btn-book btn-block" type="submit">Send enquiry →</button>
          {FORM_ERROR}
          <p class="form-note">We reply within one business day. We only use your details to respond to this enquiry — see our <a href="privacy.html">privacy policy</a>.</p>
        </form>
      </div>"""


def cta_band(title, text):
    return f"""    <section class="section">
      <div class="wrap">
        <div class="cta-band"><div class="cta-inner">
          <div><h2>{title}</h2><p>{text}</p></div>
          <div class="cta-actions">
            <a class="btn btn-book" href="contact.html">Get a free shortlist</a>
            <a class="btn btn-outline" href="{WHATSAPP}" rel="noopener">WhatsApp us</a>
          </div>
        </div></div>
      </div>
    </section>"""


STEPS = """      <div class="steps">
        <div class="step"><h3>Tell us about your event</h3><p>Share the date, audience and what you want people to take away — or the speaker you already have in mind.</p></div>
        <div class="step"><h3>Get a shortlist</h3><p>Within one business day we send speakers who fit your theme, audience and budget, with availability and fees.</p></div>
        <div class="step"><h3>We handle the rest</h3><p>Contracts, briefing, travel and on-the-day support — so your speaker arrives prepared and your event runs smoothly.</p></div>
      </div>"""

STATS = """      <div class="stats">
        <div class="stat"><div class="stat-num">600+</div><div class="stat-label">Speakers on our roster</div></div>
        <div class="stat"><div class="stat-num">94%</div><div class="stat-label">Client satisfaction</div></div>
        <div class="stat"><div class="stat-num">85%</div><div class="stat-label">Clients who book with us again</div></div>
      </div>"""


def topic_tiles():
    return '      <div class="topic-grid">\n' + '\n'.join(
        f'        <a class="topic-tile" href="topics/{c}.html"><strong>{esc(n)}</strong><span>{len(BY_CAT[c])} speakers →</span></a>'
        for c, n in CATS.items()) + '\n      </div>'


# ── HOME ──
PRIORITY = ' fetchpriority="high"'
hero_imgs = '\n'.join(f'            <img src="{BY_SLUG[s]["photo"]}" alt="{esc(BY_SLUG[s]["name"])}"{PRIORITY if i == 0 else ""} />' for i, s in enumerate(HERO_PHOTOS))
chips = '\n'.join(f'            <a class="chip" href="topics/{c}.html">{esc(CATS[c])}</a>' for c in ['business-leadership', 'sports', 'celebrities', 'comedians', 'government-policy'])
home = f"""    <section class="hero">
      <div class="wrap">
        <div>
          <span class="bubble">India’s speaker bureau</span>
          <h1>Book the right <span class="accent">speaker</span> for your event</h1>
          <p class="hero-sub">From cricket legends and CEOs to diplomats, comedians and chefs — tell us about your event and get a shortlist within one business day.</p>
          <form class="hero-search" action="speakers.html" role="search">
            <label class="visually-hidden" for="hero-q">Search speakers</label>
            <input id="hero-q" type="search" name="q" placeholder="Search a name or topic" />
            <button class="btn btn-primary" type="submit">Search</button>
          </form>
          <div class="hero-chips">
{chips}
          </div>
        </div>
        <div class="hero-art" aria-hidden="false">
          <div class="hero-card">
{hero_imgs}
          </div>
          <div class="hero-note">Free shortlist in 1 business day<span>No obligation — just tell us your brief.</span></div>
        </div>
      </div>
    </section>

    <section class="section" style="padding-top:0">
      <div class="wrap">
{STATS}
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head">
          <div><span class="bubble">Featured speakers</span><h2>Voices audiences remember</h2></div>
          <a class="btn btn-outline" href="speakers.html">See all speakers</a>
        </div>
{grid([BY_SLUG[s] for s in FEATURED])}
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <div><span class="bubble">Browse by topic</span><h2>Find speakers by topic</h2></div>
        </div>
{topic_tiles()}
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head">
          <div><span class="bubble">How it works</span><h2>From brief to standing ovation</h2></div>
        </div>
{STEPS}
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="cta-band"><div class="cta-inner">
          <div>
            <h2>Tell us about your event</h2>
            <p>Share a few details and we’ll come back within one business day with speakers who fit your audience, theme and budget.</p>
            <div class="btn-row" style="margin-top:1.5rem">
              <a class="btn btn-outline" href="tel:{PHONE}">Call {PHONE_DISPLAY}</a>
              <a class="btn btn-outline" href="{WHATSAPP}" rel="noopener">WhatsApp us</a>
            </div>
          </div>
          {enquiry_form('home-form', 'Quick enquiry', 'Takes under a minute.', short=True)}
        </div></div>
      </div>
    </section>"""
page('index.html', 'Book Keynote Speakers in India | TalentVerse Global Speaker Bureau',
     'Book keynote speakers, celebrities, sports legends, comedians and chefs for corporate events in India. Get a free shortlist from TalentVerse Global within one business day.',
     home, ld=[{"@context": "https://schema.org", "@type": "WebSite", "name": "TalentVerse Global", "url": SITE + "/",
                "potentialAction": {"@type": "SearchAction", "target": SITE + "/speakers.html?q={search_term_string}", "query-input": "required name=search_term_string"}}],
     forms=True)

# ── SPEAKERS DIRECTORY ──
filters = '\n'.join(
    ['        <button type="button" class="filter-btn active" aria-pressed="true" data-topic="all" onclick="filterSpeakers(this, \'all\')">All</button>'] +
    [f'        <button type="button" class="filter-btn" aria-pressed="false" data-topic="{c}" onclick="filterSpeakers(this, \'{c}\')">{esc(n)}</button>' for c, n in CATS.items()])
directory = f"""    <section class="page-header">
      <div class="wrap">
        <span class="bubble">600+ speakers</span>
        <h1>Find a speaker</h1>
        <p>Search by name or topic, or browse by category. Every speaker page has an enquiry button — we’ll confirm availability and fees.</p>
      </div>
    </section>

    <section class="section" style="padding-top:2rem">
      <div class="wrap">
        <div class="filters">
          <label class="search-box"><span class="visually-hidden">Search speakers</span><input type="search" id="speaker-search" placeholder="Search by name or topic…" autocomplete="off" /></label>
{filters}
        </div>
        <p class="roster-count" id="roster-count" aria-live="polite">{len(SPEAKERS)} speakers</p>
{grid(sorted(SPEAKERS, key=lambda x: x['photo'] is None), 'speakers-grid')}
        <p class="roster-empty" id="roster-empty" hidden>No speakers match that search. <a href="contact.html">Tell us what you need</a> and we’ll find the right person.</p>
      </div>
    </section>

{cta_band('Can’t find who you’re looking for?', 'Our roster is bigger than this page. Tell us your brief and we’ll suggest the right people.')}"""
page('speakers.html', 'Find a Speaker | 600+ Keynote Speakers in India | TalentVerse Global',
     'Search keynote speakers, celebrities, sports legends, comedians, authors and chefs to book for your event in India. Enquire for availability and fees.',
     directory, ld=[crumbs(('Home', ''), ('Speakers', 'speakers.html'))], active='speakers.html')

# ── TOPICS INDEX ──
topics_body = f"""    <section class="page-header">
      <div class="wrap">
        <span class="bubble">Topics</span>
        <h1>Speakers by topic</h1>
        <p>Pick a theme for your event and see who fits. Not sure? Send us your brief and we’ll recommend.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{topic_tiles()}
      </div>
    </section>
{cta_band('Need help choosing?', 'Tell us about your audience and goals — we’ll send a shortlist within one business day.')}"""
page('topics.html', 'Speakers by Topic | TalentVerse Global',
     'Browse speakers by topic: business and leadership, sports, celebrities, comedians, government and policy, health and wellbeing, chefs and more.',
     topics_body, ld=[crumbs(('Home', ''), ('Topics', 'topics.html'))], active='topics.html')

# ── TOPIC PAGES ──
for c, n in CATS.items():
    body = f"""    <section class="page-header">
      <div class="wrap">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="topics.html">Topics</a> / {esc(n)}</nav>
        <span class="bubble">{len(BY_CAT[c])} speakers</span>
        <h1>{esc(n)} speakers</h1>
        <p>{esc(TOPIC_INTROS[c])}</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{grid(BY_CAT[c])}
      </div>
    </section>
{cta_band('Need help choosing?', 'Tell us about your audience and goals — we’ll send a shortlist within one business day.')}"""
    page(f'topics/{c}.html', f'{n} Speakers to Book in India | TalentVerse Global',
         f'Book {n.lower()} speakers for corporate events, conferences and summits. {TOPIC_INTROS[c]}',
         body, ld=[crumbs(('Home', ''), ('Topics', 'topics.html'), (n, f'topics/{c}.html'))], active='topics.html')

# ── SPEAKER PROFILES ──
for s in SPEAKERS:
    cat = CATS[s['category']]
    q = s['name'].replace(' ', '%20')
    related = [r for r in BY_CAT[s['category']] if r['slug'] != s['slug']]
    related = sorted(related, key=lambda r: r['photo'] is None)[:4]
    body = f"""    <section class="section">
      <div class="wrap">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="speakers.html">Speakers</a> / <a href="topics/{s['category']}.html">{esc(cat)}</a> / {esc(s['name'])}</nav>
        <div class="profile">
          <div>{photo(s, 'profile-photo', lazy=False)}</div>
          <div>
            <span class="bubble">{esc(cat)}</span>
            <h1>{esc(s['name'])}</h1>
            <p class="profile-role">{esc(s['title'])}</p>
            <p class="profile-bio">{esc(s['bio'])}</p>
            <div class="btn-row">
              <a class="btn btn-book" href="contact.html?speaker={q}">Enquire about {esc(s['name'])}</a>
              <a class="btn btn-outline" href="{WHATSAPP}" rel="noopener">WhatsApp us</a>
            </div>
            <p class="reply-note">We’ll confirm availability and fees within one business day.</p>
          </div>
        </div>
      </div>
    </section>"""
    if related:
        body += f"""
    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head"><h2>Similar speakers</h2><a class="btn btn-outline" href="topics/{s['category']}.html">All {esc(cat)}</a></div>
{grid(related)}
      </div>
    </section>"""
    person = {"@type": "Person", "name": s['name'], "jobTitle": s['title'], "description": s['bio']}
    if s['photo']:
        person['image'] = SITE + '/' + s['photo']
    page(f"speakers/{s['slug']}.html", f"Book {s['name']} as a Speaker | TalentVerse Global",
         f"Book {s['name']} — {s['title']} — for your next event. {first_sentence(s['bio'], 100)}"[:300], body,
         ld=[crumbs(('Home', ''), ('Speakers', 'speakers.html'), (cat, f"topics/{s['category']}.html"), (s['name'], f"speakers/{s['slug']}.html")),
             {"@context": "https://schema.org", "@type": "ProfilePage", "url": f"{SITE}/speakers/{s['slug']}.html", "mainEntity": person}],
         og_image=s['photo'] or 'Images/og-image.jpg', active='speakers.html')

# ── HOW IT WORKS ──
hiw = f"""    <section class="page-header">
      <div class="wrap">
        <span class="bubble">How it works</span>
        <h1>We book speakers for your event</h1>
        <p>TalentVerse Global is a speaker bureau. We match organisations with the right voice — then manage every detail so the talk lands.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{STEPS}
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head"><div><span class="bubble">Who we work with</span><h2>For every kind of event</h2></div></div>
        <div class="topic-grid">
          <div class="topic-tile"><strong>Corporate events</strong><span>Leadership summits, sales kick-offs, offsites and annual days.</span></div>
          <div class="topic-tile"><strong>Agencies &amp; organisers</strong><span>Shortlists you can forward to clients, with fast answers on availability.</span></div>
          <div class="topic-tile"><strong>Universities &amp; associations</strong><span>Credible experts for convocations, conferences and lecture series.</span></div>
          <div class="topic-tile"><strong>Celebrations &amp; launches</strong><span>Comedians, celebrities and chefs who bring energy to the room.</span></div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
{STATS}
      </div>
    </section>
{cta_band('Ready to find your speaker?', 'Send your brief and get a free, no-obligation shortlist within one business day.')}"""
page('how-it-works.html', 'How It Works | Book a Speaker with TalentVerse Global',
     'How booking a speaker with TalentVerse Global works: share your brief, get a shortlist within one business day, and we handle contracts, briefing and travel.',
     hiw, ld=[crumbs(('Home', ''), ('How it works', 'how-it-works.html'))], active='how-it-works.html')

# ── CONTACT ──
contact = f"""    <section class="page-header">
      <div class="wrap">
        <span class="bubble">Book a speaker</span>
        <h1>Tell us about your event</h1>
        <p>We’ll reply within one business day with speakers who fit — including availability and fees.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap contact-grid">
        <div>
          <h2 style="font-size:1.5rem">Prefer to talk?</h2>
          <ul class="contact-list">
            <li><strong>Call</strong><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></li>
            <li><strong>WhatsApp</strong><a href="{WHATSAPP}" rel="noopener">Message us on WhatsApp</a></li>
            <li><strong>Email</strong><a href="mailto:{EMAIL}">{EMAIL}</a></li>
            <li><strong>Response time</strong>Within one business day</li>
          </ul>
          <p>Are you a speaker? <a href="join.html">Apply to join our roster</a>.</p>
        </div>
        {enquiry_form('contact-form', 'Booking enquiry', 'Only the essentials are required — add more detail if you have it.')}
      </div>
    </section>"""
page('contact.html', 'Book a Speaker – Enquiry | TalentVerse Global',
     f'Book a speaker for your event. Call or WhatsApp {PHONE_DISPLAY}, email {EMAIL}, or send an enquiry and get a shortlist within one business day.',
     contact, ld=[crumbs(('Home', ''), ('Contact', 'contact.html')),
                  {"@context": "https://schema.org", "@type": "ContactPage", "name": "Book a speaker", "url": SITE + "/contact.html"}],
     active='contact.html', forms=True)

# ── JOIN OUR ROSTER ──
join = f"""    <section class="page-header">
      <div class="wrap">
        <span class="bubble">For speakers</span>
        <h1>Join our roster</h1>
        <p>Speak on stages across India with event organisers who value great talks. Tell us about yourself and we’ll be in touch if there’s a fit.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap" style="max-width:820px">
        <div class="form-card">
          <h2>Speaker application</h2>
          <p>This form is for speakers. To book a speaker, use the <a href="contact.html">booking enquiry</a> instead.</p>
          <form id="join-form" data-enquiry>
            {name_fields('join')}
            <div class="form-row">
              {field('join-email', 'Email', 'email', 'email', autocomplete='email')}
              {field('join-phone', 'Phone', 'contact_number', 'tel', autocomplete='tel')}
            </div>
            <input type="hidden" name="organisation" value="Speaker roster application" />
            <input type="hidden" name="topic" value="Join our roster" />
            {field('join-expertise', 'What do you speak about?', 'expertise', placeholder='e.g. leadership, resilience, cricket')}
            {field('join-link', 'Website, LinkedIn or showreel', 'profile_link', 'url', required=False, placeholder='https://')}
            {field('join-details', 'A short bio', 'event_details', 'textarea', placeholder='Who you are and the talks you give')}
            {HONEYPOT}
            <button class="btn btn-primary btn-block" type="submit">Send application →</button>
            {FORM_ERROR}
          </form>
        </div>
      </div>
    </section>"""
page('join.html', 'Join Our Speaker Roster | TalentVerse Global',
     'Are you a speaker? Apply to join the TalentVerse Global roster and speak at corporate events, conferences and summits across India.',
     join, ld=[crumbs(('Home', ''), ('Join our roster', 'join.html'))], forms=True)

# ── THANK YOU ──
thanks = f"""    <section class="section">
      <div class="wrap prose" style="text-align:center;margin:0 auto">
        <span class="bubble">Received</span>
        <h1>Thank you — we’ve got it</h1>
        <p style="font-size:1.15rem;margin:1rem 0 2rem">We’ll reply within one business day. If your event is urgent, call or WhatsApp us on <a href="tel:{PHONE}">{PHONE_DISPLAY}</a>.</p>
        <div class="btn-row" style="justify-content:center">
          <a class="btn btn-primary" href="speakers.html">Keep browsing speakers</a>
          <a class="btn btn-outline" href="{WHATSAPP}" rel="noopener">WhatsApp us</a>
        </div>
      </div>
    </section>"""
page('thank-you.html', 'Thank You | TalentVerse Global', 'Thanks for your enquiry — TalentVerse Global will reply within one business day.', thanks, index=False)

# ── PRIVACY ──
privacy = f"""    <section class="page-header">
      <div class="wrap"><h1>Privacy policy</h1><p>Last updated 1 October 2026</p></div>
    </section>
    <section class="section">
      <div class="wrap prose">
        <p>This policy explains what personal information TalentVerse Global (“we”) collects through this website, why, and what you can do about it.</p>
        <h2>What we collect</h2>
        <ul>
          <li>Details you type into our forms: name, email, phone number, organisation, event details and, for speaker applications, your bio and links.</li>
          <li>Basic usage data (pages visited, device and browser) if analytics is enabled on this site.</li>
        </ul>
        <h2>How we use it</h2>
        <ul>
          <li>To reply to your enquiry or application and arrange bookings you ask us to.</li>
          <li>To understand which pages are useful and improve the site.</li>
        </ul>
        <p>We don’t sell your information or use it for unrelated marketing.</p>
        <h2>Who processes it</h2>
        <p>Form submissions are delivered to our inbox by EmailJS. If analytics is enabled, Google Analytics processes usage data. When you book a speaker, we share the event details needed with that speaker and their team.</p>
        <h2>How long we keep it</h2>
        <p>We keep enquiry details for as long as needed to handle your request and any resulting booking, then delete them unless we’re required to keep records.</p>
        <h2>Your choices</h2>
        <p>You can ask us to see, correct or delete the information we hold about you by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </div>
    </section>"""
page('privacy.html', 'Privacy Policy | TalentVerse Global', 'How TalentVerse Global collects and uses personal information submitted through this website.', privacy)

# ── SITEMAP ──
static = [('', '1.0', 'weekly'), ('speakers.html', '0.9', 'weekly'), ('topics.html', '0.8', 'monthly'), ('contact.html', '0.8', 'yearly'),
          ('how-it-works.html', '0.6', 'yearly'), ('join.html', '0.4', 'yearly'), ('privacy.html', '0.2', 'yearly')]
urls = static + [(f'topics/{c}.html', '0.8', 'monthly') for c in CATS] + [(f"speakers/{s['slug']}.html", '0.7', 'monthly') for s in SPEAKERS]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += ''.join(f"  <url><loc>{SITE}/{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n" for u, p, c in urls)
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm + '</urlset>\n')

print(f'Built {len(static) + 1} site pages, {len(CATS)} topic pages, {len(SPEAKERS)} speaker profiles; sitemap has {len(urls)} URLs')
