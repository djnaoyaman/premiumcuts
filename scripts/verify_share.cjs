const test=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs'),path=require('node:path');
const {mountSharePanel}=require('../src/share-page.js');
const SHARE_PAGES={index:{title:'Premium Cuts Listed — World Wide Music.',url:'https://djnaoyaman.github.io/premiumcuts/'},track:{title:'Un été & vous — Artist',url:'https://djnaoyaman.github.io/premiumcuts/tracks/001-a-01.html'}};
function fixture(nav={},page='index') {
 const elements = Object.fromEntries(['native','copy','status','manual','url','actions'].map(key=>[key,{textContent:'',disabled:true,open:false,value:'',attrs:{},events:{},setAttribute(k,v){this.attrs[k]=v;},addEventListener(k,f){this.events[k]=f;},removeEventListener(k){delete this.events[k];},focus(){this.focused=true;},select(){this.selected=true;}}]));
 const lifecycle={events:{},addEventListener(k,f){this.events[k]=f;},removeEventListener(k){delete this.events[k];}};
 const root={dataset:{shareTitle:SHARE_PAGES[page]?.title,shareUrl:SHARE_PAGES[page]?.url},querySelector(selector){return elements[selector.match(/data-share-(.+)\]/)[1]];}};
 const api=mountSharePanel(root,{nav,lifecycle});return {elements,lifecycle,api,click:kind=>elements[kind].events.click()};
}
for (const [page,expected] of Object.entries(SHARE_PAGES)) test(`fixed clean URL and title for ${page}`,async()=>{
 const shares=[],copies=[];const f=fixture({share:async data=>shares.push(data),clipboard:{writeText:async value=>copies.push(value)}},page);
 await f.click('native');await f.click('copy');assert.deepEqual(shares,[expected]);assert.deepEqual(copies,[expected.url]);assert.equal(new URL(expected.url).search,'');assert.equal(new URL(expected.url).hash,'');
 assert.equal(f.elements.status.textContent,'URLをコピーしました。');assert.equal(f.elements.actions.attrs['aria-busy'],'false');

});
test('repeat clicks cannot duplicate a pending operation; settled action resets',async()=>{
 let resolve,calls=0,copies=0;const f=fixture({share:()=>{calls++;return new Promise(r=>resolve=r);},clipboard:{writeText:async()=>copies++}});
 const pending=f.click('native');await f.click('native');await f.click('copy');assert.equal(calls,1);assert.equal(copies,0);assert.equal(f.elements.native.attrs['aria-disabled'],'true');resolve();await pending;assert.equal(f.elements.native.attrs['aria-disabled'],'false');await f.click('copy');assert.equal(copies,1);
});
test('AbortError is cancellation, never copy or success; retry remains possible',async()=>{
 let calls=0,copies=0;const f=fixture({share:async()=>{calls++;throw Object.assign(new Error(),{name:'AbortError'});},clipboard:{writeText:async()=>copies++}});
 await f.click('native');assert.equal(f.elements.status.textContent,'共有をキャンセルしました。');assert.equal(f.elements.manual.open,false);assert.equal(copies,0);await f.click('native');assert.equal(calls,2);assert.equal(f.elements.actions.attrs['aria-busy'],'false');
});
for(const mode of ['missing','reject','throw'])test(`share ${mode} offers manual URL without clipboard writes`,async()=>{
 let copies=0;const nav={clipboard:{writeText:async()=>copies++}};if(mode!=='missing')nav.share=()=>{if(mode==='throw')throw new Error();return Promise.reject(new Error());};const f=fixture(nav);await f.click('native');assert.equal(copies,0);assert.equal(f.elements.manual.open,true);assert.equal(f.elements.url.focused,true);assert.equal(f.elements.url.selected,true);assert.equal(f.elements.copy.attrs['aria-disabled'],'false');assert.doesNotMatch(f.elements.status.textContent,/完了|コピーしました/);
});
for(const mode of ['missing','reject','throw','getter'])test(`clipboard ${mode} is honest manual fallback`,async()=>{
 const nav={};if(mode==='getter')Object.defineProperty(nav,'clipboard',{get(){throw new Error();}});else if(mode!=='missing')nav.clipboard={writeText:()=>{if(mode==='throw')throw new Error();return Promise.reject(new Error());}};const f=fixture(nav);await f.click('copy');assert.equal(f.elements.manual.open,true);assert.equal(f.elements.url.value,SHARE_PAGES.index.url);assert.equal(f.elements.actions.attrs['aria-busy'],'false');assert.doesNotMatch(f.elements.status.textContent,/コピーしました/);
});
test('pagehide resets pending UI; stale completion cannot overwrite a new action',async()=>{
 let resolve;const f=fixture({share:()=>new Promise(r=>resolve=r),clipboard:{writeText:async()=>{}}});const pending=f.click('native');f.lifecycle.events.pagehide();assert.equal(f.elements.actions.attrs['aria-busy'],'false');await f.click('copy');resolve();await pending;assert.equal(f.elements.status.textContent,'URLをコピーしました。');f.api.destroy();assert.equal(f.lifecycle.events.pagehide,undefined);
});
test('unknown page refuses mounting; module cannot consult private source data',()=>{
 assert.equal(fixture({},'unknown').api,null);assert.equal(fixture({},'__proto__').api,null);const source=readFileSync(path.join(__dirname,'../src/share-page.js'),'utf8');assert.doesNotMatch(source,/\b(?:localStorage|sessionStorage|fetch|XMLHttpRequest)\b/);assert.doesNotMatch(source,/location\s*\./);assert.doesNotMatch(source,/execCommand/);
});

for(const url of ['javascript:alert(1)','http://example.test/','https://name:secret@example.test/','https://example.test/?private=1','https://example.test/#playing','not-a-url'])test(`invalid public canonical is rejected: ${url}`,()=>{SHARE_PAGES.invalid={title:'Public page',url};assert.equal(fixture({},'invalid').api,null);});
