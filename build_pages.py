#!/usr/bin/env python3
"""
Generate SEO pages from temples.json:
  - one page per major UK Hindu city  (e.g. leicester.html)
  - directory.html   (full A-Z of every temple, grouped by region)
  - map-comparison.html  (mosque-style dot map of all temples)
  - sitemap.xml + robots.txt

Run after build_from_excel.py:
    python build_pages.py
"""
import json, html, math, datetime

BASE = "https://hindu-temples.uk"
TODAY = datetime.date.today().isoformat()
T = json.load(open("temples.json", encoding="utf-8"))
for i,t in enumerate(T): t["id"]=i

TRAD = {"BAPS":"BAPS Swaminarayan","ISKCON":"ISKCON / Vaishnava","Saiva":"Saiva / Tamil",
        "Swaminarayan":"Swaminarayan","General":"Sanatan / community"}
REGION_ORDER = ["London","South East","South West","East of England","East Midlands","West Midlands",
                "Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"]

# name, slug, lat, lng, radius(mi), blurb
CITIES = [
 ("London","london",51.509,-0.126,15,"London is home to the largest Hindu population in the UK, with major mandirs across boroughs from Neasden to Southall. The Borough of Harrow has the highest proportion of Hindu residents of any local authority in England and Wales."),
 ("Leicester","leicester",52.6369,-1.1398,12,"Leicester has one of the most established Hindu communities in Britain, centred on the famous \u2018Golden Mile\u2019 along Belgrave Road, and hosts one of the largest Diwali celebrations outside India."),
 ("Birmingham","birmingham",52.4862,-1.8904,12,"Birmingham and the wider West Midlands host a large, diverse Hindu community. Nearby Tividale is home to the Shri Venkateswara (Balaji) Temple, one of the largest Hindu temple complexes in Europe."),
 ("Coventry","coventry",52.4068,-1.5197,8,"Coventry has a long-established Hindu community, with a cluster of temples spanning the Sanatan, Swaminarayan, ISKCON and South Indian Saiva traditions."),
 ("Wolverhampton","wolverhampton",52.5870,-2.1288,8,"Wolverhampton and the Black Country are home to a settled Hindu community, with mandirs across Wolverhampton, Walsall and Bilston."),
 ("Manchester","manchester",53.4808,-2.2426,9,"Greater Manchester's Hindu community is served by long-standing mandirs across the city and surrounding towns, from Withington to Whalley Range."),
 ("Bolton","bolton",53.5769,-2.4282,7,"Bolton has a notable Gujarati Hindu community, with several Swaminarayan and Sanatan temples."),
 ("Preston","preston",53.7632,-2.7031,8,"Preston is home to the Gujarat Hindu Society, one of the largest Hindu temples in Lancashire."),
 ("Liverpool","liverpool",53.4084,-2.9916,10,"Liverpool and Merseyside are served by a mix of North Indian and South Indian (Tamil) Hindu temples."),
 ("Leeds","leeds",53.8008,-1.5491,9,"Leeds has a growing Hindu community, with a central mandir and a BAPS Swaminarayan temple in Burley."),
 ("Bradford","bradford",53.7960,-1.7594,7,"Bradford's Hindu community is served by the long-established Hindu Cultural Society."),
 ("Nottingham","nottingham",52.9548,-1.1581,8,"Nottingham's Hindu temple and community centre on Carlton Road serves the wider East Midlands city."),
 ("Derby","derby",52.9225,-1.4746,8,"Derby's main mandir, the Geeta Bhawan, has served the city's Hindu community for decades."),
 ("Luton","luton",51.8787,-0.4200,7,"Luton has a well-established Hindu community, with a large community temple and a BAPS Swaminarayan mandir."),
 ("Bedford","bedford",52.1360,-0.4667,7,"Bedford's Hindu community is served by a community temple and cultural trust."),
 ("Watford","watford",51.656,-0.396,8,"Watford and the surrounding Hertfordshire area are home to Bhaktivedanta Manor, the ISKCON (Hare Krishna) estate famously donated by George Harrison in 1973."),
 ("Peterborough","peterborough",52.5695,-0.2405,7,"Peterborough is served by the Bharat Hindu Samaj, long the city's main Hindu temple."),
 ("Cardiff","cardiff",51.4816,-3.1791,10,"Cardiff has the largest Hindu community in Wales, with a Swaminarayan temple and a Sanatan Dharma community centre."),
 ("Glasgow","glasgow",55.8642,-4.2518,10,"Glasgow is home to Scotland's largest Hindu community, with several mandirs including one of the country's oldest."),
 ("Slough","slough",51.509,-0.595,6,"Slough is home to one of the first purpose-built Hindu temples in Britain, serving a large community west of London."),
]

def miles(a,b,c,d):
    R=3958.8; r=math.pi/180
    x=math.sin((c-a)*r/2)**2+math.cos(a*r)*math.cos(c*r)*math.sin((d-b)*r/2)**2
    return R*2*math.asin(math.sqrt(x))

# assign each temple to nearest city within that city's radius
_slugs={c[1] for c in CITIES}
for t in T:
    if t["region"]=="London" and "london" in _slugs:
        t["_city"]="london"; continue
    best=None; bd=1e9
    for nm,slug,la,lo,rad,bl in CITIES:
        if slug=="london": continue
        d=miles(t["lat"],t["lng"],la,lo)
        if d<=rad and d<bd: bd=d; best=slug
    t["_city"]=best
city_of={c[1]:c for c in CITIES}
temples_by_city={c[1]:[] for c in CITIES}
for t in T:
    if t["_city"]: temples_by_city[t["_city"]].append(t)
for slug in temples_by_city:
    temples_by_city[slug].sort(key=lambda x:(0 if x.get("hl") else 1, x["name"]))

def e(s): return html.escape(str(s or ""), quote=True)
def gmap(t): return "https://www.google.com/maps/dir/?api=1&destination=%s,%s"%(t["lat"],t["lng"])

def nav(active=""):
    tops=["london","leicester","birmingham","coventry","manchester","leeds"]
    links=['<a href="index.html">Map</a>','<a href="directory.html">Full directory</a>',
           '<a href="map-comparison.html">Temples vs mosques</a>']
    return '<nav class="topnav"><a class="brand" href="index.html">Hindu Temples&nbsp;UK</a><span class="nl">%s</span></nav>'%(" ".join(links))

def footer():
    cl=" · ".join('<a href="%s.html">%s</a>'%(c[1],e(c[0])) for c in CITIES)
    return ('<footer class="foot"><p class="fh">Browse Hindu temples by city</p>'
            '<p class="fc">%s</p>'
            '<p class="fmeta"><a href="directory.html">Full A\u2013Z directory</a> · '
            '<a href="map-comparison.html">Compare with UK mosques map</a> · '
            '<a href="index.html">Interactive map</a></p>'
            '<p class="fsmall">hindu-temples.uk \u2014 a free, community directory of Hindu temples and mandirs across the United Kingdom. '
            'Last updated %s. Spotted something missing or wrong? Use the report link on the map.</p></footer>'%(cl,TODAY))

def temple_block(t):
    loc=" \u00b7 ".join(x for x in [t["area"],t["county"]] if x)
    rows=['<p class="t-addr">%s</p>'%e(t["addr"])]
    if t.get("hours"): rows.append('<p class="t-meta">Opening hours: %s</p>'%e(t["hours"]))
    links=['<a href="%s" rel="nofollow" target="_blank">Directions</a>'%gmap(t)]
    if t.get("url"): links.append('<a href="%s" target="_blank" rel="noopener">Website</a>'%e(t["url"]))
    if t.get("phone"): links.append('<a href="tel:%s">%s</a>'%(e(t["phone"].replace(" ","")),e(t["phone"])))
    trad=TRAD.get(t["trad"],t["trad"])
    star=' \u2605' if t.get("hl") else ''
    closed=' <span class="tag closed">Closed</span>' if str(t.get("status","")).lower()=="closed" else ''
    return ('<article class="temple" id="t-%d">'
            '<h3>%s%s</h3><p class="t-sub"><span class="tag">%s</span> %s%s</p>%s'
            '<p class="t-links">%s</p></article>'%(
        t["id"], e(t["name"]), star, e(trad), e(loc), closed,
        "".join(rows), " ".join(links)))

def jsonld_itemlist(temples, name):
    items=[]
    for i,t in enumerate(temples,1):
        place={"@type":"PlaceOfWorship","name":t["name"],
               "address":{"@type":"PostalAddress","streetAddress":t["addr"],
                          "addressLocality":t["area"],"addressRegion":t["county"],"addressCountry":"GB"},
               "geo":{"@type":"GeoCoordinates","latitude":t["lat"],"longitude":t["lng"]}}
        if t.get("phone"): place["telephone"]=t["phone"]
        if t.get("url"): place["url"]=t["url"]
        items.append({"@type":"ListItem","position":i,"item":place})
    return json.dumps({"@context":"https://schema.org","@type":"ItemList","name":name,
                       "numberOfItems":len(temples),"itemListElement":items},
                      ensure_ascii=False, separators=(",",":"))

def jsonld_breadcrumb(trail):
    items=[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+"/"+u} for i,(n,u) in enumerate(trail)]
    return json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items},
                      ensure_ascii=False, separators=(",",":"))

PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>__TITLE__</title>
<meta name="description" content="__DESC__"/>
<link rel="canonical" href="__CANON__"/>
<meta property="og:type" content="website"/><meta property="og:title" content="__TITLE__"/>
<meta property="og:description" content="__DESC__"/><meta property="og:url" content="__CANON__"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="pages.css"/>
__LD__</head><body>
__NAV__
<main class="wrap">
__BREADCRUMB__
__BODY__
</main>
__FOOTER__
</body></html>"""

def render(fn, title, desc, canon, body, ld_blocks, crumb_html=""):
    ld="".join('<script type="application/ld+json">%s</script>\n'%b for b in ld_blocks)
    out=(PAGE.replace("__TITLE__",e(title)).replace("__DESC__",e(desc)).replace("__CANON__",canon)
         .replace("__LD__",ld).replace("__NAV__",nav()).replace("__FOOTER__",footer())
         .replace("__BREADCRUMB__",crumb_html).replace("__BODY__",body))
    open(fn,"w",encoding="utf-8").write(out)

# ---------- city pages ----------
made=[]
for nm,slug,la,lo,rad,blurb in CITIES:
    temples=temples_by_city[slug]
    if not temples: continue
    n=len(temples)
    examples=", ".join(t["name"] for t in temples[:3])
    title="Hindu Temples in %s (%d Mandirs) | hindu-temples.uk"%(nm,n)
    desc=("Find Hindu temples and mandirs in %s. Addresses, opening hours, traditions and directions for %d temples including %s."%(nm,n,examples))[:300]
    canon="%s/%s.html"%(BASE,slug)
    crumb='<p class="crumb"><a href="index.html">Home</a> › <a href="directory.html">Directory</a> › %s</p>'%e(nm)
    body=('<h1>Hindu Temples in %s</h1>'
          '<p class="lede">%s</p>'
          '<p class="count">%d temple%s listed in and around %s. Tap <a href="index.html">the interactive map</a> to search by postcode and find your nearest.</p>'
          '<div class="tlist">%s</div>'
          '<p class="backlink"><a href="directory.html">See all UK Hindu temples by region \u2192</a></p>'%(
        e(nm), e(blurb), n, "" if n==1 else "s", e(nm),
        "".join(temple_block(t) for t in temples)))
    ld=[jsonld_itemlist(temples,"Hindu Temples in %s"%nm),
        jsonld_breadcrumb([("Home","index.html"),("Directory","directory.html"),(nm,slug+".html")])]
    render("%s.html"%slug, title, desc, canon, body, ld, crumb)
    made.append((nm,slug,n))

# ---------- directory (all temples by region) ----------
by_region={r:[] for r in REGION_ORDER}
for t in T: by_region.setdefault(t["region"],[]).append(t)
sec=[]
for r in REGION_ORDER:
    ts=sorted(by_region.get(r,[]), key=lambda x:(x["county"],x["name"]))
    if not ts: continue
    rows=[]
    for t in ts:
        loc=" \u00b7 ".join(x for x in [t["area"],t["county"]] if x)
        link='%s.html#t-%d'%(t["_city"],t["id"]) if t.get("_city") else gmap(t)
        rel=' rel="nofollow" target="_blank"' if not t.get("_city") else ''
        closed=' <span class="tag closed">Closed</span>' if str(t.get("status","")).lower()=="closed" else ''
        rows.append('<li><a href="%s"%s>%s</a> <span class="dloc">%s</span> <span class="tag sm">%s</span>%s</li>'%(
            link, rel, e(t["name"]), e(loc), e(TRAD.get(t["trad"],t["trad"])), closed))
    sec.append('<section class="region"><h2 id="%s">%s <span class="rn">(%d)</span></h2><ul class="dir">%s</ul></section>'%(
        e(r.lower().replace(" ","-")), e(r), len(ts), "".join(rows)))
dcity=" · ".join('<a href="%s.html">%s</a>'%(s,e(n)) for n,s,_ in made)
dbody=('<h1>UK Hindu Temple Directory</h1>'
       '<p class="lede">A complete, regularly updated list of Hindu temples and mandirs across the United Kingdom \u2014 %d in total, each with its address and tradition. Use <a href="index.html">the interactive map</a> to search by postcode.</p>'
       '<p class="citynav">Popular cities: %s</p>%s'%(len(T),dcity,"".join(sec)))
render("directory.html","UK Hindu Temple Directory \u2014 All Mandirs by Region | hindu-temples.uk",
       "Complete directory of %d Hindu temples and mandirs across the UK, listed by region with addresses, traditions and links. Search by postcode on the interactive map."%len(T),
       BASE+"/directory.html", dbody,
       [jsonld_itemlist(T,"UK Hindu Temple Directory"),
        jsonld_breadcrumb([("Home","index.html"),("Directory","directory.html")])],
       '<p class="crumb"><a href="index.html">Home</a> › Directory</p>')

# ---------- comparison dot map ----------
pts=[{"lat":t["lat"],"lng":t["lng"],"n":t["name"],"a":t["area"],"h":bool(t.get("hl"))} for t in T]
CMP = """<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Where are the UK's Hindu Temples? Map of __N__ Mandirs | hindu-temples.uk</title>
<meta name="description" content="A map of every Hindu temple and mandir in the United Kingdom \u2014 __N__ locations plotted, in the style of the well-known UK mosques map. Compare the distribution of Hindu temples across England, Scotland, Wales and Northern Ireland."/>
<link rel="canonical" href="__BASE__/map-comparison.html"/>
<meta property="og:title" content="Where are the UK's Hindu temples?"/>
<meta property="og:description" content="Every Hindu temple in the UK, mapped \u2014 __N__ locations."/>
<meta property="og:url" content="__BASE__/map-comparison.html"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="pages.css"/>
<style>
#cmap{height:72vh;min-height:460px;width:100%;background:#f2efe9;border:1px solid var(--line);border-radius:12px}
.cmap-cap{font-family:var(--mono);font-size:12px;color:var(--ink2);margin:8px 2px 0}
.leaflet-container{background:#f2efe9}
</style></head><body>
__NAV__
<main class="wrap">
<p class="crumb"><a href="index.html">Home</a> › Temples vs mosques</p>
<h1>Where are the UK's Hindu temples?</h1>
<p class="lede">Locations of Hindu temples and mandirs across the United Kingdom and Northern Ireland \u2014 <b>__N__</b> plotted below. This companion map mirrors the widely shared <em>UK mosques</em> map so the geographic spread of Hindu places of worship can be seen and compared at a glance.</p>
<div id="cmap"></div>
<p class="cmap-cap">__N__ Hindu temples mapped · Source: hindu-temples.uk · Each dot is one temple. Tap a dot for its name.</p>
<p class="count" style="margin-top:14px">Explore the same data with postcode search and filters on the <a href="index.html">interactive finder</a>, or browse the <a href="directory.html">full directory</a>.</p>
</main>
__FOOTER__
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const P=__PTS__;
const m=L.map('cmap',{scrollWheelZoom:false}).setView([54.5,-3.4],5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',{subdomains:'abcd',maxZoom:12,attribution:'&copy; OpenStreetMap &copy; CARTO'}).addTo(m);
P.forEach(p=>{L.circleMarker([p.lat,p.lng],{radius:p.h?6:4,color:'#fff',weight:1,fillColor:p.h?'#C2362B':'#2b6fd6',fillOpacity:.85})
  .bindTooltip(p.n+(p.a?' — '+p.a:''),{direction:'top'}).addTo(m);});
</script></body></html>"""
open("map-comparison.html","w",encoding="utf-8").write(
    CMP.replace("__N__",str(len(T))).replace("__BASE__",BASE)
       .replace("__NAV__",nav()).replace("__FOOTER__",footer())
       .replace("__PTS__",json.dumps(pts,ensure_ascii=False,separators=(",",":"))))

# ---------- sitemap + robots ----------
urls=["index.html","directory.html","map-comparison.html"]+["%s.html"%s for _,s,_ in made]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    pr="1.0" if u=="index.html" else ("0.8" if u in ("directory.html","map-comparison.html") else "0.7")
    sm.append("<url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"%(BASE,u,TODAY,pr))
sm.append("</urlset>")
open("sitemap.xml","w",encoding="utf-8").write("\n".join(sm))
open("robots.txt","w",encoding="utf-8").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n"%BASE)

print("city pages:", len(made))
for nm,slug,n in made: print("  %-14s %d"%(slug,n))
print("unassigned (directory-only):", sum(1 for t in T if not t["_city"]))
print("total pages:", len(urls))
