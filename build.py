#!/usr/bin/env python3
"""Builds the static site.

Each file in src/pages/ is the body of one page. Its first line is an HTML comment
holding JSON metadata, e.g.
  <!--meta {"path": "/appraisals/divorce/", "title": "...", "description": "..."} -->
This script wraps every page in the shared header, footer and SEO tags, writes it to
public/<path>/index.html, and regenerates public/sitemap.xml.

Run:  python3 build.py
"""
import json, re, html, datetime
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "pages"
OUT = ROOT / "public"
SITE = "https://agappraisalgroupllc.com"
PHONE = "(407) 588-7197"
PHONE_E164 = "+14075887197"
EMAIL = "algiammattei@gmail.com"
# Web3Forms access key (from web3forms.com, registered to the email above). Public by design.
WEB3FORMS_KEY = "a9d595ff-6a37-442a-b9fc-3441024caaa1"
PARTIALS = ROOT / "src" / "partials"

BUSINESS = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": SITE + "/#business",
    "name": "A.G. Appraisal Group, LLC",
    "description": "Residential real estate appraisals in Central Florida by Albert Giammattei III, "
                   "State Certified Residential Appraiser, Cert Res RD6369.",
    "url": SITE + "/",
    "telephone": PHONE_E164,
    "email": EMAIL,
    "image": SITE + "/assets/social/share.jpg",
    "address": {"@type": "PostalAddress", "addressLocality": "Oviedo",
                "addressRegion": "FL", "addressCountry": "US"},
    "areaServed": [
        {"@type": "AdministrativeArea", "name": "Seminole County, Florida"},
        {"@type": "AdministrativeArea", "name": "Orange County, Florida"},
        {"@type": "AdministrativeArea", "name": "Volusia County, Florida"},
        {"@type": "AdministrativeArea", "name": "Osceola County, Florida"},
        {"@type": "AdministrativeArea", "name": "Lake County, Florida"},
        {"@type": "AdministrativeArea", "name": "Brevard County, Florida"},
    ],
    "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "09:00", "closes": "17:00"}],
    "founder": {
        "@type": "Person",
        "@id": SITE + "/#al",
        "name": "Albert Giammattei III",
        "jobTitle": "State Certified Residential Appraiser",
        "alumniOf": "University of Central Florida",
        "hasCredential": {
            "@type": "EducationalOccupationalCredential",
            "name": "Florida State Certified Residential Appraiser, Cert Res RD6369",
            "credentialCategory": "license"},
    },
    "knowsAbout": ["Residential appraisal", "Date of death appraisal", "Divorce appraisal",
                   "Property tax appeal", "PMI removal", "Retrospective appraisal"],
}

NAV = [
    ("/#services", "Services"),
    ("/#area", "Where I work"),
    ("/#about", "About Al"),
    ("/#news", "News"),
    ("/#faq", "Questions"),
]

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Albert Giammattei III">
<meta name="geo.region" content="US-FL">
<meta name="geo.placename" content="Oviedo, Florida">
<meta property="og:type" content="website">
<meta property="og:site_name" content="A.G. Appraisal Group, LLC">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/assets/social/share.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400..500&family=Public+Sans:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">
{jsonld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/"><strong>A.G. Appraisal Group</strong><span>Oviedo, Florida</span></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <div class="header-cta">
      <a class="header-phone" href="tel:{phone_e164}">{phone}</a>
      <a class="btn btn-primary" href="/#order">Order an appraisal</a>
      <details class="menu"><summary>Menu</summary><nav aria-label="Mobile">{nav}<a href="tel:{phone_e164}">Call {phone}</a></nav></details>
    </div>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <h4>A.G. Appraisal Group, LLC</h4>
        <p>Residential real estate appraisals across Central Florida. Based in Oviedo, serving Seminole and Orange counties, plus parts of Volusia, Osceola, Lake and Brevard.</p>
        <p><strong>Albert Giammattei III</strong><br>State Certified Residential Appraiser<br>Cert Res RD6369 · FHA approved</p>
        <p><a href="tel:{phone_e164}">{phone}</a><br><a href="mailto:{email}">{email}</a></p>
      </div>
      <div>
        <h4>Appraisals for</h4>
        <ul>
          <li><a href="/appraisals/estate-probate/">Estate and probate</a></li>
          <li><a href="/appraisals/divorce/">Divorce</a></li>
          <li><a href="/appraisals/property-tax-appeal/">Property tax appeal</a></li>
          <li><a href="/appraisals/pmi-removal/">PMI removal</a></li>
          <li><a href="/#services">All services</a></li>
        </ul>
      </div>
      <div>
        <h4>Where I work</h4>
        <ul>
          <li><a href="/areas/oviedo/">Oviedo</a></li>
          <li><a href="/areas/orlando/">Orlando and Orange County</a></li>
          <li>Seminole County</li>
          <li>Volusia, Osceola, Lake and Brevard, in part</li>
        </ul>
      </div>
      <div>
        <h4>Hours</h4>
        <p>Mon to Fri, 9:00 to 5:00<br>Weekends by appointment</p>
        <p>Real estate brokerage services through <a href="https://www.metropolisrealestatesolutions.com/">Metropolis Real Estate Solutions, LLC</a></p>
      </div>
    </div>
    <p class="legal">Albert Giammattei III is a Florida State Certified Residential Appraiser, Cert Res RD6369, FHA approved, licensed and insured with errors and omissions coverage. Real estate brokerage services are offered through Metropolis Real Estate Solutions, LLC. Commissions are negotiated with each client and no rate is quoted here. An appraisal is an opinion of value for a stated use as of a stated date and is not tax or legal advice.<br>© {year} A.G. Appraisal Group, LLC</p>
  </div>
</footer>
<script src="/js/site.js" defer></script>
</body>
</html>
"""


def jsonld(blocks):
    return "\n".join(
        '<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + "</script>"
        for b in blocks)


def breadcrumbs(crumbs, url):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    for i, (name, path) in enumerate(crumbs, start=2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": SITE + path})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def faq_schema(body):
    """Builds FAQPage data from <details class="qa"><summary>Q</summary><p>A</p>... blocks."""
    qas = re.findall(r'<details class="qa">\s*<summary>(.*?)</summary>(.*?)</details>', body, re.S)
    if not qas:
        return None
    strip = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q),
         "acceptedAnswer": {"@type": "Answer", "text": " ".join(strip(a).split())}} for q, a in qas]}


def build():
    nav = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV)
    pages = []
    for f in sorted(SRC.glob("*.html")):
        text = f.read_text()
        m = re.match(r"<!--meta\s+(\{.*?\})\s*-->\s*", text, re.S)
        meta = json.loads(m.group(1))
        body = text[m.end():]
        body = re.sub(r"<!--#include (\w+) -->", lambda mm: (PARTIALS / (mm.group(1) + ".html")).read_text(), body)
        body = body.replace("{{WEB3FORMS_KEY}}", WEB3FORMS_KEY)
        path = meta["path"]
        url = SITE + path
        blocks = [BUSINESS]
        if meta.get("crumbs"):
            blocks.append(breadcrumbs(meta["crumbs"], url))
        if meta.get("service"):
            s = meta["service"]
            blocks.append({"@context": "https://schema.org", "@type": "Service",
                           "name": s["name"], "serviceType": s["name"], "description": meta["description"],
                           "url": url, "provider": {"@id": SITE + "/#business"},
                           "areaServed": s.get("area", "Central Florida")})
        fq = faq_schema(body)
        if fq:
            blocks.append(fq)
        head = HEAD.format(title=html.escape(meta["title"]), description=html.escape(meta["description"]),
                           url=url, site=SITE, jsonld=jsonld(blocks), nav=nav,
                           phone=PHONE, phone_e164=PHONE_E164)
        foot = FOOT.format(phone=PHONE, phone_e164=PHONE_E164, email=EMAIL,
                           year=datetime.date.today().year)
        dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        if path == "/404/":
            dest = OUT / "404.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(head + body + foot)
        if path != "/404/":
            pages.append((path, meta.get("priority", "0.7")))
        print("built", dest.relative_to(ROOT))

    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, pr in pages:
        sm.append(f"  <url><loc>{SITE}{path}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
    print("built public/sitemap.xml")


if __name__ == "__main__":
    build()
