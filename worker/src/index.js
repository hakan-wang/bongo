// Assay live demo — REAL model calls + REAL ground-truth checks. No mock data.
// HERO (/) = the Miru use case: AI finds UGC creators; cheap model invents fakes to fill the
// request; Assay catches them against the verified creator database and returns only real ones.
// /trivia = the simple version (cheap model gets trick questions wrong, Assay catches+fixes).
// Needs a server-side secret: MISTRAL_API_KEY  (set: wrangler secret put MISTRAL_API_KEY)

const CHEAP = "mistral-small-latest";
const STRONG = "mistral-large-latest";

// Miru's "verified creator database" = the ground truth. (Fictional roster for the demo.)
const ROSTER = [
  { handle: "@liftwithmaya", niche: "fitness", followers: "240k" },
  { handle: "@theleankitchen", niche: "fitness", followers: "180k" },
  { handle: "@runnerjo", niche: "fitness", followers: "95k" },
  { handle: "@glowbyامira", niche: "beauty", followers: "310k" },
  { handle: "@matteandmore", niche: "beauty", followers: "150k" },
  { handle: "@pixelpalkev", niche: "gaming", followers: "420k" },
  { handle: "@noscopenina", niche: "gaming", followers: "210k" },
  { handle: "@forkfultom", niche: "food", followers: "260k" },
  { handle: "@spicebydina", niche: "food", followers: "130k" },
  { handle: "@gadgetgwen", niche: "tech", followers: "200k" },
];

const BRIEFS = [
  { id: "fitness", label: "Vegan protein bar — find 5 fitness creators", niche: "fitness", n: 5 },
  { id: "beauty", label: "New mascara launch — find 4 beauty creators", niche: "beauty", n: 4 },
  { id: "gaming", label: "Indie game launch — find 4 gaming creators", niche: "gaming", n: 4 },
];

const norm = s => String(s).toLowerCase().replace(/[^a-z0-9@]/g, "");
const rosterSet = new Map(ROSTER.map(c => [norm(c.handle), c]));

async function callModel(env, model, prompt) {
  const res = await fetch("https://api.mistral.ai/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": "Bearer " + env.MISTRAL_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({ model, temperature: 0.4, messages: [{ role: "user", content: prompt }] }),
  });
  if (!res.ok) throw new Error("model " + model + " HTTP " + res.status + ": " + (await res.text()).slice(0, 160));
  return ((await res.json()).choices?.[0]?.message?.content || "").trim();
}

function extractHandles(text) {
  // pull @handles or quoted handles out of whatever the model returned
  const m = text.match(/@[^\s",\]]+/g) || [];
  return [...new Set(m)];
}

// verify a recommended handle against the verified DB (ground truth) + the requested niche
function verify(handle, niche) {
  const hit = rosterSet.get(norm(handle));
  if (!hit) return { handle, ok: false, reason: "not in the verified database (invented)" };
  if (hit.niche !== niche) return { handle, ok: false, reason: "real, but wrong niche (" + hit.niche + ")" };
  return { handle, ok: true, reason: "verified " + hit.niche + " creator, " + hit.followers };
}

async function handleFind(env, briefId) {
  if (!env.MISTRAL_API_KEY) return json({ error: "No MISTRAL_API_KEY set. Run: wrangler secret put MISTRAL_API_KEY (this makes REAL calls)." }, 400);
  const brief = BRIEFS.find(b => b.id === briefId) || BRIEFS[0];
  const dbText = ROSTER.map(c => c.handle + " (" + c.niche + ", " + c.followers + ")").join(", ");

  // 1) CHEAP model: asked for more creators than the niche actually has -> it tends to invent some.
  const cheapPrompt =
    "You are a UGC creator-matching assistant. Here is our creator database: " + dbText +
    ".\nThe brand brief: " + brief.label + ".\nList exactly " + brief.n +
    " creator handles for this brief. Reply with just the @handles, comma-separated.";
  const cheapRaw = await callModel(env, CHEAP, cheapPrompt);
  const cheapPicks = extractHandles(cheapRaw).slice(0, brief.n).map(h => verify(h, brief.niche));
  const fakes = cheapPicks.filter(p => !p.ok);

  let final, fixedNote;
  if (fakes.length === 0) {
    final = cheapPicks;
    fixedNote = "Cheap model's picks all checked out.";
  } else {
    // 2) Assay caught fakes -> escalate to STRONG model with a strict instruction
    const strongPrompt =
      "Creator database (the ONLY valid creators): " + dbText +
      ".\nBrief: " + brief.label +
      ".\nReturn ONLY handles that appear in the database AND match the niche. " +
      "If fewer than " + brief.n + " match, return only those, do NOT invent any. Reply with just @handles, comma-separated.";
    const strongRaw = await callModel(env, STRONG, strongPrompt);
    const strongPicks = extractHandles(strongRaw).map(h => verify(h, brief.niche)).filter(p => p.ok);
    // dedupe
    const seen = new Set(); final = [];
    for (const p of strongPicks) { if (!seen.has(norm(p.handle))) { seen.add(norm(p.handle)); final.push(p); } }
    fixedNote = "Assay caught " + fakes.length + " invented creator" + (fakes.length > 1 ? "s" : "") +
      " and returned only the " + final.length + " real, on-niche matches.";
  }

  return json({ brief: brief.label, requested: brief.n, cheap: cheapPicks, caught: fakes.length, final, fixedNote });
}

function json(o, s = 200) { return new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }); }

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/find") return handleFind(env, url.searchParams.get("brief"));
    if (url.pathname === "/briefs") return json({ briefs: BRIEFS });
    return new Response(PAGE, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  },
};

const PAGE = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Assay × Miru — live</title>
<style>
:root{--bg:#06080a;--panel:#0d0f15;--line:#1b1f2b;--text:#eaf1f6;--muted:#7b8a98;--green:#22e3a0;--red:#ff5d6c;--amber:#ffc861;--sans:-apple-system,"SF Pro Display",system-ui,sans-serif;--mono:"SF Mono",ui-monospace,Menlo,monospace}
*{margin:0;padding:0;box-sizing:border-box}body{background:radial-gradient(1000px 500px at 50% -10%,#10161f,var(--bg));color:var(--text);font-family:var(--sans);min-height:100vh;display:flex;justify-content:center;padding:40px 20px}
.wrap{width:100%;max-width:720px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);display:flex;gap:8px;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green)}
h1{font-size:28px;font-weight:750;letter-spacing:-.02em;margin:10px 0 4px}
.sub{color:var(--muted);font-size:15px;margin-bottom:18px}
select,.run{font-family:var(--sans);font-size:14px}
select{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:11px 12px;width:100%;margin-bottom:10px}
.run{border:0;border-radius:12px;padding:13px 20px;font-weight:650;cursor:pointer;background:linear-gradient(180deg,#fff,#cdd7ee);color:#0a0c12;width:100%}
.run:disabled{opacity:.5}
.col{margin-top:18px}.h{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:14px 0 8px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px;margin-top:8px;display:flex;justify-content:space-between;gap:10px;align-items:center;opacity:0;transform:translateY(5px);transition:.3s;font-family:var(--mono);font-size:13.5px}
.card.show{opacity:1;transform:none}
.card.bad{border-color:rgba(255,93,108,.4);background:rgba(255,93,108,.06)}
.card.good{border-color:rgba(46,230,166,.35);background:rgba(46,230,166,.05)}
.badge{font-size:10px;padding:3px 9px;border-radius:20px;white-space:nowrap}
.b-bad{background:rgba(255,93,108,.15);color:var(--red)}.b-good{background:rgba(46,230,166,.15);color:var(--green)}
.reason{color:var(--muted);font-size:11.5px}
.board{margin-top:18px;background:linear-gradient(180deg,rgba(46,230,166,.08),transparent);border:1px solid rgba(46,230,166,.3);border-radius:12px;padding:16px;font-size:15px;display:none}
.board.show{display:block}.board b{color:var(--green)}
.err{color:var(--red);font-family:var(--mono);font-size:13px;margin-top:14px}
.foot{margin-top:20px;font-family:var(--mono);font-size:11px;color:var(--muted)}
</style></head><body><div class="wrap">
<div class="eyebrow"><span class="dot"></span> Assay × Miru · live · real model calls</div>
<h1>The AI invented creators. Assay caught them.</h1>
<div class="sub">A brand asks Miru's AI to find UGC creators. The cheap model makes some up to fill the brief. Assay checks every pick against the verified creator database and hands back only the real ones.</div>
<select id="brief"></select>
<button class="run" id="run">▶ Find creators (live)</button>
<div id="cheapcol"></div>
<div id="finalcol"></div>
<div class="board" id="board"></div>
<div class="foot">cheap = mistral-small · checked against Miru's verified database, not another AI · nothing pre-recorded</div>
</div><script>
const $=s=>document.querySelector(s);
fetch("/briefs").then(r=>r.json()).then(d=>{$("#brief").innerHTML=d.briefs.map(b=>'<option value="'+b.id+'">'+b.label+'</option>').join("");}).catch(()=>{});
$("#run").addEventListener("click",async()=>{
  const b=$("#run");b.disabled=true;b.textContent="finding live…";
  $("#cheapcol").innerHTML="";$("#finalcol").innerHTML="";$("#board").classList.remove("show");
  let d;try{ d=await (await fetch("/find?brief="+$("#brief").value)).json(); }
  catch(e){ $("#cheapcol").innerHTML='<div class="err">'+e+'</div>'; b.disabled=false;b.textContent="▶ Find creators (live)"; return; }
  if(d.error){ $("#cheapcol").innerHTML='<div class="err">'+d.error+'</div>'; b.disabled=false;b.textContent="▶ Find creators (live)"; return; }
  $("#cheapcol").innerHTML='<div class="h">cheap model returned '+d.cheap.length+' creators</div>';
  for(const c of d.cheap){
    const el=document.createElement("div");el.className="card "+(c.ok?"good":"bad");
    el.innerHTML='<span>'+c.handle+'</span><span class="reason">'+c.reason+'</span><span class="badge '+(c.ok?'b-good':'b-bad')+'">'+(c.ok?'real':'INVENTED')+'</span>';
    $("#cheapcol").appendChild(el);await new Promise(r=>setTimeout(r,250));requestAnimationFrame(()=>el.classList.add("show"));
  }
  await new Promise(r=>setTimeout(r,400));
  $("#finalcol").innerHTML='<div class="h">✓ Assay-verified, sent to the brand</div>';
  for(const c of d.final){
    const el=document.createElement("div");el.className="card good";
    el.innerHTML='<span>'+c.handle+'</span><span class="reason">'+c.reason+'</span><span class="badge b-good">verified</span>';
    $("#finalcol").appendChild(el);await new Promise(r=>setTimeout(r,250));requestAnimationFrame(()=>el.classList.add("show"));
  }
  $("#board").innerHTML=d.fixedNote+' <b>No fake creators reached the brand.</b>';
  $("#board").classList.add("show");
  b.disabled=false;b.textContent="▶ Run again";
});
</script></body></html>`;
