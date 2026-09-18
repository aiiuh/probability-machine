'use strict';
const $ = id => document.getElementById(id);
let session = null, active = null, pending = false, lastInput = 'unknown';
const variants = ['top-standard','top-large','bottom-standard','bottom-large'];
const uuid = () => crypto.randomUUID();
const geometry = node => { const r=node.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height}; };
window.addEventListener('pointerdown', e => {lastInput=e.pointerType || 'pointer';});
window.addEventListener('keydown', () => {lastInput='keyboard';});
fetch('/sample.json').then(r=>r.json()).then(x=>{$('spec').value=JSON.stringify(x,null,2);}).catch(e=>{$('decision').textContent=e.message;});
$('solve').addEventListener('click', async () => {
  try {
    const response=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:$('spec').value});
    const result=await response.json();
    if(!response.ok) throw new Error(result.error || 'Evaluation failed');
    $('result').textContent=JSON.stringify(result,null,2);
    $('decision').textContent=result.recommended_next_step ? `Next: ${result.recommended_next_step.kind} → ${result.recommended_next_step.name}. No action executed.` : 'No feasible action under these limits.';
  } catch(e) {$('decision').textContent=e.message;}
});
function finish(success,reason) {
  if(pending){pending=false;$('targetGroup').hidden=true;$('start').disabled=false;$('trialStatus').textContent='Trial cancelled before recording began.';}
  if(!active) return;
  session.trials.push({...active,elapsed_ms:performance.now()-active.started_ms,success,reason});
  delete session.trials[session.trials.length-1].started_ms;
  active=null; $('targetGroup').hidden=true; $('start').disabled=session.trials.length>=12;
  $('trialStatus').textContent=`${session.trials.length}/12 trials recorded. ${session.trials.length>=12?'Complete; export the session.':'Ready for the next trial.'}`;
}
$('start').addEventListener('click',e=>{
  if(!$('consent').checked){$('trialStatus').textContent='Enable local recording before starting.';return;}
  if(active || pending || (session && session.trials.length>=12)) return;
  if(!session){
    const draw=crypto.getRandomValues(new Uint32Array(1))[0];
    const index=draw%4; // 2^32 is divisible by 4: unbiased four-arm assignment.
    session={schema_version:'layout-session-0.3',data_origin:'human_session_unverified',session_id:uuid(),created_at:new Date().toISOString(),
      assignment_unit:'session',assignment_method:'crypto_uniform_4_v1',variant:variants[index],assignment_probability:.25,
      logging_policy:Object.fromEntries(variants.map(v=>[v,.25])),trials:[]};
    $('consent').disabled=true;
  }
  const [placement,size]=session.variant.split('-');
  $('targetGroup').className=`${placement} ${size}`; $('targetGroup').hidden=false; $('arenaHint').hidden=true;
  $('start').disabled=true;
  pending=true;
  requestAnimationFrame(()=>{
    if(!session || !pending)return;
    pending=false;
    active={trial:session.trials.length+1,started_ms:performance.now(),errors:0,input_modality:lastInput,
      start_pointer:lastInput==='keyboard'?null:{x:e.clientX,y:e.clientY},viewport:{width:innerWidth,height:innerHeight},
      target:geometry($('target')),decoy:geometry($('decoy')),variant:session.variant};
    $('trialStatus').textContent=`Trial ${active.trial}/12 — choose Continue.`;
  });
});
$('decoy').addEventListener('click',()=>{if(active)active.errors++;});
$('target').addEventListener('click',()=>finish(true,'target_selected'));
$('stop').addEventListener('click',()=>finish(false,'participant_stopped'));
window.addEventListener('keydown',e=>{if(e.key==='Escape')finish(false,'escape');});
$('reset').addEventListener('click',()=>{active=null;pending=false;session=null;$('targetGroup').hidden=true;$('arenaHint').hidden=false;$('consent').disabled=false;$('consent').checked=false;$('start').disabled=false;$('trialStatus').textContent='Session discarded.';});
function snapshot(){
  if(!session) return null;
  return {...session,enjoyment_rating:$('enjoyment').value?Number($('enjoyment').value):null,
    active_trial_unfinished:!!active,notes:'Repeated trials are clustered within session. Randomization is not a complete causal-identification guarantee.'};
}
$('export').addEventListener('click',()=>{
  const data=snapshot();if(!data){$('trialStatus').textContent='No session to export.';return;}
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=`layout-session-${data.session_id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
// Read-only hook for browser verification. Automated sessions are NOT human evidence.
window.probabilityMachineSnapshot=snapshot;
