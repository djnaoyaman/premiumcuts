const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync('src/home-intro.js','utf8');
function setup({path='/premiumcuts/',hash='',reduced=false,seen=false,navigation='navigate',scroll=0,storageFails=false}={}){
 const events={},docEvents={},mediaEvents={},frames=new Map(),calls=[],main={};let id=0,now=0;
 const target=(map)=>({addEventListener(e,f){(map[e]??=new Set()).add(f)},removeEventListener(e,f){map[e]?.delete(f)}});
 const motion={...target(mediaEvents),matches:reduced};
 const doc={...target(docEvents),visibilityState:'visible',getElementById:()=>main,documentElement:{scrollHeight:6000},body:{scrollHeight:6000},fonts:{ready:Promise.resolve()}};
 const c={...target(events),document:doc,location:{pathname:path,hash},innerHeight:800,scrollY:scroll,
  performance:{getEntriesByType:()=>[{type:navigation}],now:()=>now},matchMedia:()=>motion,
  sessionStorage:{getItem(){if(storageFails)throw Error();return seen},setItem(){if(storageFails)throw Error();seen=true}},
  setTimeout:()=>1,clearTimeout(){},requestAnimationFrame(f){frames.set(++id,f);return id},cancelAnimationFrame(i){frames.delete(i)},
  scrollTo(o){calls.push(o);c.scrollY=o.top}};
 c.window=c;vm.runInNewContext(source,c);
 return {c,events,docEvents,motion,calls,frames,async settle(){await Promise.resolve();await Promise.resolve();await Promise.resolve()},frame(t){now=t;const fs=[...frames.values()];frames.clear();for(const f of fs)f(t)},emit(e){for(const f of [...(events[e]||[])])f({})}};
}
(async()=>{
 let t=setup();await t.settle();t.frame(0);t.frame(16);assert.equal(t.calls[0].top,5200);t.frame(1266);assert.equal(t.calls.at(-1).top,3900);t.frame(2516);assert.equal(t.calls.at(-1).top,0);assert.equal(t.frames.size,0);assert.equal(t.events.wheel.size,0);
 const count=t.calls.length;t.c.initPremiumHomeIntro();await t.settle();assert.equal(t.calls.length,count);
 for(const config of [{path:'/premiumcuts/tracks.html'},{path:'/premiumcuts/about.html'},{path:'/premiumcuts/tracks/001-a-01.html'},{hash:'#collection'},{reduced:true},{seen:true},{navigation:'back_forward'},{navigation:'reload'},{storageFails:true}]){t=setup(config);await t.settle();assert.equal(t.frames.size,0,JSON.stringify(config));assert.equal(t.calls.length,0)}
 for(const event of ['wheel','touchstart','pointerdown','keydown','popstate','pagehide']){t=setup();await t.settle();t.frame(0);t.frame(16);t.frame(100);const before=t.calls.length;t.emit(event);t.frame(2516);assert.equal(t.calls.length,before,event);assert.equal(t.frames.size,0)}
 t=setup();t.emit('touchstart');await t.settle();assert.equal(t.calls.length,0);assert.equal(t.frames.size,0);
 t=setup({scroll:900});await t.settle();t.frame(0);t.frame(16);assert.equal(t.calls.length,0);
 t=setup();t.c.initPremiumHomeIntro({fromHistory:true});await t.settle();assert.equal(t.calls.length,0);assert.equal(t.frames.size,0);
 // A fresh internal entry into home can run; Back/Forward cannot.
 t=setup({path:'/premiumcuts/about.html'});t.c.location.pathname='/premiumcuts/';t.c.initPremiumHomeIntro();await t.settle();t.frame(0);t.frame(16);assert.equal(t.calls[0].top,5200);
 t=setup({path:'/premiumcuts/about.html'});t.c.location.pathname='/premiumcuts/';t.c.initPremiumHomeIntro({fromHistory:true});await t.settle();assert.equal(t.frames.size,0);
 console.log('PASS homepage-only2500ms accelerating sweep, once/session, anchor/history/reload/reduced-motion skips, input cancellation, no scroll lock or focus changes');
})();
