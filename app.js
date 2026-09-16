/* Hindu Temples UK — interactive finder
   Loads temples.json, renders the map + results, handles postcode search,
   filters, deep links (?postcode= ?region= ?lat=&lng=&z=) and accessibility. */

const DATA_URL = "temples.json";

const TRAD = {
  BAPS:         { label: "BAPS Swaminarayan",    short: "BAPS",          color: "#B8922F" },
  ISKCON:       { label: "ISKCON / Vaishnava",   short: "ISKCON",        color: "#2E4A6B" },
  Saiva:        { label: "Saiva / Tamil",        short: "Saiva / Tamil", color: "#BE3524" },
  Swaminarayan: { label: "Swaminarayan (other)", short: "Swaminarayan",  color: "#C56A2A" },
  General:      { label: "Sanatan / community",  short: "Community",     color: "#0E6B67" }
};
const REGIONS = ["London","South East","South West","East of England","East Midlands","West Midlands",
  "Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"];
const UK_VIEW = { center: [54.2, -2.8], zoom: 6 };

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));

const state = { data: [], user: null, region: "", county: "", trad: "", q: "" };
let map, markersById = {}, linesLayer, userMarker, pinMode = false, ready = false;

/* ---------------- boot ---------------- */
document.addEventListener("DOMContentLoaded", init);

async function init() {
  buildMap();
  buildLegend();
  bindUI();

  const params = new URLSearchParams(location.search);
  try {
    const res = await fetch(DATA_URL, { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const raw = await res.json();
    state.data = raw.map((t, i) => ({ id: i, ...t }));
    destack(state.data);
    addMarkers();
    populateFilters();
    ready = true;
    $("mapStatus").hidden = true;
    applyParams(params);
    render();
    if (params.get("postcode")) { $("pc").value = params.get("postcode"); geocode(); }
    else if (params.get("lat") && params.get("lng")) {
      map.setView([+params.get("lat"), +params.get("lng")], +(params.get("z") || 12));
    }
  } catch (err) {
    console.error("Data load failed:", err);
    showLoadError();
  }
}

/* ---------------- map ---------------- */
function buildMap() {
  map = L.map("map", { zoomControl: true }).setView(UK_VIEW.center, UK_VIEW.zoom);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19
  }).addTo(map);
  linesLayer = L.layerGroup().addTo(map);
  map.on("click", (e) => {
    if (!pinMode) return;
    setPinMode(false);
    setUser(e.latlng.lat, e.latlng.lng, "Nearest to <b>your pin</b>");
  });
}

/* temples sharing an exact coordinate get fanned out so every pin stays tappable */
function destack(list) {
  const groups = {};
  list.forEach((t) => {
    const k = t.lat.toFixed(4) + "," + t.lng.toFixed(4);
    (groups[k] = groups[k] || []).push(t);
  });
  Object.values(groups).forEach((g) => {
    if (g.length === 1) { g[0].dlat = g[0].lat; g[0].dlng = g[0].lng; return; }
    const rad = 0.0016 + 0.0007 * Math.min(g.length, 8);
    g.forEach((t, i) => {
      const a = (2 * Math.PI * i) / g.length;
      t.dlat = t.lat + rad * Math.sin(a);
      t.dlng = t.lng + rad * Math.cos(a) / Math.cos((t.lat * Math.PI) / 180);
    });
  });
}

function markerIcon(t) {
  const size = t.hl ? 17 : 13;
  const color = (TRAD[t.trad] || TRAD.General).color;
  const cls = "tmarker" + (t.hl ? " feat" : "");
  return L.divIcon({ className: "", iconSize: [size, size], iconAnchor: [size / 2, size / 2],
    html: `<div class="${cls}" style="width:${size}px;height:${size}px;background:${color}"></div>` });
}

function addMarkers() {
  state.data.forEach((t) => {
    const m = L.marker([t.dlat, t.dlng], { icon: markerIcon(t), alt: t.name });
    m.bindPopup(popupHTML(t), { maxWidth: 270 });
    m.on("click", () => scrollToCard(t.id));
    m.addTo(map);
    markersById[t.id] = m;
  });
}

const dirLink = (t) => `https://www.google.com/maps/dir/?api=1&destination=${t.lat},${t.lng}`;

function popupHTML(t) {
  const loc = [t.area, t.region].filter(Boolean).join(" · ");
  return `<div>
    <p class="pop-name">${esc(t.name)}${t.hl ? " ★" : ""}</p>
    <p class="pop-loc">${esc(loc)}</p>
    <p class="pop-addr">${esc(t.addr)}</p>
    ${t.hours ? `<p class="pop-hours">Hours: ${esc(t.hours)}</p>` : ""}
    <div class="pop-links">
      <a href="${dirLink(t)}" target="_blank" rel="noopener">Directions →</a>
      ${t.url ? `<a href="${esc(t.url)}" target="_blank" rel="noopener">Website</a>` : ""}
      ${t.phone ? `<a href="tel:${esc(t.phone.replace(/\s/g, ""))}">Call</a>` : ""}
    </div></div>`;
}

/* ---------------- distance + direction lines ---------------- */
function haversine(a, b, c, d) {
  const R = 3958.8, r = Math.PI / 180;
  const x = Math.sin((c - a) * r / 2) ** 2 +
            Math.cos(a * r) * Math.cos(c * r) * Math.sin((d - b) * r / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(x));
}
function bearing(a, b, c, d) {
  const r = Math.PI / 180;
  const y = Math.sin((d - b) * r) * Math.cos(c * r);
  const x = Math.cos(a * r) * Math.sin(c * r) - Math.sin(a * r) * Math.cos(c * r) * Math.cos((d - b) * r);
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}
/* dashed sightlines from the searched point to the nearest four matches */
function drawLines(list) {
  linesLayer.clearLayers();
  if (!state.user) return;
  list.slice(0, 4).forEach((t) => {
    L.polyline([[state.user.lat, state.user.lng], [t.dlat, t.dlng]],
      { color: "#2E4A6B", weight: 2, opacity: 0.65, dashArray: "3 6" })
      .addTo(linesLayer);
    const rot = bearing(state.user.lat, state.user.lng, t.dlat, t.dlng);
    L.marker([t.dlat, t.dlng], { interactive: false, zIndexOffset: 400,
      icon: L.divIcon({ className: "", iconSize: [10, 10], iconAnchor: [5, 5],
        html: `<div class="arrowhead" style="transform:rotate(${rot}deg)"></div>` }) })
      .addTo(linesLayer);
  });
}

/* ---------------- filters + state ---------------- */
function populateFilters() {
  REGIONS.filter((r) => state.data.some((t) => t.region === r))
    .forEach((r) => $("fRegion").insertAdjacentHTML("beforeend", `<option>${esc(r)}</option>`));
  Object.keys(TRAD).forEach((k) =>
    $("fTrad").insertAdjacentHTML("beforeend", `<option value="${k}">${TRAD[k].label}</option>`));
  refreshCounties();
}
function refreshCounties() {
  const set = [...new Set(state.data
    .filter((t) => !state.region || t.region === state.region)
    .map((t) => t.county))].sort();
  $("fCounty").innerHTML = '<option value="">All counties</option>' +
    set.map((c) => `<option${c === state.county ? " selected" : ""}>${esc(c)}</option>`).join("");
}

function currentList() {
  const q = state.q.toLowerCase();
  let list = state.data.filter((t) =>
    (!state.region || t.region === state.region) &&
    (!state.county || t.county === state.county) &&
    (!state.trad || t.trad === state.trad) &&
    (!q || t.name.toLowerCase().includes(q) || t.area.toLowerCase().includes(q)));
  if (state.user) {
    list.forEach((t) => (t.dist = haversine(state.user.lat, state.user.lng, t.lat, t.lng)));
    list.sort((a, b) => a.dist - b.dist);
  } else {
    const rank = (r) => { const i = REGIONS.indexOf(r); return i < 0 ? 99 : i; };
    list.sort((a, b) => rank(a.region) - rank(b.region) ||
      a.county.localeCompare(b.county) || a.name.localeCompare(b.name));
  }
  return list;
}

function syncURL() {
  const p = new URLSearchParams();
  if (state.region) p.set("region", state.region);
  if (state.county) p.set("county", state.county);
  if (state.trad) p.set("trad", state.trad);
  if (state.q) p.set("q", state.q);
  const pc = $("pc").value.trim();
  if (state.user && pc) p.set("postcode", pc);
  const qs = p.toString();
  history.replaceState(null, "", qs ? "?" + qs : location.pathname);
}
function applyParams(p) {
  if (p.get("region") && REGIONS.includes(p.get("region"))) {
    state.region = p.get("region"); $("fRegion").value = state.region; refreshCounties();
  }
  if (p.get("county")) { state.county = p.get("county"); refreshCounties(); $("fCounty").value = state.county; }
  if (p.get("trad") && TRAD[p.get("trad")]) { state.trad = p.get("trad"); $("fTrad").value = state.trad; }
  if (p.get("q")) { state.q = p.get("q"); $("fName").value = state.q; }
}

/* ---------------- rendering ---------------- */
function cardHTML(t) {
  const tr = TRAD[t.trad] || TRAD.General;
  const loc = [t.area, t.region].filter(Boolean).join(" · ");
  const closed = String(t.status || "").toLowerCase() === "closed"
    ? '<span class="chip closed">Closed</span>' : "";
  return `<article class="card${t.hl ? " feat" : ""}" style="--dot:${tr.color}" data-id="${t.id}"
      tabindex="0" role="button" aria-label="Show ${esc(t.name)} on the map">
    <div class="c-top"><h3 class="c-name">${esc(t.name)}${t.hl ? " ★" : ""}</h3></div>
    <p class="c-loc">${esc(loc)}</p>
    <p class="c-addr">${esc(t.addr)}</p>
    ${t.hours ? `<p class="c-hours">Hours: ${esc(t.hours)}</p>` : ""}
    <div class="chips">
      <span class="chip"><span class="swatch" style="background:${tr.color}"></span>${tr.label}</span>
      ${t.hl ? '<span class="chip feat">★ Featured</span>' : ""}${closed}
    </div>
    ${t.note ? `<p class="c-note">${esc(t.note)}</p>` : ""}
    <div class="c-links">
      <a href="${dirLink(t)}" target="_blank" rel="noopener">Directions →</a>
      ${t.url ? `<a href="${esc(t.url)}" target="_blank" rel="noopener">Website</a>` : ""}
      ${t.phone ? `<a href="tel:${esc(t.phone.replace(/\s/g, ""))}">Call</a>` : ""}
    </div>
  </article>`;
}

function render() {
  if (!ready) return;
  const list = currentList();
  $("count").innerHTML = `<b>${list.length}</b> temple${list.length === 1 ? "" : "s"}`;

  const shown = new Set(list.map((t) => t.id));
  Object.entries(markersById).forEach(([id, m]) => m.setOpacity(shown.has(+id) ? 1 : 0.18));

  if (!list.length) {
    $("results").innerHTML = `<div class="empty"><p class="big">No temples match</p>
      <p>Try widening the region, or <button type="button" class="linklike" id="emptyClear">clear all filters</button>.</p></div>`;
    const b = $("emptyClear"); if (b) b.addEventListener("click", clearAll);
    linesLayer.clearLayers();
    return;
  }
  if (state.user) drawLines(list); else linesLayer.clearLayers();

  $("results").innerHTML = list.map(cardHTML).join("");
  $("results").querySelectorAll(".card").forEach((card) => {
    const open = (e) => {
      if (e.target.closest("a")) return;
      focusTemple(+card.dataset.id);
    };
    card.addEventListener("click", open);
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(e); }
    });
  });
}

function focusTemple(id) {
  const t = state.data.find((x) => x.id === id);
  if (!t) return;
  map.flyTo([t.dlat, t.dlng], 14, { duration: 0.6 });
  markersById[id].openPopup();
  if (window.matchMedia("(max-width:899px)").matches) {
    document.querySelector(".map-wrap").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
function scrollToCard(id) {
  const el = $("results").querySelector(`.card[data-id="${id}"]`);
  if (!el) return;
  el.scrollIntoView({ behavior: "smooth", block: "center" });
  el.style.borderColor = "var(--saffron)";
  setTimeout(() => (el.style.borderColor = ""), 1200);
}

/* ---------------- location ---------------- */
function setHint(html) { $("hint").innerHTML = html; }

async function geocode() {
  const raw = $("pc").value.trim();
  if (!raw) { setHint("Enter a UK postcode to rank temples by distance."); return; }
  const pc = raw.toUpperCase().replace(/\s+/g, "");
  setHint("Looking up postcode…");
  try {
    let r = await fetch(`https://api.postcodes.io/postcodes/${encodeURIComponent(pc)}`);
    let j = await r.json();
    if (j.status === 200) return setUser(j.result.latitude, j.result.longitude,
      `Nearest to <b>${esc(j.result.postcode)}</b>`);
    const out = pc.replace(/\d[A-Z]{2}$/, "");
    r = await fetch(`https://api.postcodes.io/outcodes/${encodeURIComponent(out)}`);
    j = await r.json();
    if (j.status === 200) return setUser(j.result.latitude, j.result.longitude,
      `Approximate area <b>${esc(j.result.outcode)}</b> (full postcode not found)`);
    setHint('<span class="err">Postcode not recognised.</span> Check it, or drop a pin on the map instead.');
  } catch {
    setHint('<span class="err">Couldn\u2019t reach the postcode service.</span> Try again, or drop a pin on the map.');
  }
}

function setUser(lat, lng, msg) {
  state.user = { lat, lng };
  if (userMarker) userMarker.remove();
  userMarker = L.marker([lat, lng], { zIndexOffset: 1000, alt: "Your location",
    icon: L.divIcon({ className: "", iconSize: [15, 15], iconAnchor: [7.5, 7.5],
      html: '<div class="you-dot you-pulse" style="width:15px;height:15px"></div>' }) }).addTo(map);
  render();
  syncURL();
  const list = currentList();
  if (list.length) {
    const n = list[0];
    setHint(`${msg} — lines point to your four nearest temples. Closest is <b>${esc(n.name)}</b>.`);
    map.flyTo([n.dlat, n.dlng], 11, { duration: 0.7 });
    setTimeout(() => markersById[n.id].openPopup(), 750);
  } else {
    setHint(msg + " — no temples match your current filters.");
  }
}

function setPinMode(on) {
  pinMode = on;
  $("pin").setAttribute("aria-pressed", String(on));
  if (on) setHint("Tap anywhere on the map to set your location.");
}

function clearAll() {
  state.region = state.county = state.trad = state.q = "";
  state.user = null;
  $("fRegion").value = ""; $("fTrad").value = ""; $("fName").value = ""; $("pc").value = "";
  refreshCounties();
  if (userMarker) { userMarker.remove(); userMarker = null; }
  linesLayer.clearLayers();
  setPinMode(false);
  setHint("Filters and location cleared. Enter a postcode to rank by distance.");
  map.flyTo(UK_VIEW.center, UK_VIEW.zoom, { duration: 0.6 });
  history.replaceState(null, "", location.pathname);
  render();
}

/* ---------------- legend + errors ---------------- */
function buildLegend() {
  $("legendRows").innerHTML = Object.keys(TRAD).map((k) =>
    `<div class="row"><span class="swatch" style="background:${TRAD[k].color}"></span>${TRAD[k].short}</div>`
  ).join("") +
  `<div class="row"><span class="swatch ring" style="background:var(--vermilion)"></span>Featured</div>`;
}

function showLoadError() {
  $("mapStatus").hidden = true;
  $("count").textContent = "";
  $("results").innerHTML = `<div class="error-card"><p class="big">The temple list didn\u2019t load</p>
    <p>Check your connection, then <button type="button" class="linklike" id="retry">try again</button>.</p></div>`;
  $("retry").addEventListener("click", () => location.reload());
}

/* ---------------- events ---------------- */
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }

function bindUI() {
  $("go").addEventListener("click", geocode);
  $("pc").addEventListener("keydown", (e) => { if (e.key === "Enter") geocode(); });

  $("geo").addEventListener("click", () => {
    if (!navigator.geolocation) { setHint("Location isn\u2019t available in this browser."); return; }
    setHint("Getting your location…");
    navigator.geolocation.getCurrentPosition(
      (p) => setUser(p.coords.latitude, p.coords.longitude, "Nearest to <b>your location</b>"),
      () => setHint('<span class="err">Location permission denied.</span> Enter a postcode or drop a pin instead.'),
      { enableHighAccuracy: true, timeout: 8000 });
  });

  $("pin").addEventListener("click", () => setPinMode(!pinMode));

  $("fRegion").addEventListener("change", (e) => {
    state.region = e.target.value; state.county = ""; refreshCounties(); render(); syncURL();
  });
  $("fCounty").addEventListener("change", (e) => { state.county = e.target.value; render(); syncURL(); });
  $("fTrad").addEventListener("change", (e) => { state.trad = e.target.value; render(); syncURL(); });
  $("fName").addEventListener("input", debounce((e) => { state.q = e.target.value.trim(); render(); syncURL(); }, 150));

  $("clear").addEventListener("click", clearAll);
  $("legendToggle").addEventListener("click", () => {
    const lg = $("legend");
    const collapsed = lg.classList.toggle("collapsed");
    $("legendToggle").setAttribute("aria-expanded", String(!collapsed));
  });
}
