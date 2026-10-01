# TalentVerse Global website

Static site — no build step. Upload the whole folder to any static host.

| Page | File |
| --- | --- |
| Home | `index.html` |
| Speakers | `speakers.html` |
| Speaker profile | `navtej-sarna.html` |
| About | `about.html` |
| Journal | `journal.html` |
| Contact / enquiry form | `contact.html` |

Shared styles live in `css/styles.css`, shared scripts (mobile menu, speaker filter, EmailJS forms) in `js/main.js`.

## SEO launch checklist

1. **Domain** — canonical URLs, social tags, `sitemap.xml` and `robots.txt` assume `https://talentverseglobal.com`. If the site lives elsewhere, search-and-replace that URL.
2. **Google Search Console** — verify the domain, then submit `https://talentverseglobal.com/sitemap.xml`.
3. **Google Analytics 4** — add the GA4 tag to every page's `<head>`. The forms already fire a `generate_lead` event on successful submission; mark it as a key event in GA4.
4. **Google Business Profile** — create one with the same name, phone (+91 98209 84063) and email as the site footer.
5. **EmailJS template** — forms send `first_name`, `last_name`, `email`, `contact_number`, `organisation`, `event_date`, `audience_size`, `topic`, `budget`, `event_details` and `page`. Make sure the template includes the ones you want in the email.

## Adding a speaker profile page

Copy `navtej-sarna.html`, change the title, description, canonical URL, JSON-LD, photo and text, link to it from `speakers.html`, and add it to `sitemap.xml`.
