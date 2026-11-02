'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),vm=require('vm');
const proposed=require('../src/share-page.js');
const player=fs.readFileSync(path.join(__dirname,'../src/player.js'),'utf8');
const start=player.indexOf('async function navigate('),end=player.indexOf('// Reading an Essentials liner',start);
const navigateSource=player.slice(start,end).trim();
assert.equal((navigateSource.match(/window\.PremiumShare\?\.syncFromDocument\(doc\);/g)||[]).length,1,'Actual shipped navigate() must contain exactly one share hook');
const HOME={title:'Premium Cuts Listed',url:'https://djnaoyaman.github.io/premiumcuts/'};
const TRACK={title:'A & B — Artist | Premium Cuts Listed',url:'https://djnaoyaman.github.io/premiumcuts/tracks/001-a-01.html'};
function root(page){
 const nodes=Object.fromEntries(['native','copy','status','manual','url','actions'].map(k=>[k,{disabled:true,attrs:{},events:{},open:false,value:'',textContent:'',setAttribute(k,v){this.attrs[k]=v},addEventListener(k,f){this.events[k]=f},removeEventListener(k){delete this.events[k]},focus(){this.focused=true},select(){this.selected=true}}]));
 return {dataset:{shareTitle:page.title,shareUrl:page.url},nodes,removed:false,querySelector(s){return nodes[s.match(/data-share-(.+)\]/)[1]]},cloneNode(){return root(page)},remove(){this.removed=true}};
}
function doc(initial){
 const state={panels:initial?[initial]:[],title:HOME.title,main:{replaceWith(next){state.main=next}},head:{querySelectorAll(){return []},append(){}}};
 const footer={append(x){state.panels.push(x)}};
 Object.assign(state,{querySelectorAll(s){return s==='[data-page-share]'?state.panels.filter(x=>!x.removed):[]},querySelector(s){if(s==='main')return state.main;if(s==='footer')return footer;if(s==='[data-page-share]')return state.querySelectorAll(s)[0]||null;return null}});return state;
}
function source(page){const d=doc(page?root(page):null);d.title=page?.title||'Not found';return d;}
function life(){const handlers=new Set();return {addEventListener(k,f){handlers.add(f)},removeEventListener(k,f){handlers.delete(f)},reset(){for(const f of handlers)f()},count:()=>handlers.size}}
async function navigate(d,destination,manager){
 const ctx={navigation:0,refreshCatalog:async()=>{},catalogVersion:'mock',URL,fetch:async()=>({ok:true,text:async()=>''}),DOMParser:class{parseFromString(){return destination}},document:d,history:{pushState(){}},initPage(){},window:{PremiumShare:manager,scrollTo(){}},location:{assign(){throw Error('Unexpected full navigation fallback')}}};
 const code=navigateSource;
 vm.runInNewContext(code+';globalThis.run=navigate',ctx);await ctx.run(new URL(TRACK.url));
}
test('shipped hook refreshes actual navigation payload and preserves old footer',async()=>{
 const first=root(HOME),d=doc(first),calls=[],l=life(),footer=d.querySelector('footer');const m=proposed.createShareManager({doc:d,nav:{share:async x=>calls.push(x)},lifecycle:l});await navigate(d,source(TRACK),m);const next=d.querySelector('[data-page-share]');assert.notEqual(first,next);assert.equal(first.removed,true);assert.equal(first.nodes.native.events.click,undefined);assert.equal(d.querySelector('footer'),footer);assert.equal(l.count(),1);await next.nodes.native.events.click();assert.deepEqual(calls,[TRACK]);
});
for(const outcome of ['resolve','reject'])test(`SPA commit invalidates pending old ${outcome}`,async()=>{
 let settle;const calls=[],l=life(),first=root(HOME),d=doc(first);const nav={share:()=>new Promise((r,j)=>settle=outcome==='resolve'?r:j),clipboard:{writeText:async x=>calls.push(x)}};const m=proposed.createShareManager({doc:d,nav,lifecycle:l});const pending=first.nodes.native.events.click();await navigate(d,source(TRACK),m);const next=d.querySelector('[data-page-share]');await next.nodes.copy.events.click();settle(Error());await pending;assert.equal(next.nodes.status.textContent,'URLをコピーしました。');assert.equal(next.nodes.manual.open,false);assert.deepEqual(calls,[TRACK.url]);assert.equal(first.nodes.status.textContent,'');
});
test('successive pages, Back-style sync and repeated hook keep one live handler',async()=>{
 const l=life(),d=doc(root(HOME)),copies=[],m=proposed.createShareManager({doc:d,nav:{clipboard:{writeText:async x=>copies.push(x)}},lifecycle:l});for(const page of [TRACK,HOME,HOME,TRACK]){m.syncFromDocument(source(page));assert.equal(l.count(),1);assert.equal(d.querySelectorAll('[data-page-share]').length,1);await d.querySelector('[data-page-share]').nodes.copy.events.click()};assert.deepEqual(copies,[TRACK.url,HOME.url,HOME.url,TRACK.url]);m.destroy();assert.equal(l.count(),0);
});
test('404 without a panel removes old URL; next valid page works',async()=>{
 const d=doc(root(HOME)),m=proposed.createShareManager({doc:d,nav:{},lifecycle:life()});m.syncFromDocument(source(null));assert.equal(d.querySelector('[data-page-share]'),null);m.syncFromDocument(source(TRACK));assert.equal(d.querySelector('[data-page-share]').nodes.url.value,TRACK.url);
});
test('invalid new canonical cannot retain stale old page or mount invalid controls',()=>{
 const d=doc(root(HOME)),l=life(),m=proposed.createShareManager({doc:d,nav:{},lifecycle:l});m.syncFromDocument(source({...TRACK,url:TRACK.url+'?state=secret'}));assert.equal(d.querySelector('[data-page-share]'),null);assert.equal(l.count(),0);
});
test('existing button behavior stays pagehide-safe after footer remount',async()=>{
 const d=doc(root(HOME)),l=life(),m=proposed.createShareManager({doc:d,nav:{},lifecycle:l});m.syncFromDocument(source(TRACK));const r=d.querySelector('[data-page-share]');await r.nodes.copy.events.click();assert.equal(r.nodes.manual.open,true);l.reset();assert.equal(r.nodes.manual.open,false);assert.equal(r.nodes.status.textContent,'');
});
