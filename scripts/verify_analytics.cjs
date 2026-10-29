const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const calls=[],listeners={},timers=new Map();let serial=0;
const ctx={URL,Set,console,TRACKS:[{id:'001-a-01'}],PREMIUM_MYSPIN:[{id:'spin-1'}],location:{href:'https://djnaoyaman.github.io/premiumcuts/?q=PRIVATE#SECRET',origin:'https://djnaoyaman.github.io'},document:{referrer:'https://example.org/path?q=PRIVATE#SECRET',addEventListener(t,f){(listeners[t]??=[]).push(f)},getElementById:()=>({children:[1,2]})},history:{pushState(){calls.push(['history'])},replaceState(){calls.push(['history'])}},setTimeout(f){timers.set(++serial,f);return serial},clearTimeout(id){timers.delete(id)},window:{gtag(...a){calls.push(a)},addEventListener(t,f){listeners[t]=[f]},PremiumPlayer:{getState:()=>({current:'001-a-01'})}}};
vm.createContext(ctx);const run=f=>vm.runInContext(fs.readFileSync('src/'+f,'utf8'),ctx);
run('analytics-privacy.js');assert.equal(calls.at(-1)[1].page_location,'https://djnaoyaman.github.io/premiumcuts/');assert.equal(calls.at(-1)[1].page_referrer,'https://example.org/path');ctx.history.replaceState({},'', '/premiumcuts/tracks/a.html?q=PRIVATE#SECRET');assert.equal(calls.at(-2)[1].page_location,'https://djnaoyaman.github.io/premiumcuts/tracks/a.html');assert.equal(calls.at(-1)[0],'history');run('analytics-privacy.js');ctx.location.href='https://djnaoyaman.github.io/premiumcuts/player.html?q=PRIVATE#SECRET';listeners.popstate[0]();assert.equal(calls.at(-1)[1].page_location,'https://djnaoyaman.github.io/premiumcuts/player.html');assert.equal(listeners.popstate.length,1);
run('analytics.js');run('analytics.js');assert.equal(listeners.click.length,1);assert.equal(listeners.input.length,1);
const api=ctx.window.PremiumAnalytics;calls.length=0;api.reset('001-a-01');api.intent('toggle','001-a-01');assert.equal(calls.length,1);assert.equal(calls[0][1],'pc_player_intent');api.state('paused','001-a-01');api.state('completed','001-a-01');assert.equal(calls.length,1);
for(const state of ['playing','playing','paused','paused','completed','playing','completed','completed'])api.state(state,'001-a-01');
assert.deepEqual(calls.filter(x=>x[1]==='pc_playback_state').map(x=>x[2].state),['playing','paused','playing','completed']);
const count=calls.length;api.state('playing','PRIVATE');api.intent('PRIVATE','PRIVATE');assert.equal(calls.length,count);
function click(p){const t={dataset:{},hasAttribute:()=>false,...p};listeners.click[0]({target:{closest:()=>t}})}
click({id:'pc-next'});click({dataset:{playId:'001-a-01'}});click({tagName:'A',href:'https://djnaoyaman.github.io/cratediggin/?q=PRIVATE'});assert.equal(calls.at(-1)[2].destination,'cratediggin');
const input={id:'search',value:'PRIVATE',isConnected:true};listeners.input[0]({target:input});listeners.input[0]({target:input});assert.equal(timers.size,1);for(const f of timers.values())f();timers.clear();assert.equal(calls.at(-1)[2].result_count,2);assert.equal(calls.at(-1)[2].query_present,true);listeners.input[0]({target:{id:'series-filter',value:'PRIVATE'}});assert.equal(calls.at(-1)[2].filter_type,'series-filter');assert.ok(!JSON.stringify(calls).includes('PRIVATE'));
assert.ok(calls.every(c=>!['page_view','click','view_search_results','video_start','video_complete','video_progress'].includes(c[1])));
// Exercise the real YouTube callback with the established offline player harness.
let harness=fs.readFileSync('scripts/verify_player.cjs','utf8');
harness=harness.replace("ctx.window.scrollTo=()=>{};", "ctx.window.scrollTo=()=>{};ctx.TRACKS=catalog.tracks;ctx.window.gtag=(...a)=>{if(a[0]==='event')analyticsCalls.push(a)};");
harness=harness.replace("const fs=require", "const analyticsCalls=[];const fs=require");
harness=harness.replace("vm.createContext(ctx);", "vm.createContext(ctx);vm.runInContext(fs.readFileSync('src/analytics.js','utf8'),ctx);");
harness=harness.replace("console.log('PASS recording catalog;", "assert.ok(analyticsCalls.some(a=>a[1]==='pc_playback_state'&&a[2].state==='playing'));assert.ok(analyticsCalls.some(a=>a[1]==='pc_playback_state'&&a[2].state==='completed'));console.log('PASS recording catalog;");
vm.runInNewContext(harness,{require,console,URL,Map,Set,setTimeout,clearTimeout});
console.log('PASS analytics exact state/intent separation, dedup, delegated SPA listeners, query-free event fields, privacy history ordering, real player hooks');
