# hindu-temples.uk

A free directory and interactive map of Hindu temples across the United Kingdom.
Live at **https://hindu-temples.uk** (GitHub Pages).

## What's in this repo

| File | What it is |
|---|---|
| `temples.xlsx` | **The master data — the only file you edit.** Dropdowns + a Guide tab. |
| `build.py` | One-command builder: regenerates everything below from the Excel. |
| `temples.json` | Map data (generated — don't edit by hand) |
| `index.html` | Homepage: postcode finder + map + city links + FAQ (generated) |
| `directory.html`, `temple-map.html`, `about.html`, `404.html`, 20 city pages | Generated |
| `site.css`, `app.js` | Design system + finder application |
| `sitemap.xml`, `robots.txt`, `favicon.svg`, `og-image.png`, `site.webmanifest` | SEO assets (generated) |
| `CNAME` | Sets the custom domain for GitHub Pages |

## Updating the site

1. Edit `temples.xlsx` — add/remove rows, fill in Opening hours, Website, Status, etc.
2. Run (needs Python + `pip install openpyxl`):

       python build.py

3. Commit and push everything. The live site updates in ~1 minute.

`build.py` rebuilds `temples.json` *and* every page, so counts, city pages,
sitemap and structured data always stay in sync with the data.

## Deployment (already set up)

GitHub Pages → Settings → Pages → deploy from `main`, root folder.
Custom domain via `CNAME` file. In IONOS DNS: four A records for `@` →
`185.199.108.153 / 185.199.109.153 / 185.199.110.153 / 185.199.111.153`,
plus a CNAME for `www` → `hindu-temples.github.io`. Tick **Enforce HTTPS**.

Note: the map loads data over HTTP, so opening `index.html` from your desktop
shows an empty map — it works on any real host (or `python -m http.server` locally).

## Getting found (do once)

1. Verify the site at **Google Search Console** and **Bing Webmaster Tools**.
2. Submit `https://hindu-temples.uk/sitemap.xml` in both.
3. Ask temples you list — and bodies like NCHT UK / Hindu Council UK — to link
   to the site. Inbound links are the biggest ranking factor.

## Contact button

All "Report or add a temple" links open a pre-filled email to
`hindu.temples.uk@gmail.com` — no setup needed. To switch to a Google Form
later: create the form, copy its share link, replace the `MAILTO` value near
the top of `build.py` with that link, and run `python build.py` again.
