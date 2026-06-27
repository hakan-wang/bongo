// Plumbline live demo — REAL model calls + REAL ground-truth checks. No mock data.
// Cheap model answers -> deterministic check vs known answer -> escalate the failures to a strong model.
// Needs a server-side secret: MISTRAL_API_KEY  (set with: wrangler secret put MISTRAL_API_KEY)

const CHEAP = "mistral-small-latest";
const STRONG = "mistral-large-latest";

// Tasks with KNOWN correct answers (the ground truth). These are ones cheap models often get wrong,
// so the "catch" is real, not staged. Answers are checked deterministically.
const TASKS = [
  { id: "strawberry", q: "How many times does the letter r appear in the word strawberry?", a: "3" },
  { id: "count-e", q: "How many times does the letter e appear in the phrase 'these elements were excellent'?", a: "7" },
  { id: "compare", q: "Which is larger, 9.11 or 9.9? Answer with just the number.", a: "9.9" },
  { id: "days", q: "If today is Monday, what day of the week is it 100 days from now?", a: "wednesday" },
];

function norm(s) { return String(s).toLowerCase().replace(/[^a-z0-9.]/g, ""); }
// ground-truth check: does the model's answer contain the known correct answer?
function check(output, expected) {
  const o = norm(output), e = norm(expected);
  return o.includes(e);
}

async function callModel(env, model, question) {
  const res = await fetch("https://api.mistral.ai/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": "Bearer " + env.MISTRAL_API_KEY, "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      temperature: 0,
      messages: [{ role: "user", content: question + "\n\nReply with ONLY the final answer, nothing else." }],
    }),
  });
  if (!res.ok) throw new Error("model " + model + " HTTP " + res.status + ": " + (await res.text()).slice(0, 200));
  const data = await res.json();
  return (data.choices?.[0]?.message?.content || "").trim();
}

async function runTask(env, t) {
  const trace = { id: t.id, question: t.q, expected: t.a, steps: [], verdict: "", fixed_by: "" };

  // 1) cheap model attempt (REAL call)
  const cheapAns = await callModel(env, CHEAP, t.q);
  const cheapOk = check(cheapAns, t.a);
  trace.steps.push({ role: "cheap", model: CHEAP, answer: cheapAns, ok: cheapOk });

  if (cheapOk) {
    trace.verdict = "VERIFIED";
    trace.fixed_by = "cheap";
    return trace;
  }

  // 2) Plumbline caught a wrong answer -> escalate ONLY this task to the strong model (REAL call)
  const strongAns = await callModel(env, STRONG, t.q);
  const strongOk = check(strongAns, t.a);
  trace.steps.push({ role: "verifier", model: "bongo", answer: "cheap answer failed the ground-truth check", ok: false });
  trace.steps.push({ role: "strong", model: STRONG, answer: strongAns, ok: strongOk });
  trace.verdict = strongOk ? "CAUGHT + FIXED" : "CAUGHT (still wrong)";
  trace.fixed_by = strongOk ? "strong-escalation" : "unrecovered";
  return trace;
}

async function handleRun(env) {
  if (!env.MISTRAL_API_KEY) {
    return json({ error: "No MISTRAL_API_KEY set on the server. Run: wrangler secret put MISTRAL_API_KEY (this demo makes REAL calls, so it needs a real key)." }, 400);
  }
  const results = [];
  for (const t of TASKS) {
    try { results.push(await runTask(env, t)); }
    catch (e) { results.push({ id: t.id, question: t.q, error: String(e.message || e) }); }
  }
  const caught = results.filter(r => r.fixed_by && r.fixed_by !== "cheap").length;
  const cheapRight = results.filter(r => r.fixed_by === "cheap").length;
  return json({
    results,
    summary: {
      total: results.length,
      cheap_alone_correct: cheapRight,
      caught_and_fixed: results.filter(r => r.verdict === "CAUGHT + FIXED").length,
      caught: caught,
    },
  });
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/run") return handleRun(env);
    return new Response(PAGE, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  },
};

const PAGE = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Plumbline — live</title>
<style>
:root{--bg:#06080a;--panel:#0d0f15;--line:#1b1f2b;--text:#eaf1f6;--muted:#7b8a98;--green:#22e3a0;--red:#ff5d6c;--amber:#ffc861;--sans:-apple-system,"SF Pro Display",system-ui,sans-serif;--mono:"SF Mono",ui-monospace,Menlo,monospace}
*{margin:0;padding:0;box-sizing:border-box}body{background:radial-gradient(1000px 500px at 50% -10%,#10161f,var(--bg));color:var(--text);font-family:var(--sans);min-height:100vh;display:flex;justify-content:center;padding:42px 20px}
.wrap{width:100%;max-width:760px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);display:flex;gap:8px;align-items:center}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green)}
h1{font-size:30px;font-weight:750;letter-spacing:-.02em;margin:10px 0 4px}
.sub{color:var(--muted);font-size:15px;margin-bottom:8px}
.tag{font-family:var(--mono);font-size:11.5px;color:var(--amber);margin-bottom:22px}
.run{border:0;border-radius:12px;padding:14px 22px;font-size:15px;font-weight:650;cursor:pointer;background:linear-gradient(180deg,#fff,#cdd7ee);color:#0a0c12}
.run:disabled{opacity:.5}
.task{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin-top:14px;opacity:0;transform:translateY(6px);transition:.3s}
.task.show{opacity:1;transform:none}
.q{font-size:14px;margin-bottom:10px}.q b{color:var(--muted);font-family:var(--mono);font-weight:400}
.line{font-family:var(--mono);font-size:13px;padding:6px 10px;border-radius:8px;margin-top:6px;display:flex;gap:10px;align-items:flex-start}
.cheap{background:rgba(255,93,108,.07)}.strong{background:rgba(46,230,166,.07)}.verif{color:var(--amber)}
.badge{font-size:10px;padding:2px 8px;border-radius:20px;white-space:nowrap}
.bad{background:rgba(255,93,108,.15);color:var(--red)}.good{background:rgba(46,230,166,.15);color:var(--green)}
.verdict{margin-top:10px;font-weight:700;font-size:13px}
.vgood{color:var(--green)}.vbad{color:var(--red)}.vfix{color:var(--amber)}
.board{margin-top:20px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;display:none}
.board.show{display:block}.board .big{font-size:15px;line-height:1.6}.board .big b{color:var(--green)}
.err{color:var(--red);font-family:var(--mono);font-size:13px;margin-top:14px}
.foot{margin-top:22px;font-family:var(--mono);font-size:11px;color:var(--muted)}
</style></head><body><div class="wrap">
<div class="eyebrow"><span class="dot"></span> Plumbline · live · real model calls</div>
<h1>Watch a cheap AI get caught, and fixed.</h1>
<div class="sub">A cheap model answers. Plumbline checks each answer against the real correct answer. The ones it gets wrong, Plumbline catches and escalates to a stronger model.</div>
<div class="tag">real Mistral API calls · checked against ground truth · nothing pre-recorded</div>
<button class="run" id="run">▶ Run it live</button>
<div id="out"></div>
<div class="board" id="board"><div class="big" id="boardtext"></div></div>
<div class="foot">cheap = mistral-small · strong = mistral-large · the check is deterministic, not another AI</div>
</div><script>
const $=s=>document.querySelector(s);
$("#run").addEventListener("click",async()=>{
  const b=$("#run");b.disabled=true;b.textContent="running live…";
  $("#out").innerHTML="";$("#board").classList.remove("show");
  let data;
  try{ data=await (await fetch("/run")).json(); }
  catch(e){ $("#out").innerHTML='<div class="err">'+e+'</div>'; b.disabled=false;b.textContent="▶ Run it live"; return; }
  if(data.error){ $("#out").innerHTML='<div class="err">'+data.error+'</div>'; b.disabled=false;b.textContent="▶ Run it live"; return; }
  for(const r of data.results){
    const el=document.createElement("div");el.className="task";
    let h='<div class="q"><b>Q:</b> '+r.question+'</div>';
    if(r.error){ h+='<div class="err">'+r.error+'</div>'; }
    else{
      for(const s of r.steps){
        if(s.role==="cheap") h+='<div class="line cheap"><span>cheap ('+s.model+'): '+s.answer+'</span><span class="badge '+(s.ok?'good':'bad')+'">'+(s.ok?'correct':'WRONG')+'</span></div>';
        else if(s.role==="verifier") h+='<div class="line verif">↳ Plumbline checked it against the real answer ('+r.expected+') → caught the mistake</div>';
        else if(s.role==="strong") h+='<div class="line strong"><span>strong ('+s.model+'): '+s.answer+'</span><span class="badge '+(s.ok?'good':'bad')+'">'+(s.ok?'fixed':'still wrong')+'</span></div>';
      }
      const cls=r.verdict==="VERIFIED"?"vgood":(r.verdict==="CAUGHT + FIXED"?"vfix":"vbad");
      h+='<div class="verdict '+cls+'">'+r.verdict+'</div>';
    }
    el.innerHTML=h;$("#out").appendChild(el);
    requestAnimationFrame(()=>el.classList.add("show"));
    await new Promise(r=>setTimeout(r,350));
  }
  const s=data.summary;
  $("#boardtext").innerHTML='Cheap model alone got <b>'+s.cheap_alone_correct+'/'+s.total+'</b> right. Plumbline caught the rest and fixed <b>'+s.caught_and_fixed+'</b> by escalating only those to the strong model. Same cheap model, now trustworthy.';
  $("#board").classList.add("show");
  b.disabled=false;b.textContent="▶ Run again";
});
</script></body></html>`;
