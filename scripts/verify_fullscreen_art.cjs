const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class Node{constructor(){this.children=[];this.listeners={};this.dataset={};this.style={setProperty:(k,v)=>this.style[k]=v,getPropertyValue:k=>this.style[k]};this.value=0;this.max=180;this.textContent=''}addEventListener(k,f){(this.listeners[k]??=[]).push(f)}dispatchEvent(e){e.target=this;for(const f of this.listeners[e.type]||[])f(e)}click(){this.dispatchEvent({type:'click',detail:0})}append(n){this.children.push(n)}replaceChildren(){this.children=[]}setAttribute(k,v){this[k]=v}getContext(){return{font:'',measureText(s){return{width:Array.from(s).length*parseFloat(this.font)*.65}}}}};
const nodes=new Map(),get=id=>nodes.get(id)||nodes.set(id,new Node()).get(id);let frame,end,state={current:null,currentTrack:null,playing:false,full:true,artState:'idle'};
const ctx={console,MouseEvent:class{constructor(type,opts){Object.assign(this,{type},opts)}},document:{addEventListener:(k,f)=>get('document').addEventListener(k,f),getElementById:get,createElement:()=>new Node(),createElementNS:()=>new Node()},window:{PremiumPlayer:{getState:()=>state},matchMedia:()=>({matches:false})},MutationObserver:class{observe(){}},requestAnimationFrame(f){frame=f},setInterval(){},setTimeout(f){end=f;return 1},clearTimeout(){end=null}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync('dist/data.js','utf8')+';this.items=[...PREMIUM_AUDIO,...PREMIUM_MYSPIN];this.meta=PREMIUM_ART',ctx);vm.runInContext(fs.readFileSync('src/fullscreen-art.js','utf8'),ctx);const sync=ctx.window.PremiumFullscreenArt.sync;
assert.equal(Object.keys(ctx.meta).length,ctx.items.length);for(const item of ctx.items){state.current=item.id;state.currentTrack=item;sync();assert(get('label-copy').children.some(n=>n.textContent==='制作年・制作国：未確認'));assert(get('label-copy').children.every(n=>Number(n['font-size'])>=3));}
state.current='reference:001-a-11';state.currentTrack={id:state.current,title:'Different rendition',artist:'Different performer'};sync();assert(get('label-copy').children.some(n=>n.textContent.includes('発売 未確認')));
state.artState='playing';state.playing=true;get('pc-seek').value=90;sync();assert.equal(get('pc-player').dataset.needle,'down');frame(100);frame(200);const spin=get('disc-spin').transform;state.artState='paused';state.playing=false;sync();frame(300);assert.equal(get('disc-spin').transform,spin);assert.equal(get('pc-player').dataset.needle,'down');state.artState='stopped';sync();assert.equal(get('pc-player').dataset.needle,'up');
state.artState='ended';sync();for(let i=4;i<20;i++)frame(i*100);assert(get('tonearm').transform.includes('23.18996342096852'));end();assert.equal(get('pc-player').dataset.needle,'up');sync();assert.equal(get('pc-player').dataset.needle,'up');
for(let i=0;i<=100;i++){const a=Math.min(1,i/100/.98)*23.18996342096852*Math.PI/180,vx=790-37*Math.sin(48*Math.PI/180)-850,vy=385+37*Math.cos(48*Math.PI/180)-70,r=Math.hypot(350+vx*Math.cos(a)-vy*Math.sin(a),-211+vx*Math.sin(a)+vy*Math.cos(a));assert(r>=95/204*325-1e-8);assert(r>87/204*325)}
const source=fs.readFileSync('src/fullscreen-art.js','utf8');for(const forbidden of ['ART_DEMO','art-track','audio-mode','reopen','new YT.Player'])assert(!source.includes(forbidden));console.log('PASS all '+ctx.items.length+' playable labels, reference unknowns, rotation/pause/stop/end and approved stylus geometry; no demo controls');

// Circular SVG hit target delegates once; never implements a second transport.
const hit=get('pc-art-toggle'),panel=get('pc-player');let toggles=0;
get('pc-toggle').addEventListener('click',()=>toggles++);
function event(type,extra={}){return {type,preventDefault(){},isPrimary:true,button:0,pointerId:1,clientX:100,clientY:100,detail:1,...extra}}
function fire(type,extra){hit.dispatchEvent(event(type,extra))}
panel.dataset.mode='art';state.full=true;state.wantsPlay=true;sync();
assert.equal(hit.tabindex,'0');assert.equal(hit['aria-label'],'レコードを一時停止');
fire('pointerdown');fire('click');assert.equal(toggles,1);
fire('pointerdown');get('document').dispatchEvent(event('pointermove',{clientX:140}));fire('click');assert.equal(toggles,1,'drag out and back must not toggle');
fire('pointerdown');get('document').dispatchEvent(event('pointercancel'));fire('click');assert.equal(toggles,1);
fire('pointerdown');get('document').dispatchEvent(event('scroll'));fire('click');assert.equal(toggles,1,'scroll cancels tap');
fire('pointerdown');get('document').dispatchEvent(event('pointerdown',{pointerId:2}));fire('click');assert.equal(toggles,1,'multitouch cancels');
fire('pointerdown',{button:2});fire('click');assert.equal(toggles,1,'right button is not a tap');
fire('keydown',{key:'Enter'});fire('keydown',{key:'Enter',repeat:true});assert.equal(toggles,2);
fire('keydown',{key:' '});assert.equal(toggles,2);fire('keyup',{key:' '});assert.equal(toggles,3);
fire('keyup',{key:' '});assert.equal(toggles,3);
fire('keydown',{key:' '});fire('blur');fire('keyup',{key:' '});assert.equal(toggles,3);
fire('click',{detail:0});assert.equal(toggles,4,'assistive activation uses the same route');
for(const mode of ['video','hybrid']){panel.dataset.mode=mode;sync();fire('click',{detail:0});assert.equal(hit.tabindex,'-1');assert.equal(toggles,4)}
panel.dataset.mode='art';state.full=false;sync();fire('click',{detail:0});assert.equal(toggles,4);
state.full=true;state.playing=false;state.wantsPlay=false;sync();assert.equal(hit['aria-label'],'レコードを再生');
vm.runInContext(source,ctx);fire('click',{detail:0});assert.equal(toggles,5,'initialization is idempotent');
const shell=fs.readFileSync('src/player-shell.html','utf8'),css=fs.readFileSync('src/fullscreen-art.css','utf8');
assert(shell.includes('id="pc-art-toggle" r="202"'));assert(shell.indexOf('id="pc-art-toggle"')<shell.indexOf('id="arm-map"'),'needle stays above hit region');
assert(!shell.includes('class="pc-art" aria-hidden="true"'));
assert(css.includes('overflow:visible;border-radius:0'),'WebKit arm clip fix remains');
console.log('PASS disc tap delegation, drag/scroll/cancel/multitouch guards, keyboard, accessible state, mode isolation and idempotence');
