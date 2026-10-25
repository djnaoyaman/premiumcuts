const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class Node{constructor(){this.dataset={};this.hidden=false;this.checked=true;this.value=0;this.children=[];this.style={};this.attrs={};this.classList={toggle(){}}}setAttribute(k,v){this.attrs[k]=v}removeAttribute(k){delete this.attrs[k]}querySelector(){return new Node()}querySelectorAll(){return []}addEventListener(){}append(...n){this.children.push(...n)}replaceChildren(){this.children=[]}focus(){}getClientRects(){return [1]}}
const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id)},body=new Node();
const doc={currentScript:{src:'https://example.test/premiumcuts/player.js'},getElementById:get,querySelector:()=>new Node(),querySelectorAll:()=>[],createElement:()=>new Node(),addEventListener(){},head:new Node(),body,activeElement:null};
const catalog=JSON.parse(fs.readFileSync('catalog.json')),research=JSON.parse(fs.readFileSync('research.json')),sources={...research.players};for(const a of research.articles)if(a.youtube)for(const id of a.ids)sources[id]=a.youtube;
const audio=catalog.tracks.filter(t=>sources[t.id]).map(t=>({...t,videoId:sources[t.id].id,url:sources[t.id].url}));let events,videoId='',calls=[];
function Player(id,opts){events=opts.events;Object.assign(this,{loadVideoById(id){videoId=id;calls.push(['load',id])},cueVideoById(id){videoId=id;calls.push(['cue',id])},getVideoData:()=>({video_id:videoId}),pauseVideo(){calls.push(['pause'])},playVideo(){calls.push(['play'])},stopVideo(){calls.push(['stop'])},seekTo(n){calls.push(['seek',n])},getDuration:()=>180,getCurrentTime:()=>0})}
const ctx={document:doc,PREMIUM_AUDIO:audio,URL,Map,Set,console,location:{origin:'https://example.test',pathname:'/premiumcuts/player.html'},window:{YT:{Player}},YT:{Player},localStorage:{getItem:()=>null,setItem(){}},setTimeout:()=>1,clearTimeout(){},setInterval(){},addEventListener(){},history:{}};ctx.window.scrollTo=()=>{};vm.createContext(ctx);vm.runInContext(fs.readFileSync('src/player.js','utf8'),ctx);const api=ctx.window.PremiumPlayer;
assert.equal(api.getState().queue.length,24,'all recordings deduplicated across appearances');assert.equal(audio.find(t=>t.id==='cd-00-d1-21').videoId,'JNbxvLowZD8');assert.equal(audio.find(t=>t.id==='006-b-08').videoId,'xHVpXZHupHA');
assert.equal(audio.find(t=>t.id==='005-a-15').videoId,'MF13kdqG6jA');assert.equal(audio.find(t=>t.id==='cd-00-d2-11').videoId,'MF13kdqG6jA');
get('pc-toggle').onclick();api.stop();events.onReady();assert.equal(calls.at(-1)[0],'cue','stop before API ready cancels pending playback');
api.play('003-a-04','volume:003');assert.equal(api.getState().queue.join(','),'003-a-03,003-a-04,003-a-12,003-b-01,003-b-02,003-b-07,003-b-11');assert.equal(calls.at(-1)[1],'o1w5FMjoQ9Y');
events.onStateChange({data:1});assert.equal(api.getState().playing,true);events.onStateChange({data:0});assert.equal(api.getState().current,'003-a-12','ended advances within selected mix');
events.onStateChange({data:1});get('pc-toggle').onclick();events.onStateChange({data:2});assert.equal(api.getState().wantsPlay,false);events.onStateChange({data:0});assert.equal(api.getState().current,'003-a-12','paused recording does not advance');
api.play('003-b-11','volume:003');events.onStateChange({data:1});events.onStateChange({data:0});assert.equal(api.getState().current,'003-b-11','queue ends without looping');assert.equal(api.getState().playing,false);
api.play('007-b-11','volume:007');events.onError({data:101});assert.equal(api.getState().wantsPlay,false);assert.match(get('pc-status').textContent,/YouTube/);assert.equal(api.getState().current,'007-b-11','specified unavailable video is preserved');
api.play('004-b-07','volume:004');assert.equal(api.getState().queue.join(','),'004-a-01,004-a-02,004-b-07');get('pc-seek').value=30;get('pc-seek').oninput();assert.equal(calls.at(-1).join(','),'seek,30');
console.log('PASS 24 recordings; mix queues, deduplication, pending-stop, play/pause, auto advance, end-of-queue, errors, seeking.');
(async()=>{
 // A tab already playing must acquire a newly published source without recreating YouTube.
 await api.refresh(true); // Finish the initial offline check in this isolated harness.
 api.play('004-b-07','volume:004');events.onStateChange({data:1});
 const before=api.getState(),callsBefore=calls.length;
 const added={...catalog.tracks.find(t=>t.id==='004-a-03'),videoId:'abcdefghijk',url:'https://youtu.be/abcdefghijk'};
 const updated=audio.map(t=>({...t,...(t.id==='004-b-07'?{videoId:'zyxwvutsrqp',url:'https://youtu.be/zyxwvutsrqp'}:{})}));updated.push(added);
 ctx.fetch=async url=>({ok:true,json:async()=>url.includes('version.json')?{version:'fixture-v2'}:{version:'fixture-v2',tracks:catalog.tracks,volumes:catalog.volumes,audio:updated}});
 assert.equal(await api.refresh(true),true);
 assert.equal(api.getState().current,before.current);assert.equal(api.getState().playing,true);assert.equal(calls.length,callsBefore,'refresh does not reload or pause the active recording');
 assert.equal(api.getState().queue.slice(0,before.queue.length).join(','),before.queue.join(','),'existing relative play order preserved');assert.ok(api.getState().queue.includes(added.id),'new source appears in selected mix');
 events.onStateChange({data:1});assert.equal(api.getState().playing,true,'active-source identity survives source metadata updates');
 api.play(added.id,'volume:004');assert.equal(calls.at(-1)[1],'abcdefghijk','new source can be selected without a page reload');
 const lastQueue=api.getState().queue.join(',');ctx.fetch=async()=>{throw Error('offline')};assert.equal(await api.refresh(true),false);assert.equal(api.getState().queue.join(','),lastQueue,'offline checks preserve the existing catalog');
 ctx.fetch=async url=>({ok:true,json:async()=>url.includes('version.json')?{version:'bad-v3'}:{version:'bad-v3',tracks:catalog.tracks,volumes:catalog.volumes,audio:[{id:'bad',videoId:'invalid',title:'Bad',artist:'Bad'}]}});
 assert.equal(await api.refresh(true),false);assert.equal(api.getState().queue.join(','),lastQueue,'invalid data cannot erase a working queue');
 console.log('PASS stale-tab catalog refresh, active recording continuity, new source selection, offline and invalid-data recovery.');
})().catch(e=>{console.error(e);process.exitCode=1});
