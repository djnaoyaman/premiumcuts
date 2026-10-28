const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('src/back-to-top.js','utf8');
function setup(path='/premiumcuts/tracks.html', reduced=false){
 const events={},docs={},frames=[],top={dataset:{scrollEdge:'top'},closest(){return this}},bottom={dataset:{scrollEdge:'bottom'},closest(){return this}},input={setAttribute(k,v){this[k]=v}},output={};
 const nav={hidden:true,contains:n=>[top,bottom,input].includes(n),querySelector:s=>s==='input'?input:s==='output'?output:s.includes('="top"')?top:bottom};
 const focus={setAttribute(){},focus(o){this.focused=o},addEventListener(){}};
 const c={location:{pathname:path},scrollY:0,innerHeight:800,document:{documentElement:{scrollHeight:10800},getElementById:()=>nav,querySelector:()=>focus,addEventListener:(k,f)=>docs[k]=f},addEventListener:(k,f)=>events[k]=f,requestAnimationFrame:f=>frames.push(f),matchMedia:()=>({matches:reduced}),scrollTo:o=>c.scroll=o};c.window=c;vm.runInNewContext(source,c);
 return {c,nav,top,bottom,input,output,focus,events,docs,flush(){while(frames.length)frames.shift()()}};
}
let t=setup();assert(!t.nav.hidden);assert(t.top.disabled);assert.equal(t.output.textContent,'0%');
t.c.scrollY=5000;t.events.scroll();t.flush();assert.equal(t.input.value,50);assert.equal(t.output.textContent,'50%');
t.docs.click({target:t.bottom,preventDefault(){}});assert.equal(t.c.scroll.top,10000);assert.equal(t.c.scroll.behavior,'smooth');
t.input.value=25;t.docs.input({target:t.input});assert.equal(t.c.scroll.top,2500);assert.equal(t.c.scroll.behavior,'instant');
t.c.scrollY=10000;t.events.scroll();t.flush();assert(t.bottom.disabled);assert.equal(t.output.textContent,'100%');
t.docs.click({target:t.top,preventDefault(){}});assert.equal(t.c.scroll.top,0);assert(t.focus.focused.preventScroll);
t.c.document.documentElement.scrollHeight=800;t.events.resize();t.flush();assert(t.nav.hidden);assert.equal(t.output.textContent,'0%');
t=setup('/premiumcuts/tracks.html',true);t.docs.click({target:t.bottom,preventDefault(){}});assert.equal(t.c.scroll.behavior,'instant');
for(const path of ['/premiumcuts/','/premiumcuts/about.html','/premiumcuts/tracks/001-a-01.html']){t=setup(path);assert(t.nav.hidden);t.docs.click({target:t.bottom,preventDefault(){throw Error('wrong scope')}});assert(!t.c.scroll)}
t=setup('/premiumcuts/');t.c.location.pathname='/premiumcuts/tracks.html';t.events.pageshow();t.flush();assert(!t.nav.hidden);
for(const p of fs.readdirSync('dist').filter(x=>x.endsWith('.html')))assert.equal(fs.readFileSync('dist/'+p,'utf8').includes('id="songs-scroll-nav"'),p==='tracks.html',p);
console.log('PASS Songs-only top/bottom/percentage, precise seeking, extent changes, reduced motion and SPA scope');
