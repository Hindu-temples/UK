# hindu-temples.uk — project handover

**Paste this whole file into a new chat to pick up exactly where we left off.**
Last updated: 3 September 2026.

---

## 1. What this is

A free directory and interactive map of **154 verified Hindu temples** across the UK.
Live at **https://hindu-temples.uk** via GitHub Pages (repo: `Hindu-temples/UK`).
Contact address used everywhere on the site: **hindu.temples.uk@gmail.com**

Built and run by one person — non-technical, works from a phone most of the time,
edits data in Excel, deploys by uploading files to GitHub. Domain is managed at IONOS.

Built because no map like it existed. Directories of other faiths' places of worship
are widely published; the UK's mandirs had nothing equivalent.

---

## 2. Current state (verified, not from memory)

| | |
|---|---|
| Temples | **154**, all 12 UK regions |
| With a website link | 119 |
| With a phone number | 138 |
| With verified opening hours | 13 |
| Traditions | General/Sanatan 87 · Saiva/Tamil 32 · BAPS 14 · Swaminarayan 12 · ISKCON 9 |
| HTML pages | 30 |
| Cambridge events loaded | 13, from 8 organisations |
| Posters / calendar files / images | 10 / 13 / 3 |

**⚠ The live site may be behind.** As of this writing the live site was still the
12 July build (153 temples, no websites, no Cambridge page) because the newer zips
had not been uploaded. Check `hindu-temples.uk` and compare the temple count in the
footer before assuming anything is live.

---

## 3. How it works — the whole architecture

**One command builds everything:**

```
python build.py
```

- Reads `temples.xlsx` → writes `temples.json` → generates every HTML page,
  the sitemap, robots.txt, favicon, og-image and apple-touch-icon.
- Needs `pip install openpyxl` (and `pillow` for the og-image).
- Workflow is: **edit `temples.xlsx` → run `python build.py` → upload everything to GitHub.**

**Key files**

| File | Role |
|---|---|
| `temples.xlsx` | **The master data. The only file the owner edits by hand.** 4 sheets: Temples, Guide, Festivals, Events |
| `build.py` | The entire site generator (~1600 lines) |
| `temples.json` | Generated map data — never edit by hand |
| `site.css` | One stylesheet for the whole site |
| `app.js` | The postcode finder / map application |
| `posters/` `events/` `img/` | **Three folders that must be uploaded too** — posters, .ics calendar files, page images |

**Excel sheets**
- **Temples** — 17 columns, dropdowns. Name, Area, Region, County, Lat, Lng, Address, Phone, Tradition, Notes, Featured, Status, Opening hours, Website, Facebook, Instagram, Last updated.
- **Festivals** — national festival dates. Blank Temple Name = UK-wide date.
- **Events** — local community events for the Cambridge page. Date, Time, Title, City, Venue, Address, Organiser, Link, Poster, Details, Free?
- **Guide** — instructions for the owner, kept up to date as features are added.

---

## 4. Pages built

**Core:** `index.html` (postcode finder + map + city grid + landmark temples + FAQ),
`directory.html` (all 154 by region, with website links and a name filter),
`temple-map.html` (all-UK dot map + region counts table), `about.html`, `404.html`.

**20 city pages:** london (38), leicester (14), coventry (8), birmingham (7),
manchester (7), wolverhampton (5), liverpool (4), watford (4), glasgow (4),
bolton (3), cardiff (3), leeds (2), luton (2), bedford (2), nottingham (2),
preston (2), bradford (1), derby (1), peterborough (1), slough (1).

**Content pages:**
- `visiting-a-hindu-temple.html` — first-time visitors and school RE trips. KS1–GCSE cards, SACRE named, risk assessment and safeguarding section, 9 etiquette cards, 8 questions to ask a temple, temple architecture table, FAQPage schema.
- `temple-traditions.html` — the five traditions explained, each linking to the map filtered to it.
- `hinduism-in-britain.html` — history. 13-point timeline 1929→2021, SVG population chart (30,000 in 1961 → 1,066,894 in 2021), census tables. Sources: ONS 2021, NRS 2022, NISRA.
- `cambridge.html` — the community events page (see §5).

**Nav:** Find a temple · Directory · Temple map · Visiting a temple · Hinduism in the UK · About

---

## 5. The Cambridge page — the most active part

**URL: `hindu-temples.uk/cambridge.html`**

Cambridge has no temple but a very active community. The page gathers festival events
from **8 organisations** in one place. The owner lives there and hand-shares it in a
500+ member community group.

Structure: short 3-sentence intro → plain button to `cambridgetemple.org` →
"Season ahead" festival strip → "Next up" ribbon → 3 month calendars →
13 event cards → festival dates → nearest temples → organisations box → cross-links.

**Each event card:** poster (tap to enlarge), date, relative badge (Today/Tomorrow/This Saturday),
time, cost or Free badge, venue, full address, details, organiser, and buttons —
**Directions** (Google Maps), **Add to calendar** (.ics), and **Register / book** *only where
a genuine booking link exists*. Every card ends: *"Full details and contact information are
on the poster — please reach out to the organisers."*

**Auto-expiry, two layers:** `build.py` drops past events at build time; a small script
removes them in the browser as dates pass, so the page self-cleans between rebuilds.
Same for festival dates and the festival strip.

**The 8 organisations:** Cambridge Hindu Association (chauk.org, charity 1077911),
Hindu Samaj Northstowe (hindusamajnorthstowe.org, charity 1213652), Cambourne Indian Club
(cambourneindianclub.com), ISKCON Cambridgeshire, Cambridge Hindu Forum,
Maharashtra Mandal Cambridgeshire (CIC 16632179), Cambourne Hindu Association /
Cambourne Vedic Heritage, CAM Community.

**Two events still missing venues** — 19 Sep Ganesh Chaturthi Maha Pooja (Cambridge Hindu
Forum), and the Grand Garba Nights 10 & 17 Oct (CAM Community). Both show
"venue to be confirmed" rather than a guess.

**It is built generically.** Adding another temple-less town (Warrington, Sunderland,
Lincoln, Blackburn, Wrexham) is one entry in the `COMMUNITY` list in `build.py`.

---

## 6. Standing rules — do not break these

1. **No mosque references anywhere.** Fully removed from code, content and comments. The old `map-comparison.html` is now a noindex redirect to `temple-map.html`.
2. **No distances shown.** Straight-line miles mislead. The map still draws lines to the 4 nearest temples and orders by proximity, but shows no figures. Cambridge copy says "at least an hour's drive each way."
3. **Never publish personal mobile numbers.** Posters carry volunteers' numbers; they stay in the poster image only, never as page text.
4. **Never publish bank details.** One poster carries an account number and sort code.
5. **No AI images of deities, symbols or Devanagari** — it garbles them. Architectural silhouettes without deities or lettering are fine (owner supplies these).
6. **Never publish unverified data.** Flag it or leave it out. The brand is "verified." Wrong opening hours send someone on an hour's drive to a closed mandir.
7. **Facts only from temple websites** — times, dates, addresses. Never copy their prose or photos.
8. **Text must be real HTML, not baked into images.** Text inside a poster or infographic is invisible to Google and screen readers. SEO is the owner's top priority.
9. **Only label a link "Register / book" if it genuinely is one.** An organisation's homepage is not a booking link.

---

## 7. Known gaps and pending actions

**Owner's to-do list:**
- [ ] **Upload the current build to GitHub** — including `posters/`, `events/` and `img/` folders. This is the blocker for everything.
- [ ] Verify at **Google Search Console** and **Bing Webmaster Tools**, submit `https://hindu-temples.uk/sitemap.xml`. Still outstanding; biggest single SEO action left.
- [ ] Send the Cambridge group message (final version in §9).
- [ ] Send own photos of **Balaji Tividale** and **Neasden** — for the history page, which currently has no images.
- [ ] Chase the two missing Cambridge venues.
- [ ] Turn on **GitHub two-factor authentication**.
- [ ] Consider moving hosting to **IONOS** (already paid for) so `temples.xlsx` and `build.py` are not public. Note: `temples.json` must stay public — the map fetches it — so the temple data is public either way. Deleting files from GitHub does not remove them from git history; only deleting the repo does.

**Data gaps:**
- 35 temples have no website; 141 have no verified opening hours.
- **No temple has published 2026 Diwali or Annakut dates** — checked, they haven't been announced. Do not invent them or copy them from SEO aggregator sites.
- Dussehra and Diwali currently show "none announced yet" on the Cambridge page.

**Ideas discussed but not built:**
- Google Sheet + Form feeding the Cambridge events, so the owner can update from a phone without a rebuild.
- Individual pages for the ~40 most significant temples (currently they are anchors on city pages).
- A services index (weddings, namkaran, priest booking) — needs data we don't have.
- An observation-led school worksheet — deliberately *not* a tick-box list, because a Tamil kovil and a BAPS mandir have different features.

---

## 8. Verified festival dates 2026

Ganesh Chaturthi **14 Sep** · Anant Chaturdashi/Visarjan **25 Sep** ·
Sharad Navratri **11–19 Oct** · Dussehra **20 Oct** · Karwa Chauth **29 Oct** ·
Dhanteras **6 Nov** · **Diwali 8 Nov** · Govardhan Puja/Annakut **9 Nov** ·
Kartik Purnima 24 Nov *(not independently verified)*

**Sources genuinely disagree** on Dussehra (19 or 20 Oct), Govardhan Puja (9 or 10 Nov)
and Naraka Chaturdashi (7 or 8 Nov). The site says so rather than picking — that honesty
is a feature, not a gap. UK temples also do not all observe on the same day.

---

## 9. The Cambridge group message (final, approved)

> Hi All, Happy Janmashtami in advance 🙏 A lot is happening this festive season.
>
> We don't have a temple in Cambridge, but look at how much our community is putting on. Posters and messages get lost, so it's all in one place now, and no one should miss attending these just because the information could not be easily found:
>
> https://hindu-temples.uk/cambridge
>
> *13 events • 8 organisations • posters, timings, venues, directions • add to your phone calendar*
>
> Ganesh Chaturthi, Navratri, Dussehra and Diwali still to come. Please share.
>
> For more details, or to get in touch, email hindu.temples.uk@gmail.com
>
> The closer we come together, the closer we get to our temple dream. 🙏

Send **after** the site is live, not before.

---

## 10. Working style that has suited the owner

- Build things rather than describe them; hand back a working zip.
- Flag what cannot be verified rather than filling the gap plausibly.
- Push back once, with reasons, then do what's asked — several of the owner's corrections have been better than the original proposal.
- Responses stay short; the owner is usually on a phone.
- When a file is retired, say explicitly which files to delete from GitHub — uploading never deletes.
