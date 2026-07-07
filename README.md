# hindu-temples.uk

Interactive finder for Hindu temples across the UK — search by postcode, browse by
region and tradition. 151 temples, each verified with a real street address.

## Files
- `index.html`, `styles.css`, `app.js` — the website
- `temples.json` — map data the site loads (**generated — don't edit by hand**)
- `temples.xlsx` — the master list you edit
- `build_from_excel.py` — rebuilds `temples.json` from the Excel
- `CNAME` — custom domain for GitHub Pages

## Publish it (GitHub Pages)
1. Put all these files in the repo root (this repo).
2. **Settings → Pages** → Source: *Deploy from a branch* → Branch `main`, folder `/ (root)` → Save.
3. Wait ~1 minute — the site is live.
4. Custom domain: the `CNAME` file sets `hindu-temples.uk`. In your IONOS DNS add:
   - four **A** records for the apex `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - one **CNAME** for `www` → `hindu-temples.github.io` (your `owner.github.io`)
   Then tick **Enforce HTTPS** on the Pages page.

Prefer hosting on IONOS directly? Upload `index.html`, `styles.css`, `app.js`, `temples.json`
to the web root. It must be served over http(s) — opening the file locally won't load the map.

## Updating the data
1. Edit `temples.xlsx` (the *Temples* sheet has dropdowns; a *Guide* tab explains each column).
   Add/remove rows, fill Opening hours / Website / social / Status.
2. Run once: `pip install openpyxl`  — then: `python build_from_excel.py temples.xlsx`
3. Commit the updated `temples.json`. The live site updates.

## Contact / report button
The **Report or add a temple** button already opens a pre-filled email to
`hindu.temples.uk@gmail.com` — no setup needed.

To switch to a Google Form (entries collect in a Sheet you own):
1. Go to forms.google.com signed in as hindu.temples.uk@gmail.com → new form.
2. Add fields: Temple name, Town/postcode, What's new or wrong, Opening hours,
   Website/social, Your email (optional).
3. **Send → link** icon → copy the URL.
4. In `app.js` line 1, replace the `mailto:...` string with that form URL. Commit.

## Search-optimised pages (SEO)
A single JavaScript map isn't indexable on its own, so the site also generates static pages Google can read:
- `directory.html` — full A–Z of every temple, by region
- one page per major UK Hindu city (e.g. `leicester.html`) — 20 cities
- `map-comparison.html` — dot map of all temples, in the style of the UK mosques map
- `sitemap.xml`, `robots.txt`

Regenerate them whenever the data changes:

    python build_pages.py

Full update flow: edit `temples.xlsx` → `python build_from_excel.py temples.xlsx` → `python build_pages.py` → commit everything.

### Get it indexed
1. Add the site to **Google Search Console** (search.google.com/search-console) and **Bing Webmaster Tools**.
2. Submit `https://hindu-temples.uk/sitemap.xml`.
3. Ask a few of the temples (you have their contacts) plus NCHT UK / Hindu Council UK to link to the site — inbound links are the biggest ranking factor.
