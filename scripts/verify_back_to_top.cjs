const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('src/back-to-top.js', 'utf8');
function setup(path='/premiumcuts/tracks.html', reduced=false) {
  const events={}, docEvents={}, frames=[];
  const button={hidden:true,contains:node=>node===button};
  const heading={setAttribute(k,v){this[k]=v},removeAttribute(k){delete this[k]},focus(o){this.focused=o},addEventListener(e,fn){this[e]=fn}};
  const c={location:{pathname:path},scrollY:0,innerHeight:800,
    document:{getElementById:()=>button,querySelector:()=>heading,addEventListener:(k,v)=>docEvents[k]=v},
    addEventListener:(k,v)=>events[k]=v,requestAnimationFrame:f=>frames.push(f),
    matchMedia:()=>({matches:reduced}),scrollTo:o=>c.scroll=o};
  c.window=c;vm.runInNewContext(source,c);
  return {c,button,heading,events,docEvents,flush(){while(frames.length)frames.shift()()}};
}
let t=setup();assert(t.button.hidden);
t.c.scrollY=1000;t.events.scroll();t.flush();assert(!t.button.hidden);
let prevented=false;t.docEvents.click({target:t.button,preventDefault(){prevented=true}});
assert(prevented);assert.equal(t.c.scroll.top,0);assert.equal(t.c.scroll.behavior,'smooth');
assert.equal(t.heading.tabindex,'-1');assert(t.heading.focused.preventScroll);t.heading.blur();assert(!('tabindex' in t.heading));
t.c.scrollY=0;t.events.scroll();t.flush();assert(t.button.hidden);
t=setup('/premiumcuts/tracks.html',true);t.docEvents.click({target:t.button,preventDefault(){}});assert.equal(t.c.scroll.behavior,'instant');
for(const path of ['/premiumcuts/','/premiumcuts/index.html','/premiumcuts/about.html','/premiumcuts/tracks/001-a-01.html']){
 t=setup(path);t.c.scrollY=1200;t.events.scroll();t.flush();assert(t.button.hidden);t.docEvents.click({target:t.button,preventDefault(){throw Error('Other page intercepted')}});assert(!t.c.scroll);
}
// Delegated listeners also work after SPA entry / replacement of main.
t=setup('/premiumcuts/');t.c.location.pathname='/premiumcuts/tracks.html';t.c.scrollY=1500;t.events.scroll();t.flush();assert(!t.button.hidden);
t.c.location.pathname='/premiumcuts/about.html';t.docEvents.click({target:t.button,preventDefault(){throw Error('Stale control')}});assert(!t.c.scroll);
const pages=fs.readdirSync('dist').filter(p=>p.endsWith('.html'));
for(const p of pages){const html=fs.readFileSync('dist/'+p,'utf8');assert.equal(html.includes('id="songs-back-to-top"'),p==='tracks.html',p)}
for(const p of fs.readdirSync('dist/tracks'))assert(!fs.readFileSync('dist/tracks/'+p,'utf8').includes('id="songs-back-to-top"'));
assert.match(fs.readFileSync('src/style.css','utf8'),/safe-area-inset-top/);
console.log('PASS Songs-only top control, scroll threshold, click/keyboard focus, reduced motion, SPA replacement and other-page isolation');
