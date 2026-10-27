const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class Node{constructor(){this.dataset={};this.hidden=false;this.checked=true;this.value=0;this.children=[];this.style={};this.attrs={};this.classList={toggle(){}}}setAttribute(k,v){this.attrs[k]=v}removeAttribute(k){delete this.attrs[k]}querySelector(){return new Node()}querySelectorAll(){return []}addEventListener(){}append(...n){this.children.push(...n)}replaceChildren(){this.children=[]}focus(){}getClientRects(){return [1]}}
function harness(path='/premiumcuts/tracks.html',random=0){
let randomCalls=0;const handlers={},winhandlers={};
const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id)},body=new Node();
const doc={currentScript:{src:'https://example.test/premiumcuts/player.js'},getElementById:get,querySelector:()=>new Node(),querySelectorAll:()=>[],createElement:()=>new Node(),addEventListener(k,f){handlers[k]=f},head:new Node(),body,activeElement:null};
const catalog=JSON.parse(fs.readFileSync('catalog.json')),research=JSON.parse(fs.readFileSync('research.json')),sources={...research.players};for(const a of research.articles)if(a.youtube)for(const id of a.ids)sources[id]=a.youtube;
Object.assign(sources,JSON.parse(fs.readFileSync('audio_sources.json')));
const audio=catalog.tracks.filter(t=>sources[t.id]).map(t=>({...t,videoId:sources[t.id].id,url:sources[t.id].url}));let events,videoId='',calls=[];
function Player(id,opts){events=opts.events;Object.assign(this,{loadVideoById(id){videoId=id;calls.push(['load',id])},cueVideoById(id){videoId=id;calls.push(['cue',id])},getVideoData:()=>({video_id:videoId}),pauseVideo(){calls.push(['pause'])},playVideo(){calls.push(['play'])},stopVideo(){calls.push(['stop'])},seekTo(n){calls.push(['seek',n])},getDuration:()=>180,getCurrentTime:()=>0})}
const ctx={Math:Object.assign(Object.create(Math),{random:()=>{randomCalls++;return random}}),document:doc,PREMIUM_AUDIO:audio,PREMIUM_MYSPIN:JSON.parse(fs.readFileSync('myspin.json')),PREMIUM_ESSENTIAL_IDS:JSON.parse(fs.readFileSync('features.json')).essentials.track_ids,URL,URLSearchParams,Map,Set,console,location:{origin:'https://example.test',pathname:path,search:''},window:{YT:{Player}},YT:{Player},localStorage:{getItem:()=>null,setItem(){}},setTimeout:()=>1,clearTimeout(){},setInterval(){},addEventListener(k,f){winhandlers[k]=f},history:{pushState(a,b,u){const x=new URL(u,ctx.location.origin);Object.assign(ctx.location,{pathname:x.pathname,search:x.search,href:x.href})}}};ctx.window.scrollTo=()=>{};vm.createContext(ctx);vm.runInContext(fs.readFileSync('src/player.js','utf8'),ctx);const api=ctx.window.PremiumPlayer;

return {api,get,ctx,calls,events:()=>events,randomCalls:()=>randomCalls,setRandom:value=>random=value,click:async(dataset)=>handlers.click({preventDefault(){},target:{closest:s=>s==='[data-play-id],[data-play-volume],[data-play-all]'?{dataset,hasAttribute:name=>name==='data-play-all'&&'playAll' in dataset}:null}})};
}
(async()=>{
 for(const random of [0,0.5,1-Number.EPSILON]){
  const h=harness(undefined,random),state=h.api.getState(),ids=Array.from(state.queue),index=Math.floor(random*ids.length);
  assert.equal(state.current,ids[index]);assert.equal(state.wantsPlay,false);assert.equal(h.randomCalls(),1,'one initial draw only');
  h.events().onReady();assert.equal(h.randomCalls(),1,'YouTube readiness does not redraw');
  h.get('pc-toggle').onclick();h.events().onStateChange({data:1});
  h.get('pc-next').onclick();assert.equal(h.api.getState().current,ids[(index+1)%ids.length]);
  h.get('pc-prev').onclick();assert.equal(h.api.getState().current,ids[index]);
  h.events().onStateChange({data:1});h.events().onStateChange({data:0});
  assert.equal(h.api.getState().current,ids[index===ids.length-1?index:index+1]);
  if(index===ids.length-1)assert.equal(h.api.getState().wantsPlay,false,'automatic end stops normally');
  assert.equal(h.randomCalls(),1);assert.deepEqual(Array.from(h.api.getState().queue),ids);
  const fresh=harness(undefined,random);assert.equal(fresh.randomCalls(),1,'reload draws once');
 }
 const h=harness(),ids=Array.from(h.api.getState().queue);h.events().onReady();
 await h.click({playId:ids[8],playScope:'all'});assert.equal(h.api.getState().current,ids[8]);assert.equal(h.randomCalls(),1,'manual choice wins');
 h.events().onStateChange({data:1});h.get('pc-toggle').onclick();h.get('pc-toggle').onclick();assert.equal(h.api.getState().current,ids[8]);assert.equal(h.randomCalls(),1,'resume does not redraw');
 h.events().onStateChange({data:1});const before=h.calls.length;
 h.ctx.location.pathname='/premiumcuts/features/essentials.html';h.api.syncPageScope();
 h.ctx.location.pathname='/premiumcuts/tracks.html';h.api.syncPageScope();
 assert.equal(h.calls.length,before,'active navigation does not restart audio');assert.equal(h.randomCalls(),1);
 h.api.stop();h.ctx.location.pathname='/premiumcuts/my-spin.html';h.api.syncPageScope();
 assert.equal(h.api.getState().current,JSON.parse(fs.readFileSync('myspin.json'))[0].id);
 h.setRandom(0.5);h.ctx.location.pathname='/premiumcuts/tracks.html';h.api.syncPageScope();
 assert.equal(h.api.getState().current,ids[Math.floor(ids.length*0.5)]);assert.equal(h.randomCalls(),2);assert.equal(h.api.getState().wantsPlay,false);
 h.api.syncPageScope();assert.equal(h.randomCalls(),2,'same context does not redraw');
 await h.click({playAll:''});assert.equal(h.randomCalls(),3);assert.equal(h.api.getState().current,ids[Math.floor(ids.length*0.5)]);assert.equal(h.api.getState().wantsPlay,true);
 h.api.stop();h.api.chooseScope('essentials');h.get('pc-scope').value='all';h.get('pc-scope').onchange();assert.equal(h.randomCalls(),4);assert.equal(h.api.getState().wantsPlay,false);
 for(const path of ['/premiumcuts/features/essentials.html','/premiumcuts/my-spin.html','/premiumcuts/tracks/'+ids[4]+'.html']){
  const x=harness(path,0.5);assert.equal(x.randomCalls(),0,'other collections and direct song do not randomize');assert.equal(x.api.getState().wantsPlay,false);
 }
 const direct=harness('/premiumcuts/tracks/'+ids[4]+'.html');assert.equal(direct.api.getState().current,ids[4]);
 assert.deepEqual(Array.from(h.api.getState().queue),ids,'Songs list stays fixed');
 console.log('PASS random starting point, endpoints, reload, explicit choice, resume, active/idle transitions, next/previous/end and collection isolation');
})().catch(e=>{console.error(e);process.exitCode=1});
