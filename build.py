#!/usr/bin/env python3
"""
Hindu Temples UK — site builder.

    python build.py

One command does everything:
  1. If temples.xlsx is present (and openpyxl installed), rebuilds temples.json from it.
  2. Generates every page: index, directory, 20 city pages, temple-map, about, 404.
  3. Generates sitemap.xml, robots.txt, site.webmanifest, favicon.svg,
     og-image.png and apple-touch-icon.png.

Edit temples.xlsx  ->  python build.py  ->  commit. That's the whole workflow.
"""
import json, html, math, os, sys, datetime

BASE   = "https://hindu-temples.uk"
EMAIL  = "hindu.temples.uk@gmail.com"
TODAY  = datetime.date.today().isoformat()
MAILTO = ("mailto:" + EMAIL +
  "?subject=Temple%20submission%20%E2%80%93%20hindu-temples.uk"
  "&amp;body=Temple%20name%3A%0AAddress%20%2F%20postcode%3A%0A"
  "What%27s%20new%2C%20closed%2C%20or%20wrong%3A%0AOpening%20hours%20(if%20known)%3A%0A"
  "Website%20%2F%20social%20links%3A%0A")

TRAD_LABEL = {"BAPS":"BAPS Swaminarayan","ISKCON":"ISKCON / Vaishnava","Saiva":"Saiva / Tamil",
              "Swaminarayan":"Swaminarayan (other)","General":"Sanatan / community"}
REGIONS = ["London","South East","South West","East of England","East Midlands","West Midlands",
           "Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"]

# name, slug, lat, lng, radius(mi), zoom, blurb
CITIES = [
 ("London","london",51.509,-0.126,15,10,"London is home to the largest Hindu population in the UK, with major mandirs across the capital from Neasden to Southall. The borough of Harrow has the highest proportion of Hindu residents of any local authority in England and Wales."),
 ("Leicester","leicester",52.6369,-1.1398,12,12,"Leicester has one of the most established Hindu communities in Britain, centred on the famous Golden Mile along Belgrave Road, and hosts one of the largest Diwali celebrations outside India."),
 ("Birmingham","birmingham",52.4862,-1.8904,12,11,"Birmingham and the wider West Midlands host a large, diverse Hindu community. Nearby Tividale is home to the Shri Venkateswara (Balaji) Temple, one of the largest Hindu temple complexes in Europe."),
 ("Coventry","coventry",52.4068,-1.5197,8,12,"Coventry has a long-established Hindu community, with a cluster of temples spanning the Sanatan, Swaminarayan, ISKCON and South Indian Saiva traditions."),
 ("Wolverhampton","wolverhampton",52.5870,-2.1288,8,12,"Wolverhampton and the Black Country are home to a settled Hindu community, with mandirs across Wolverhampton, Walsall and Bilston."),
 ("Manchester","manchester",53.4808,-2.2426,9,11,"Greater Manchester's Hindu community is served by long-standing mandirs across the city and surrounding towns, from Withington to Whalley Range."),
 ("Bolton","bolton",53.5769,-2.4282,7,12,"Bolton has a notable Gujarati Hindu community, with several Swaminarayan and Sanatan temples."),
 ("Preston","preston",53.7632,-2.7031,8,12,"Preston is home to the Gujarat Hindu Society, one of the largest Hindu temples in Lancashire."),
 ("Liverpool","liverpool",53.4084,-2.9916,10,11,"Liverpool and Merseyside are served by a mix of North Indian and South Indian Tamil Hindu temples."),
 ("Leeds","leeds",53.8008,-1.5491,9,12,"Leeds has a growing Hindu community, with a central mandir and a BAPS Swaminarayan temple in Burley."),
 ("Bradford","bradford",53.7960,-1.7594,7,12,"Bradford's Hindu community is served by the long-established Hindu Cultural Society."),
 ("Nottingham","nottingham",52.9548,-1.1581,8,12,"Nottingham's Hindu temple and community centre on Carlton Road serves the wider East Midlands city."),
 ("Derby","derby",52.9225,-1.4746,8,12,"Derby's main mandir, the Geeta Bhawan, has served the city's Hindu community for decades."),
 ("Luton","luton",51.8787,-0.4200,7,12,"Luton has a well-established Hindu community, with a large community temple and a BAPS Swaminarayan mandir."),
 ("Bedford","bedford",52.1360,-0.4667,7,12,"Bedford's Hindu community is served by a community temple and cultural trust."),
 ("Watford","watford",51.656,-0.396,8,12,"Watford and the surrounding Hertfordshire villages are home to Bhaktivedanta Manor, the ISKCON estate famously donated by George Harrison in 1973."),
 ("Peterborough","peterborough",52.5695,-0.2405,7,12,"Peterborough is served by the Bharat Hindu Samaj, long the city's main Hindu temple."),
 ("Cardiff","cardiff",51.4816,-3.1791,10,12,"Cardiff has the largest Hindu community in Wales, with a Swaminarayan temple and a Sanatan Dharma community centre."),
 ("Glasgow","glasgow",55.8642,-4.2518,10,11,"Glasgow is home to Scotland's largest Hindu community, with several mandirs including one of the country's oldest."),
 ("Slough","slough",51.509,-0.595,6,12,"Slough is home to one of the first purpose-built Hindu temples in Britain, serving a large community west of London."),
]

FEATURED = [
 ("BAPS Shri Swaminarayan Mandir","Neasden","london","Europe's first traditional stone mandir (1995), hand-carved in marble and limestone."),
 ("Shri Venkateswara (Balaji) Temple","Tividale","birmingham","One of the largest Hindu temple complexes in Europe, in the South Indian style."),
 ("Bhaktivedanta Manor","Aldenham","watford","The ISKCON (Hare Krishna) estate donated by George Harrison in 1973."),
 ("Bharat Hindu Samaj Mandir","Peterborough","peterborough","Long the main mandir serving Peterborough and the surrounding area."),
 ("Shree Sanatan Mandir","Leicester","leicester","A carved-limestone landmark serving Leicester's Golden Mile community."),
 ("Shree Ghanapathy Temple","Wimbledon","london","A leading South London Saiva temple, dedicated to Lord Ganesha."),
]

FAQS = [
 ("How many Hindu temples are there in the UK?",
  'This directory lists <b>__N__ verified Hindu temples and mandirs</b> across England, Scotland, Wales and Northern Ireland, each checked against a real street address. National bodies such as the National Council of Hindu Temples UK estimate several hundred places of Hindu worship in total once smaller community shrines and home gatherings are included.'),
 ("Which UK city has the most Hindu temples?",
  'London has by far the most, with <a href="london.html">__NLON__ temples listed</a> across the capital. <a href="leicester.html">Leicester</a> follows with __NLEI__, clustered around the Golden Mile on Belgrave Road \u2014 home to one of the largest Diwali celebrations outside India.'),
 ("What is the largest Hindu temple in the UK?",
  'The <b>BAPS Shri Swaminarayan Mandir in Neasden</b>, London \u2014 opened in 1995 \u2014 was Europe\u2019s first traditional stone mandir and remains the best known. The <b>Shri Venkateswara (Balaji) Temple</b> in Tividale, near Birmingham, is among the largest Hindu temple complexes in Europe.'),
 ("How do I find my nearest Hindu temple?",
  'Type your postcode into the search box at the top of this page. The map ranks every temple by distance, draws sightlines to the four nearest, and gives you one-tap directions, phone numbers and websites where available.'),
 ("Are temple opening times listed?",
  'Opening hours are shown where they have been verified, and more are added as temples confirm them. Times can change for festivals and private events, so it\u2019s always worth checking with the temple before travelling.'),
 ("A temple is missing or has closed \u2014 how do I report it?",
  'Email <a href="__MAILTO__">' + EMAIL + '</a> with the temple\u2019s name and address and what needs changing. Every submission is checked before the map is updated \u2014 see <a href="about.html">how this directory is maintained</a>.'),
]

# ---------------------------------------------------------------- data
def s(v): return "" if v is None else str(v).strip()

def load_from_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    ws = wb["Temples"] if "Temples" in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = [s(h) for h in rows[0]]
    def col(name):
        return header.index(name) if name in header else None
    idx = {k: col(k) for k in ["Temple Name","Area","Region","County","Latitude","Longitude",
           "Address","Phone","Tradition","Notes","Featured","Status","Opening hours",
           "Website","Facebook","Instagram","Last updated"]}
    for req in ("Temple Name","Latitude","Longitude"):
        if idx[req] is None: sys.exit("ERROR: column '%s' missing from %s" % (req, path))
    def get(row, k):
        i = idx[k]; return row[i] if i is not None and i < len(row) else None
    labels = {v.lower(): k for k, v in TRAD_LABEL.items()}
    out, skipped = [], []
    for n, row in enumerate(rows[1:], start=2):
        name = s(get(row, "Temple Name"))
        if not name: continue
        try:
            lat = round(float(get(row, "Latitude")), 4); lng = round(float(get(row, "Longitude")), 4)
        except (TypeError, ValueError):
            skipped.append((n, name)); continue
        traw = s(get(row, "Tradition"))
        trad = traw if traw in TRAD_LABEL else labels.get(traw.lower(), "General")
        rec = {"name": name, "area": s(get(row, "Area")), "region": s(get(row, "Region")),
               "county": s(get(row, "County")), "lat": lat, "lng": lng,
               "addr": s(get(row, "Address")), "phone": s(get(row, "Phone")),
               "trad": trad, "note": s(get(row, "Notes")),
               "hl": s(get(row, "Featured")).lower() in ("yes","y","true","1")}
        for xk, jk in (("Status","status"),("Opening hours","hours"),("Website","url"),
                       ("Facebook","fb"),("Instagram","ig"),("Last updated","updated")):
            v = s(get(row, xk))
            if v and not (jk == "status" and v.lower() == "open"): rec[jk] = v
        out.append(rec)
    if skipped:
        print("Skipped %d row(s) with no coordinates:" % len(skipped))
        for n, nm in skipped: print("  row %d: %s" % (n, nm))
    return out

def load_data():
    if os.path.exists("temples.xlsx"):
        try:
            data = load_from_xlsx("temples.xlsx")
            json.dump(data, open("temples.json","w",encoding="utf-8"),
                      ensure_ascii=False, separators=(",",":"))
            print("data: rebuilt temples.json from temples.xlsx (%d temples)" % len(data))
            return data
        except ImportError:
            print("data: openpyxl not installed - using existing temples.json")
    data = json.load(open("temples.json", encoding="utf-8"))
    print("data: loaded temples.json (%d temples)" % len(data))
    return data

T = load_data()
for i, t in enumerate(T): t["id"] = i

def miles(a,b,c,d):
    R=3958.8; r=math.pi/180
    x=math.sin((c-a)*r/2)**2+math.cos(a*r)*math.cos(c*r)*math.sin((d-b)*r/2)**2
    return R*2*math.asin(math.sqrt(x))

for t in T:
    if t["region"] == "London":
        t["_city"] = "london"; continue
    best, bd = None, 1e9
    for nm, slug, la, lo, rad, z, bl in CITIES:
        if slug == "london": continue
        d = miles(t["lat"], t["lng"], la, lo)
        if d <= rad and d < bd: bd, best = d, slug
    t["_city"] = best

BY_CITY = {c[1]: [] for c in CITIES}
for t in T:
    if t["_city"]: BY_CITY[t["_city"]].append(t)
for slug in BY_CITY:
    BY_CITY[slug].sort(key=lambda x: (0 if x.get("hl") else 1, x["name"]))

N = len(T)
N_LON = len(BY_CITY["london"]); N_LEI = len(BY_CITY["leicester"])
REGION_COUNT = {r: sum(1 for t in T if t["region"] == r) for r in REGIONS}

# ---------------------------------------------------------------- helpers
def e(x): return html.escape(str(x or ""), quote=True)
def sub(tpl, **kw):
    for k, v in kw.items(): tpl = tpl.replace("__%s__" % k, v)
    return tpl
def gdir(t): return "https://www.google.com/maps/dir/?api=1&amp;destination=%s,%s" % (t["lat"], t["lng"])
def ld(obj): return '<script type="application/ld+json">%s</script>' % json.dumps(
    obj, ensure_ascii=False, separators=(",", ":"))

FAVICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
 '<rect width="64" height="64" rx="14" fill="#BE3524"/>'
 '<path d="M32 8 L44 38 H20 Z" fill="#FBF3E4"/>'
 '<rect x="16" y="38" width="32" height="12" fill="#FBF3E4"/>'
 '<rect x="28" y="41" width="8" height="9" fill="#BE3524"/>'
 '<circle cx="32" cy="6.5" r="2.5" fill="#E8A13A"/></svg>')

BRAND_SVG = ('<svg viewBox="0 0 64 64" aria-hidden="true">'
 '<rect width="64" height="64" rx="14" fill="#BE3524"/>'
 '<path d="M32 8 L44 38 H20 Z" fill="#FBF3E4"/>'
 '<rect x="16" y="38" width="32" height="12" fill="#FBF3E4"/>'
 '<rect x="28" y="41" width="8" height="9" fill="#BE3524"/>'
 '<circle cx="32" cy="6.5" r="2.5" fill="#E8A13A"/></svg>')

HAS_OG = False  # set true if og-image.png generated

def head(title, desc, canon, active="", leaflet=False, noindex=False, extra=""):
    og = ('<meta property="og:image" content="%s/og-image.png"/>'
          '<meta name="twitter:card" content="summary_large_image"/>' % BASE) if HAS_OG else \
         '<meta name="twitter:card" content="summary"/>'
    return sub("""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>__TITLE__</title>
<meta name="description" content="__DESC__"/>
<link rel="canonical" href="__CANON__"/>__ROBOTS__
<meta name="theme-color" content="#FAF6EE"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="Hindu Temples UK"/>
<meta property="og:title" content="__TITLE__"/>
<meta property="og:description" content="__DESC__"/>
<meta property="og:url" content="__CANON__"/>
__OG__
<link rel="icon" type="image/svg+xml" href="favicon.svg"/>
<link rel="apple-touch-icon" href="apple-touch-icon.png"/>
<link rel="manifest" href="site.webmanifest"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
__TILES__<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
__LEAFLET__<link rel="stylesheet" href="site.css"/>
__EXTRA__
<!-- analytics: paste your snippet here -->
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
""", TITLE=e(title), DESC=e(desc), CANON=canon,
     ROBOTS='\n<meta name="robots" content="noindex,nofollow"/>' if noindex else "",
     OG=og,
     TILES='<link rel="preconnect" href="https://a.basemaps.cartocdn.com"/>\n' if leaflet else "",
     LEAFLET='<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>\n' if leaflet else "",
     EXTRA=extra)

def header_html(active=""):
    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ""
        return '<a href="%s"%s>%s</a>' % (href, cur, label)
    return ('<header class="site-header"><div class="bar">'
            '<a class="brand" href="index.html">%s<b>Hindu Temples UK</b></a>'
            '<nav class="site-nav" aria-label="Main">%s%s%s%s</nav>'
            '</div><div class="kalash"></div></header>\n<main id="main">' % (
        BRAND_SVG,
        a("index.html", "Find a temple", "home"),
        a("directory.html", "Directory", "directory"),
        a("temple-map.html", "Temple map", "map"),
        a("about.html", "About", "about")))

def footer_html():
    cities = " ".join('<a href="%s.html">%s</a> ·' % (c[1], e(c[0])) for c in CITIES).rstrip(" ·")
    return sub("""</main>
<footer class="site-footer">
  <div class="cols">
    <div class="f-brand">
      <b>Hindu Temples UK</b>
      <p>A free, community-maintained directory of Hindu temples and mandirs across the United Kingdom — every listing verified against a real street address.</p>
    </div>
    <div>
      <p class="f-h">Explore</p>
      <ul class="f-links">
        <li><a href="index.html">Find your nearest temple</a></li>
        <li><a href="directory.html">Full A–Z directory</a></li>
        <li><a href="temple-map.html">Map of every UK temple</a></li>
        <li><a href="about.html">About &amp; data sources</a></li>
        <li><a href="__MAILTO__">Report or add a temple</a></li>
      </ul>
    </div>
    <div>
      <p class="f-h">Temples by city</p>
      <p class="f-cities">__CITIES__</p>
    </div>
  </div>
  <div class="f-meta"><div class="in">
    <span>© __YEAR__ hindu-temples.uk · __N__ temples · Updated __TODAY__</span>
    <span><a href="__MAILTO__">__EMAIL__</a></span>
  </div></div>
</footer>
</body>
</html>""", MAILTO=MAILTO, CITIES=cities, YEAR=TODAY[:4], N=str(N), TODAY=TODAY, EMAIL=EMAIL)

def temple_article(t):
    loc = " · ".join(x for x in [t["area"], t["county"]] if x)
    closed = ' <span class="tag closed">Closed</span>' if str(t.get("status","")).lower()=="closed" else ""
    meta = ""
    if t.get("hours"): meta += '<p class="t-meta">Opening hours: %s</p>' % e(t["hours"])
    if t.get("note"):  meta += '<p class="t-meta">%s</p>' % e(t["note"])
    links = ['<a href="%s" target="_blank" rel="noopener">Directions →</a>' % gdir(t)]
    if t.get("url"):   links.append('<a href="%s" target="_blank" rel="noopener">Website</a>' % e(t["url"]))
    if t.get("phone"): links.append('<a href="tel:%s">%s</a>' % (e(t["phone"].replace(" ","")), e(t["phone"])))
    return ('<article class="temple" id="t-%d">'
            '<h3>%s%s</h3>'
            '<p class="t-sub"><span class="tag">%s</span> %s%s</p>'
            '<p class="t-addr">%s</p>%s'
            '<p class="t-links">%s</p></article>' % (
        t["id"], e(t["name"]), " ★" if t.get("hl") else "",
        e(TRAD_LABEL.get(t["trad"], t["trad"])), e(loc), closed, e(t["addr"]), meta, " ".join(links)))

def ld_place(t, compact=False):
    p = {"@type": "HinduTemple", "name": t["name"],
         "address": {"@type": "PostalAddress", "streetAddress": t["addr"],
                     "addressLocality": t["area"], "addressRegion": t["county"], "addressCountry": "GB"}}
    if not compact:
        p["geo"] = {"@type": "GeoCoordinates", "latitude": t["lat"], "longitude": t["lng"]}
        if t.get("phone"): p["telephone"] = t["phone"]
        if t.get("url"): p["url"] = t["url"]
    return p

def ld_itemlist(temples, name, compact=False):
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name,
            "numberOfItems": len(temples),
            "itemListElement": [{"@type": "ListItem", "position": i, "item": ld_place(t, compact)}
                                for i, t in enumerate(temples, 1)]}

def ld_breadcrumb(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i+1, "name": n, "item": BASE + "/" + u}
                                for i, (n, u) in enumerate(trail)]}

# ---------------------------------------------------------------- index
def build_index():
    faq_html, faq_ld = [], []
    for q, a in FAQS:
        a = sub(a, N=str(N), NLON=str(N_LON), NLEI=str(N_LEI), MAILTO=MAILTO)
        faq_html.append("<details><summary>%s</summary><p>%s</p></details>" % (e(q), a))
        import re as _re
        faq_ld.append({"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": _re.sub(r"<[^>]+>", "", a)}})

    city_cards = "".join(
        '<a class="city-card" href="%s.html"><b>%s</b><span>%d temple%s</span></a>' %
        (slug, e(nm), len(BY_CITY[slug]), "" if len(BY_CITY[slug]) == 1 else "s")
        for nm, slug, la, lo, rad, z, bl in CITIES if BY_CITY[slug])

    feats = []
    for name, area, cslug, why in FEATURED:
        t = next((x for x in T if x["name"] == name and x["area"] == area), None)
        if not t: continue
        feats.append('<div class="feat-card"><h3>%s</h3><p class="where">%s · %s</p><p>%s</p>'
                     '<a href="%s.html#t-%d">View in %s →</a></div>' %
                     (e(t["name"]), e(t["area"]), e(t["region"]), e(why),
                      cslug, t["id"], e(dict((c[1], c[0]) for c in CITIES)[cslug])))

    page = head(
        "UK Hindu Temples — Interactive Map & Directory of %d Mandirs" % N,
        "Find your nearest Hindu temple by postcode. An interactive map and complete directory of %d verified mandirs across England, Scotland, Wales and Northern Ireland — with addresses, traditions, opening hours and directions." % N,
        BASE + "/", active="home", leaflet=True,
        extra="\n".join([
            ld({"@context": "https://schema.org", "@type": "WebSite", "name": "Hindu Temples UK",
                "url": BASE + "/", "description": "Interactive map and directory of Hindu temples across the United Kingdom.",
                "potentialAction": {"@type": "SearchAction",
                    "target": {"@type": "EntryPoint", "urlTemplate": BASE + "/?postcode={postcode}"},
                    "query-input": "required name=postcode"}}),
            ld({"@context": "https://schema.org", "@type": "Organization", "name": "Hindu Temples UK",
                "url": BASE + "/", "logo": BASE + "/favicon.svg", "email": EMAIL}),
            ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_ld}),
        ]))
    page += header_html("home")
    page += sub("""
<section class="hero wrap">
  <p class="eyebrow">Sacred geography · United Kingdom</p>
  <h1>Find your nearest Hindu temple</h1>
  <p class="lede">From the hand-carved marble of Neasden to the Tamil kovils of Croydon and the ISKCON estate at Bhaktivedanta Manor — this directory maps <b>__N__ verified Hindu temples and mandirs</b> across England, Scotland, Wales and Northern Ireland. Search by postcode, or browse by region and tradition.</p>
  <ul class="hero-stats">
    <li><b>__N__</b>temples verified</li>
    <li><b>12</b>regions covered</li>
    <li><b>5</b>traditions mapped</li>
  </ul>
</section>

<section class="finder wrap" aria-label="Temple finder">
  <div class="search-card">
    <div class="search-row">
      <div class="field">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 21s-7-6.4-7-11a7 7 0 1114 0c0 4.6-7 11-7 11z" stroke="#BE3524" stroke-width="1.6"/><circle cx="12" cy="10" r="2.4" stroke="#BE3524" stroke-width="1.6"/></svg>
        <input id="pc" type="text" inputmode="text" autocomplete="postal-code" placeholder="Enter a postcode (e.g. LE1 6EJ)" aria-label="Postcode" spellcheck="false"/>
      </div>
      <button class="btn btn-primary" id="go">Find</button>
    </div>
    <div class="search-aux">
      <button class="btn btn-ghost btn-sm" id="geo">◎ Use my location</button>
      <button class="btn btn-ghost btn-sm" id="pin" aria-pressed="false">✛ Drop a pin</button>
    </div>
    <p class="hint" id="hint" role="status" aria-live="polite">Nearest temples are ranked by straight-line distance from your postcode.</p>
    <div class="filters">
      <div class="sel"><label for="fRegion">Region</label>
        <select id="fRegion"><option value="">All regions</option></select></div>
      <div class="sel"><label for="fCounty">County / borough</label>
        <select id="fCounty"><option value="">All counties</option></select></div>
      <div class="sel"><label for="fTrad">Tradition</label>
        <select id="fTrad"><option value="">All traditions</option></select></div>
      <div class="sel"><label for="fName">Search by name</label>
        <div class="field" style="min-height:42px"><input id="fName" type="search" placeholder="Temple name…" style="font-family:var(--font-body);font-size:15px;padding:9px 0"/></div></div>
    </div>
    <p class="report-line">Missing temple or wrong details? <a href="__MAILTO__">Report it →</a></p>
  </div>

  <div class="map-wrap">
    <div id="map" role="application" aria-label="Map of Hindu temples in the UK"></div>
    <p class="map-status" id="mapStatus">Loading __N__ temples…</p>
    <div class="legend collapsed" id="legend">
      <button class="legend-h" id="legendToggle" aria-expanded="false" aria-controls="legendRows">Key <span class="caret">▾</span></button>
      <div class="legend-body" id="legendRows"></div>
    </div>
  </div>

  <div class="results-block">
    <div class="results-head">
      <span class="count" id="count" role="status" aria-live="polite"></span>
      <button class="linklike" id="clear">Clear filters &amp; location</button>
    </div>
    <div class="results" id="results" aria-label="Temple results">
      <div class="card skel" aria-hidden="true"></div>
      <div class="card skel" aria-hidden="true"></div>
      <div class="card skel" aria-hidden="true"></div>
    </div>
  </div>
</section>

<section class="section wrap" id="cities">
  <div class="section-head">
    <h2>Browse temples by city</h2>
    <p class="section-sub">Every major Hindu community in Britain, from the capital to the Golden Mile — each city page lists its mandirs with addresses, traditions and directions.</p>
  </div>
  <div class="city-grid">__CITYCARDS__</div>
</section>

<section class="section wrap" id="featured">
  <div class="section-head">
    <h2>Landmark temples of the UK</h2>
    <p class="section-sub">Six places that anchor Hindu life in Britain.</p>
  </div>
  <div class="feat-grid">__FEATS__</div>
</section>

<section class="section wrap" id="faq">
  <div class="section-head">
    <h2>Common questions</h2>
  </div>
  <div class="faq">__FAQS__</div>
</section>
""", N=str(N), CITYCARDS=city_cards, FEATS="".join(feats), FAQS="".join(faq_html), MAILTO=MAILTO)
    page += footer_html()
    page += """
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>
<script src="app.js" defer></script>"""
    open("index.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- city pages
def build_city_pages():
    made = []
    for nm, slug, la, lo, rad, z, blurb in CITIES:
        temples = BY_CITY[slug]
        if not temples: continue
        n = len(temples)
        clat = sum(t["lat"] for t in temples) / n
        clng = sum(t["lng"] for t in temples) / n
        examples = ", ".join(t["name"] for t in temples[:3])
        title = "Hindu Temples in %s — %d Mandir%s Listed" % (nm, n, "" if n == 1 else "s")
        desc = ("Find Hindu temples and mandirs in %s: addresses, opening hours, traditions and directions for %d temple%s including %s." % (
            nm, n, "" if n == 1 else "s", examples))[:158]
        canon = "%s/%s.html" % (BASE, slug)
        body = sub("""
<div class="page wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="index.html">Home</a> › <a href="directory.html">Directory</a> › __NM__</nav>
  <h1>Hindu Temples in __NM__</h1>
  <div class="prose">
    <p class="lede">__BLURB__</p>
    <p><b>__CN__ temple__PL__</b> listed in and around __NM__. <a href="index.html?lat=__LAT__&amp;lng=__LNG__&amp;z=__Z__">Open __NM__ on the interactive map</a> to search by postcode and see them all at once.</p>
  </div>
  <div class="tlist">__TEMPLES__</div>
  <p class="backlink"><a href="directory.html">See every UK Hindu temple by region →</a></p>
</div>""", NM=e(nm), BLURB=e(blurb), CN=str(n), PL="" if n == 1 else "s",
           LAT="%.4f" % clat, LNG="%.4f" % clng, Z=str(z),
           TEMPLES="".join(temple_article(t) for t in temples))
        page = (head(title, desc, canon, leaflet=False,
                     extra="\n".join([ld(ld_itemlist(temples, "Hindu Temples in %s" % nm)),
                                      ld(ld_breadcrumb([("Home",""),("Directory","directory.html"),(nm, slug+".html")]))]))
                + header_html("") + body + footer_html())
        open("%s.html" % slug, "w", encoding="utf-8").write(page)
        made.append((nm, slug, n))
    return made

# ---------------------------------------------------------------- directory
def build_directory():
    jump = " ".join('<a href="#%s">%s</a>' % (r.lower().replace(" ", "-"), e(r))
                    for r in REGIONS if REGION_COUNT[r])
    secs = []
    for r in REGIONS:
        ts = sorted((t for t in T if t["region"] == r), key=lambda x: (x["county"], x["name"]))
        if not ts: continue
        rows = []
        for t in ts:
            loc = " · ".join(x for x in [t["area"], t["county"]] if x)
            if t.get("_city"):
                link, rel = "%s.html#t-%d" % (t["_city"], t["id"]), ""
            else:
                link, rel = gdir(t), ' target="_blank" rel="noopener"'
            closed = ' <span class="tag closed">Closed</span>' if str(t.get("status","")).lower()=="closed" else ""
            rows.append('<li><a href="%s"%s>%s</a> <span class="dloc">%s</span>%s</li>' %
                        (link, rel, e(t["name"]), e(loc), closed))
        secs.append('<section class="region-sec"><h2 id="%s">%s <span class="rn">%d temple%s</span></h2>'
                    '<ul class="dir">%s</ul></section>' %
                    (r.lower().replace(" ", "-"), e(r), len(ts), "" if len(ts)==1 else "s", "".join(rows)))
    body = sub("""
<div class="page wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="index.html">Home</a> › Directory</nav>
  <h1>UK Hindu Temple Directory</h1>
  <div class="prose">
    <p class="lede">Every Hindu temple and mandir in this directory — <b>__N__ in total</b> — listed by region with its town and county. Prefer a map? Use the <a href="index.html">postcode finder</a> or the <a href="temple-map.html">all-UK temple map</a>.</p>
  </div>
  <div class="dir-tools">
    <div class="field">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="#5F5344" stroke-width="1.6"/><path d="M20 20l-4-4" stroke="#5F5344" stroke-width="1.6"/></svg>
      <input id="dirFilter" type="search" placeholder="Filter by name or town…" aria-label="Filter temples"/>
    </div>
    <span class="count" id="dirCount"></span>
  </div>
  <p class="jumper">Jump to: __JUMP__</p>
  __SECS__
</div>
<script>
(function(){
  var input=document.getElementById('dirFilter'),items=[].slice.call(document.querySelectorAll('ul.dir li')),
      secs=[].slice.call(document.querySelectorAll('.region-sec')),count=document.getElementById('dirCount');
  function apply(){
    var q=input.value.trim().toLowerCase(),shown=0;
    items.forEach(function(li){var on=!q||li.textContent.toLowerCase().indexOf(q)>-1;li.style.display=on?'':'none';if(on)shown++;});
    secs.forEach(function(s){var any=[].slice.call(s.querySelectorAll('li')).some(function(li){return li.style.display!=='none';});s.style.display=any?'':'none';});
    count.textContent=q?shown+' of __N__ temples':'';
  }
  input.addEventListener('input',apply);
})();
</script>""", N=str(N), JUMP=jump, SECS="".join(secs))
    page = (head("UK Hindu Temple Directory — All %d Mandirs by Region" % N,
                 "The complete A–Z directory of %d Hindu temples and mandirs across the UK, organised by region and county, with links to full details, maps and directions." % N,
                 BASE + "/directory.html", active="directory",
                 extra="\n".join([ld(ld_itemlist(T, "UK Hindu Temple Directory", compact=True)),
                                  ld(ld_breadcrumb([("Home",""),("Directory","directory.html")]))]))
            + header_html("directory") + body + footer_html())
    open("directory.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- temple map
def build_temple_map():
    rows = "".join("<tr><td>%s</td><td>%d</td></tr>" % (e(r), REGION_COUNT[r])
                   for r in REGIONS if REGION_COUNT[r])
    trad_counts = {}
    for t in T: trad_counts[t["trad"]] = trad_counts.get(t["trad"], 0) + 1
    trad_line = ", ".join("%d %s" % (trad_counts[k], TRAD_LABEL[k].lower())
                          for k in ["General","Saiva","BAPS","Swaminarayan","ISKCON"] if trad_counts.get(k))
    pts = [{"lat": t["lat"], "lng": t["lng"], "n": t["name"], "a": t["area"], "h": bool(t.get("hl"))} for t in T]
    body = sub("""
<div class="page wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="index.html">Home</a> › Temple map</nav>
  <h1>Every Hindu temple in the UK, on one map</h1>
  <div class="prose">
    <p class="lede">All <b>__N__ Hindu temples and mandirs</b> in this directory, plotted across England, Scotland, Wales and Northern Ireland — from Aberdeen to Southampton, and from Belfast to Ipswich. Each dot is one temple; tap it for the name.</p>
  </div>
  <div class="bigmap-wrap"><div id="bigmap" role="application" aria-label="Map showing every Hindu temple in the UK"></div></div>
  <p class="map-cap">__N__ temples · one dot each · featured temples in vermilion · source: hindu-temples.uk</p>
  <div class="prose">
    <h2>Hindu temples by region</h2>
    <p>London and the Midlands hold the largest clusters, tracing where Britain's Hindu communities first settled — but every UK region now has at least one mandir. The directory spans __TRADS__.</p>
  </div>
  <table class="stats-table">
    <thead><tr><th scope="col">Region</th><th scope="col">Temples</th></tr></thead>
    <tbody>__ROWS__<tr><td><b>United Kingdom</b></td><td><b>__N__</b></td></tr></tbody>
  </table>
  <div class="prose">
    <p>Explore the same data with postcode search and filters on the <a href="index.html">interactive finder</a>, browse the <a href="directory.html">full A–Z directory</a>, or jump to a city such as <a href="london.html">London</a>, <a href="leicester.html">Leicester</a> or <a href="birmingham.html">Birmingham</a>.</p>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>
<script>
document.addEventListener('DOMContentLoaded',function(){
  var P=__PTS__;
  var m=L.map('bigmap',{scrollWheelZoom:false}).setView([54.5,-3.4],5);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
    {subdomains:'abcd',maxZoom:12,attribution:'&copy; OpenStreetMap &copy; CARTO'}).addTo(m);
  P.forEach(function(p){
    L.circleMarker([p.lat,p.lng],{radius:p.h?6:4,color:'#fff',weight:1,
      fillColor:p.h?'#BE3524':'#B8922F',fillOpacity:.88})
      .bindTooltip(p.n+(p.a?' — '+p.a:''),{direction:'top'}).addTo(m);
  });
});
</script>""", N=str(N), ROWS=rows, TRADS=e(trad_line),
           PTS=json.dumps(pts, ensure_ascii=False, separators=(",", ":")))
    page = (head("Map of Every Hindu Temple in the UK — %d Mandirs Plotted" % N,
                 "A single map of all %d Hindu temples and mandirs in the United Kingdom, with counts by region. See where Britain's Hindu communities worship, from London to Glasgow." % N,
                 BASE + "/temple-map.html", active="map", leaflet=True,
                 extra="\n".join([
                     ld({"@context": "https://schema.org", "@type": "Dataset",
                         "name": "Hindu temples of the United Kingdom",
                         "description": "Locations of %d verified Hindu temples and mandirs across the UK." % N,
                         "url": BASE + "/temple-map.html", "license": BASE + "/about.html",
                         "spatialCoverage": "United Kingdom", "creator": {"@type": "Organization", "name": "Hindu Temples UK"}}),
                     ld(ld_breadcrumb([("Home",""),("Temple map","temple-map.html")]))]))
            + header_html("map") + body + footer_html())
    open("temple-map.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- about
def build_about():
    body = sub("""
<div class="page wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="index.html">Home</a> › About</nav>
  <h1>About this directory</h1>
  <div class="prose">
    <p class="lede">hindu-temples.uk is a free, independent directory of Hindu temples and mandirs across the United Kingdom — built because nothing like it existed. Directories of other places of worship are widely published; the UK's __N__-plus mandirs deserved the same visibility.</p>

    <h2>How the data is compiled</h2>
    <p>The directory brings together the national temple bodies' published listings, community directories and multiple independent research passes, then verifies <b>every single temple</b> against live mapping data. Verification confirms three things: the temple exists at a real street address, its map pin sits on the actual building rather than a town centre, and it is genuinely a Hindu place of worship. Entries that fail any check are removed.</p>
    <p>Each listing records the temple's name, address, town, county, region, tradition (Sanatan/community, Saiva/Tamil, BAPS, other Swaminarayan, or ISKCON), and — where verified — phone number, opening hours and website. Currently: <b>__N__ temples</b> across all 12 UK regions, last updated <b>__TODAY__</b>.</p>

    <h2>What the directory is not</h2>
    <p>It is not exhaustive — smaller community shrines and home gatherings open, move and close all the time — and it is not affiliated with any temple, organisation or tradition. Distances on the finder are straight-line, for ranking; use each temple's Directions link for an actual route. Always confirm opening times with the temple before travelling, especially around festivals.</p>

    <h2 id="report">Report a temple, closure or correction</h2>
    <p>Spotted a missing mandir, a closure, wrong details, or have opening hours or a website to add? Email <a href="__MAILTO__">__EMAIL__</a> with the temple's name and address and what needs changing. Every submission is checked before the directory is updated.</p>

    <h2>Use of this data</h2>
    <p>The directory is free for personal and community use — linking to <a href="index.html">hindu-temples.uk</a> is appreciated. For bulk or commercial use, please get in touch first.</p>
  </div>
</div>""", N=str(N), TODAY=TODAY, MAILTO=MAILTO, EMAIL=EMAIL)
    page = (head("About Hindu Temples UK — Data, Sources & Contact",
                 "How hindu-temples.uk compiles and verifies the UK's most complete directory of Hindu temples — and how to report a missing temple, a closure or a correction.",
                 BASE + "/about.html", active="about",
                 extra="\n".join([
                     ld({"@context": "https://schema.org", "@type": "AboutPage",
                         "name": "About Hindu Temples UK", "url": BASE + "/about.html"}),
                     ld({"@context": "https://schema.org", "@type": "Organization",
                         "name": "Hindu Temples UK", "url": BASE + "/", "email": EMAIL,
                         "contactPoint": {"@type": "ContactPoint", "email": EMAIL, "contactType": "customer support"}}),
                     ld(ld_breadcrumb([("Home",""),("About","about.html")]))]))
            + header_html("about") + body + footer_html())
    open("about.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- 404 + legacy redirect
def build_404():
    body = """
<div class="page wrap">
  <h1>That page doesn't exist</h1>
  <div class="prose">
    <p class="lede">The address may have changed, or the link was mistyped. Everything on the site is one step away:</p>
    <p><a class="btn btn-primary" href="index.html" style="margin-right:10px">Find a temple</a>
       <a class="btn btn-ghost" href="directory.html">Browse the full directory</a></p>
  </div>
</div>"""
    page = (head("Page not found — Hindu Temples UK", "This page could not be found.",
                 BASE + "/404.html", noindex=True) + header_html("") + body + footer_html())
    open("404.html", "w", encoding="utf-8").write(page)

def build_legacy_redirect():
    # map-comparison.html was briefly live; forward it cleanly to temple-map.html
    open("map-comparison.html", "w", encoding="utf-8").write(
"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8"/>
<title>Moved — Map of Every Hindu Temple in the UK</title>
<meta name="robots" content="noindex"/>
<link rel="canonical" href="%s/temple-map.html"/>
<meta http-equiv="refresh" content="0; url=temple-map.html"/>
</head>
<body>
<p>This page has moved to <a href="temple-map.html">the UK Hindu temple map</a>.</p>
</body>
</html>""" % BASE)

# ---------------------------------------------------------------- assets
def build_assets(city_slugs):
    open("favicon.svg", "w", encoding="utf-8").write(FAVICON_SVG)
    json.dump({"name": "Hindu Temples UK", "short_name": "Temples UK",
               "start_url": "/", "display": "browser",
               "background_color": "#FAF6EE", "theme_color": "#BE3524",
               "icons": [{"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"}]},
              open("site.webmanifest", "w", encoding="utf-8"), indent=1)

    urls = ["", "directory.html", "temple-map.html", "about.html"] + ["%s.html" % s for s in city_slugs]
    pr = {"": "1.0", "directory.html": "0.9", "temple-map.html": "0.8", "about.html": "0.5"}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append("<url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" %
                  (BASE, u, TODAY, pr.get(u, "0.7")))
    sm.append("</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write("\n".join(sm))
    open("robots.txt", "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)

def build_images():
    """og-image.png (1200x630) + apple-touch-icon.png (180x180). Optional: skipped if PIL missing."""
    global HAS_OG
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("assets: PIL not installed - skipping og-image + apple-touch-icon"); return
    try:
        f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 78)
        f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        f_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24)
    except OSError:
        print("assets: fonts unavailable - skipping og-image"); return

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#FAF6EE")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill="#E8A13A")
    d.rectangle([0, 8, W, 14], fill="#BE3524")
    # temple mark
    mx, my = 92, 130
    d.rounded_rectangle([mx, my, mx + 150, my + 150], 30, fill="#BE3524")
    d.polygon([(mx + 75, my + 18), (mx + 118, my + 92), (mx + 32, my + 92)], fill="#FBF3E4")
    d.rectangle([mx + 28, my + 92, mx + 122, my + 122], fill="#FBF3E4")
    d.rectangle([mx + 64, my + 99, mx + 86, my + 122], fill="#BE3524")
    d.text((92, 330), "Hindu Temples UK", font=f_big, fill="#231B14")
    d.text((94, 432), "Find your nearest mandir — %d temples mapped" % N, font=f_sub, fill="#5F5344")
    d.text((94, 540), "hindu-temples.uk", font=f_tag, fill="#BE3524")
    img.save("og-image.png", optimize=True)

    icon = Image.new("RGB", (180, 180), "#BE3524")
    di = ImageDraw.Draw(icon)
    di.polygon([(90, 20), (128, 106), (52, 106)], fill="#FBF3E4")
    di.rectangle([44, 106, 136, 142], fill="#FBF3E4")
    di.rectangle([80, 114, 100, 142], fill="#BE3524")
    icon.save("apple-touch-icon.png", optimize=True)
    HAS_OG = True
    print("assets: og-image.png + apple-touch-icon.png generated")

# ---------------------------------------------------------------- run
def main():
    build_images()               # sets HAS_OG before pages reference it
    build_index()
    made = build_city_pages()
    build_directory()
    build_temple_map()
    build_about()
    build_404()
    build_legacy_redirect()
    build_assets([slug for _, slug, _ in made])
    print("pages: index + directory + temple-map + about + 404 + %d city pages" % len(made))
    for nm, slug, n in made: print("  %-14s %d" % (slug, n))
    print("done: %d temples, sitemap has %d URLs" % (N, 4 + len(made)))

if __name__ == "__main__":
    main()
