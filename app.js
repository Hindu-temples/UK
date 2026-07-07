const FORM_URL = "mailto:hindu.temples.uk@gmail.com?subject=Temple%20submission%20%E2%80%93%20hindu-temples.uk&body=Temple%20name%3A%0AAddress%20%2F%20postcode%3A%0AWhat%27s%20new%2C%20closed%2C%20or%20wrong%3A%0AOpening%20hours%20(if%20known)%3A%0AWebsite%20%2F%20social%20links%3A%0A";  // Works now (opens email). To use a Google Form instead, paste its link here.
const RAW = await (await fetch(new URL('./temples.json', import.meta.url), {cache:'no-store'})).json();
const T = RAW.map((r,i)=>Object.assign({id:i},r));

const TRAD = {
  BAPS:        {label:"BAPS Swaminarayan",short:"BAPS",   color:"#C29A2B"},
  ISKCON:      {label:"ISKCON / Vaishnava",short:"ISKCON",  color:"#2E4A6B"},
  Saiva:       {label:"Saiva / Tamil",short:"Saiva / Tamil",       color:"#C2362B"},
  Swaminarayan:{label:"Swaminarayan (other)",short:"Swaminarayan",color:"#C56A2A"},
  General:     {label:"Sanatan / community",short:"Community", color:"#0F6E6A"}
};
const REGION_ORDER = ["London","South East","South West","East of England","East Midlands","West Midlands","Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"];
const regionRank = r => {const i=REGION_ORDER.indexOf(r);return i<0?99:i;};

/* de-stack temples sharing an exact coordinate so pins stay separately clickable */
(function(){
  const g={};
  T.forEach(t=>{const k=t.lat.toFixed(4)+","+t.lng.toFixed(4);(g[k]=g[k]||[]).push(t);});
  Object.values(g).forEach(a=>{
    if(a.length===1){a[0].dlat=a[0].lat;a[0].dlng=a[0].lng;return;}
    const n=a.length,rad=0.0016+0.0007*Math.min(n,8);
    a.forEach((t,i)=>{const ang=2*Math.PI*i/n;
      t.dlat=t.lat+rad*Math.sin(ang);
      t.dlng=t.lng+rad*Math.cos(ang)/Math.cos(t.lat*Math.PI/180);});
  });
})();

/* ---------- map ---------- */
const map = L.map('map',{zoomControl:true,attributionControl:true}).setView([54.2,-2.6],6);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{
  attribution:'&copy; OpenStreetMap &copy; CARTO',subdomains:'abcd',maxZoom:19
}).addTo(map);

function markerHTML(t,size){
  const c=(TRAD[t.trad]||TRAD.General).color;
  const cls='tmarker'+(t.hl?' feat':'');
  return L.divIcon({className:'',html:`<div class="${cls}" style="width:${size}px;height:${size}px;background:${c}"></div>`,iconSize:[size,size],iconAnchor:[size/2,size/2]});
}
const markers={};
T.forEach(t=>{
  const m=L.marker([t.dlat,t.dlng],{icon:markerHTML(t,t.hl?17:13)}).addTo(map);
  m.bindPopup(popupHTML(t),{maxWidth:260});
  m.on('click',()=>{highlightCard(t.id);});
  markers[t.id]=m;
});

function gmaps(t){return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(t.name+', '+t.addr)}`;}
function dirLink(t){return `https://www.google.com/maps/dir/?api=1&destination=${t.lat},${t.lng}`;}
function popupHTML(t){
  const loc=[t.area,t.region].filter(Boolean).join(' · ');
  return `<div><p class="pop-name">${t.name}${t.hl?' ★':''}</p>
    <p class="pop-loc">${loc}${t.approx?' · approx. location':''}</p>
    <p class="pop-addr">${t.addr}</p>
    ${t.hours?`<p class="pop-hours">Hours: ${t.hours}</p>`:''}
    <div class="pop-links"><a href="${dirLink(t)}" target="_blank" rel="noopener">Directions →</a>
    ${t.url?`<a href="${t.url}" target="_blank" rel="noopener">Website</a>`:''}
    ${t.phone?`<a href="tel:${t.phone.replace(/\s/g,'')}">Call</a>`:''}</div></div>`;
}

/* ---------- state & filters ---------- */
let user=null,userMarker=null,pinMode=false;
const el=id=>document.getElementById(id);

function haversine(a,b,c,d){const R=3958.8,r=Math.PI/180;
  const x=Math.sin((c-a)*r/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin((d-b)*r/2)**2;
  return R*2*Math.asin(Math.sqrt(x));}
const linesLayer=L.layerGroup().addTo(map);
function bearing(a,b,c,d){const R=Math.PI/180,D=180/Math.PI;const dl=(d-b)*R;
  const y=Math.sin(dl)*Math.cos(c*R),x=Math.cos(a*R)*Math.sin(c*R)-Math.sin(a*R)*Math.cos(c*R)*Math.cos(dl);
  return (Math.atan2(y,x)*D+360)%360;}
function drawLines(list){linesLayer.clearLayers();if(!user)return;
  list.forEach(t=>{const poly=L.polyline([[user.lat,user.lng],[t.dlat,t.dlng]],{color:'#2E4A6B',weight:2,opacity:.65,dashArray:'3 6'});
    const d=(t.dist!=null?t.dist:haversine(user.lat,user.lng,t.lat,t.lng));
    poly.bindTooltip(d.toFixed(1)+' mi',{permanent:true,direction:'center',className:'dist-tip'});poly.addTo(linesLayer);
    const brg=bearing(user.lat,user.lng,t.dlat,t.dlng);
    L.marker([t.dlat,t.dlng],{interactive:false,zIndexOffset:400,icon:L.divIcon({className:'',html:'<div class="arrowhead" style="transform:rotate('+brg+'deg)"></div>',iconSize:[10,10],iconAnchor:[5,5]})}).addTo(linesLayer);});}

// populate region + tradition selects
REGION_ORDER.filter(r=>T.some(t=>t.region===r)).forEach(r=>{
  el('fRegion').insertAdjacentHTML('beforeend',`<option>${r}</option>`);});
Object.keys(TRAD).forEach(k=>{
  el('fTrad').insertAdjacentHTML('beforeend',`<option value="${k}">${TRAD[k].label}</option>`);});
// legend
el('legendRows').innerHTML=Object.keys(TRAD).map(k=>
  `<div class="row"><span class="swatch" style="background:${TRAD[k].color}"></span>${TRAD[k].short}</div>`).join('');

function refreshCounties(){
  const reg=el('fRegion').value;
  const set=[...new Set(T.filter(t=>!reg||t.region===reg).map(t=>t.county))].sort();
  el('fCounty').innerHTML='<option value="">All counties</option>'+set.map(c=>`<option>${c}</option>`).join('');
}
refreshCounties();

function currentList(){
  const reg=el('fRegion').value,cty=el('fCounty').value,tr=el('fTrad').value,nm=el('fName').value.trim().toLowerCase();
  let a=T.filter(t=>(!reg||t.region===reg)&&(!cty||t.county===cty)&&(!tr||t.trad===tr)&&(!nm||t.name.toLowerCase().includes(nm)||t.area.toLowerCase().includes(nm)));
  if(user){a.forEach(t=>t.dist=haversine(user.lat,user.lng,t.lat,t.lng));a.sort((x,y)=>x.dist-y.dist);}
  else{a.sort((x,y)=>regionRank(x.region)-regionRank(y.region)||x.county.localeCompare(y.county)||x.name.localeCompare(y.name));}
  return a;
}

function render(){
  const a=currentList();
  el('count').innerHTML=`<b>${a.length}</b> temple${a.length!==1?'s':''}`+(user?' · nearest first':'');
  const list=el('list');
  if(!a.length){list.innerHTML=`<div class="empty"><div class="big">No temples match</div>Try widening the region or clearing the name search.</div>`;
    for(const id in markers)markers[id].setOpacity(.25);linesLayer.clearLayers();return;}
  const shown=new Set(a.map(t=>t.id));
  for(const id in markers)markers[id].setOpacity(shown.has(+id)?1:.2);
  if(user)drawLines(a.slice(0,4));else linesLayer.clearLayers();
  list.innerHTML=a.map(t=>{
    const c=(TRAD[t.trad]||TRAD.General).color;
    const loc=[t.area,t.region].filter(Boolean).join(' · ');
    const dist=(user&&t.dist!=null)?`<span class="c-dist">${t.dist<0.1?'here':t.dist.toFixed(1)+' mi'}</span>`:'';
    return `<div class="card${t.hl?' feat':''}" style="--dot:${c}" data-id="${t.id}">
      <div class="c-top"><h3 class="c-name">${t.name}${t.hl?' ★':''}</h3>${dist}</div>
      <p class="c-loc">${loc}${t.approx?' · <i>approx. location</i>':''}</p>
      <p class="c-addr">${t.addr}</p>
      ${t.hours?`<p class="c-hours">Hours: ${t.hours}</p>`:''}
      <div class="chips">
        <span class="chip"><span class="swatch" style="background:${c}"></span>${(TRAD[t.trad]||TRAD.General).label}</span>
        ${t.hl?'<span class="chip feat">★ Featured</span>':''}
        ${t.status&&t.status.toLowerCase()==='closed'?'<span class="chip closed">Closed</span>':''}
      </div>
      ${t.note?`<p class="c-note">${t.note}</p>`:''}
      <div class="c-links"><a href="${dirLink(t)}" target="_blank" rel="noopener">Directions →</a>
      ${t.url?`<a href="${t.url}" target="_blank" rel="noopener">Website</a>`:''}
      ${t.phone?`<a href="tel:${t.phone.replace(/\s/g,'')}">Call</a>`:''}</div>
    </div>`;}).join('');
  [...list.querySelectorAll('.card')].forEach(card=>{
    card.addEventListener('click',e=>{if(e.target.closest('a'))return;
      const id=+card.dataset.id,t=T.find(x=>x.id===id);
      map.flyTo([t.dlat,t.dlng],14,{duration:.6});markers[id].openPopup();});
  });
}

function highlightCard(id){
  const card=el('list').querySelector(`.card[data-id="${id}"]`);
  if(card){card.scrollIntoView({behavior:'smooth',block:'center'});
    card.style.borderColor='var(--saffron)';setTimeout(()=>card.style.borderColor='',1200);}
}

/* ---------- geocoding ---------- */
async function geocode(){
  const raw=el('pc').value.trim();if(!raw){setHint('Enter a UK postcode to find your nearest temple.');return;}
  const pc=raw.toUpperCase().replace(/\s+/g,'');
  setHint('Looking up postcode…');
  try{
    let r=await fetch(`https://api.postcodes.io/postcodes/${encodeURIComponent(pc)}`);
    let j=await r.json();
    if(j.status===200){return setUser(j.result.latitude,j.result.longitude,`Nearest to <b>${j.result.postcode}</b>`);}
    // fallback: outward code
    const out=pc.replace(/\d[A-Z]{2}$/,'');
    r=await fetch(`https://api.postcodes.io/outcodes/${encodeURIComponent(out)}`);j=await r.json();
    if(j.status===200){return setUser(j.result.latitude,j.result.longitude,`Approximate area <b>${j.result.outcode}</b> (full postcode not found)`);}
    setHint('<span class="err">Postcode not recognised.</span> Check it, or drop a pin on the map instead.');
  }catch(e){setHint('<span class="err">Couldn\'t reach the postcode service.</span> Try dropping a pin on the map.');}
}
function setUser(lat,lng,msg){
  user={lat,lng};
  if(userMarker)userMarker.remove();
  userMarker=L.marker([lat,lng],{icon:L.divIcon({className:'',html:'<div class="you-dot you-pulse" style="width:15px;height:15px"></div>',iconSize:[15,15],iconAnchor:[7.5,7.5]}),zIndexOffset:1000}).addTo(map);
  render();
  const a=currentList();
  if(a.length){const n=a[0];setHint(`${msg} — closest is <b>${n.name}</b>, ${n.dist.toFixed(1)} mi away.`);
    map.flyTo([n.dlat,n.dlng],11,{duration:.7});setTimeout(()=>markers[n.id].openPopup(),700);}
  else setHint(msg+' — but no temples match your current filters.');
}
function setHint(h){el('hint').innerHTML=h;}

/* ---------- events ---------- */
el('go').onclick=geocode;
el('pc').addEventListener('keydown',e=>{if(e.key==='Enter')geocode();});
el('geo').onclick=()=>{
  if(!navigator.geolocation){setHint('Location isn\'t available in this browser.');return;}
  setHint('Getting your location…');
  navigator.geolocation.getCurrentPosition(
    p=>setUser(p.coords.latitude,p.coords.longitude,'Nearest to <b>your location</b>'),
    ()=>setHint('<span class="err">Location permission denied.</span> Enter a postcode or drop a pin instead.'),
    {enableHighAccuracy:true,timeout:8000});
};
el('pin').onclick=()=>{pinMode=!pinMode;
  el('pin').style.background=pinMode?'var(--saffron)':'';el('pin').style.color=pinMode?'#fff':'';
  setHint(pinMode?'Tap anywhere on the map to set your location.':'Pin mode off.');};
map.on('click',e=>{if(!pinMode)return;pinMode=false;el('pin').style.background='';el('pin').style.color='';
  setUser(e.latlng.lat,e.latlng.lng,'Nearest to <b>your pin</b>');});

el('fRegion').onchange=()=>{refreshCounties();render();};
el('fCounty').onchange=render;
el('fTrad').onchange=render;
el('fName').addEventListener('input',render);
el('clear').onclick=()=>{
  el('fRegion').value='';el('fCounty').value='';el('fTrad').value='';el('fName').value='';refreshCounties();
  user=null;if(userMarker){userMarker.remove();userMarker=null;}el('pc').value='';
  setHint('Filters and location cleared. Enter a postcode to rank by distance.');
  map.flyTo([54.2,-2.6],6,{duration:.6});render();};

el('aboutBtn').onclick=()=>el('aboutModal').classList.add('open');
el('reportBtn').onclick=()=>window.open(FORM_URL,'_blank','noopener');
el('legendToggle').onclick=()=>el('legend').classList.toggle('collapsed');
el('aboutClose').onclick=()=>el('aboutModal').classList.remove('open');
el('aboutModal').addEventListener('click',e=>{if(e.target===el('aboutModal'))el('aboutModal').classList.remove('open');});

render();
