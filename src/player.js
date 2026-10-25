/* Shared listening room. Reference behavior: CRATE DIGGIN' and suburbia CLASSICA.
   Keep one YouTube instance and the selected queue alive while browsing. */
(()=>{'use strict';
 const scriptURL=new URL(document.currentScript.src),base=new URL('.',scriptURL).pathname;
 let catalogVersion=scriptURL.searchParams.get('v')||'',catalogRequest=null,lastCatalogCheck=0,activeVideoId=null;
 const tracks=PREMIUM_AUDIO, byId=new Map(tracks.map(t=>[t.id,t]));
 const $=id=>document.getElementById(id),panel=$('pc-player');if(!panel)return;
 const title=$('pc-title'),artist=$('pc-artist'),status=$('pc-status'),toggle=$('pc-toggle'),seek=$('pc-seek');
 const unique=list=>{const seen=new Set();return list.filter(t=>!seen.has(t.videoId)&&seen.add(t.videoId)).map(t=>t.id)};
 let queue=unique(tracks),scope='all',current=null,yt=null,ready=false,loading=null,wantsPlay=false,playing=false,reachedPlaying=false,full=false,fullFocus=null,previousExpanded='true',mode='hybrid',watchdog=null,loadSerial=0,navigation=0;
 const time=n=>Math.floor(Math.max(0,n)/60)+':'+String(Math.floor(Math.max(0,n)%60)).padStart(2,'0');
 function setStatus(s){status.textContent=s}
 function expanded(value){panel.dataset.expanded=String(value);$('pc-fold').setAttribute('aria-expanded',String(value));$('pc-fold').setAttribute('aria-label',value?'プレーヤーを小さく表示':'プレーヤーを展開');$('pc-fold').textContent=value?'−':'＋'}
 function paint(state){playing=state;panel.dataset.playing=String(state);toggle.textContent=state?'Ⅱ':'▶';toggle.setAttribute('aria-label',state?'一時停止':'再生');toggle.title=state?'一時停止':'再生'}
 function clearWatch(){clearTimeout(watchdog);watchdog=null}
 function watch(){clearWatch();const serial=loadSerial;watchdog=setTimeout(()=>{if(serial!==loadSerial||!wantsPlay||playing)return;wantsPlay=false;yt?.pauseVideo?.();paint(false);setStatus('再生ボタンをもう一度押すか、YouTubeで開いてください。')},18000)}
 function matches(){const id=yt?.getVideoData?.()?.video_id;return !id||id===activeVideoId}
 function queueFor(value){return unique(value.startsWith('volume:')?tracks.filter(t=>t.volume===value.slice(7)):tracks)}
 function chooseScope(value){scope=value;queue=queueFor(value);renderQueue()}
 function load(id,play=false){const t=byId.get(id);if(!t)return;clearWatch();loadSerial++;reachedPlaying=false;current=id;activeVideoId=t.videoId;wantsPlay=play;paint(false);title.textContent=t.title;artist.textContent=t.artist;
  const a=$('pc-song-link');a.hidden=false;a.textContent='曲の解説を読む ↗';a.href=base+'tracks/'+id+'.html';const link=$('pc-youtube');link.hidden=false;link.href=t.url;
  $('pc-elapsed').textContent='0:00';$('pc-duration').textContent='—';seek.value=0;seek.max=100;loading={id,play};
  if(ready){loading=null;if(play){setStatus('音源を読み込んでいます。');watch();yt.loadVideoById(t.videoId)}else{yt.cueVideoById(t.videoId);setStatus('再生ボタンで聴けます。')}}else setStatus('YouTubeの準備をしています。');
  renderQueue();document.querySelectorAll('[data-play-id]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.playId===id)));
 }
 function playId(id,value){if(!byId.has(id))return;if(value)chooseScope(value);if(!queue.includes(id)){scope='all';queue=unique(tracks);if(!queue.includes(id)){queue.unshift(id)}}expanded(true);load(id,true)}
 function advance(delta,automatic=false){if(!queue.length)return;const i=queue.indexOf(current);if(automatic&&i===queue.length-1){wantsPlay=false;reachedPlaying=false;paint(false);setStatus('この曲順の再生が終わりました。');return}const next=queue[(i<0?(delta>0?0:queue.length-1):(i+delta+queue.length)%queue.length)];load(next,automatic||wantsPlay||playing)}
 function playPause(){if(!current){const first=queue[0];if(first)load(first,true);return}if(wantsPlay||playing){wantsPlay=false;if(loading)loading.play=false;clearWatch();yt?.pauseVideo?.();paint(false);setStatus('一時停止中');return}wantsPlay=true;if(!ready){loading={id:current,play:true};setStatus('準備ができ次第、選んだ曲を再生します。');return}if(!matches()){load(current,true);return}setStatus('音源を読み込んでいます。');watch();yt.playVideo()}
 function stop(){wantsPlay=false;reachedPlaying=false;if(loading)loading.play=false;loadSerial++;clearWatch();yt?.stopVideo?.();paint(false);seek.value=0;$('pc-elapsed').textContent='0:00';setStatus('停止しました。')}
 function startAPI(){if(window.YT?.Player){createYT();return}window.onYouTubeIframeAPIReady=createYT;const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.onerror=()=>setStatus('YouTubeへのリンクからも聴けます。');document.head.append(script)}
 function createYT(){if(yt)return;yt=new YT.Player('pc-yt',{host:'https://www.youtube-nocookie.com',width:'100%',height:'100%',playerVars:{playsinline:1,rel:0,origin:location.origin},events:{
  onReady(){ready=true;const pending=loading;loading=null;if(pending)load(pending.id,pending.play);else setStatus('曲を選んで、再生ボタンを押してください。')},
  onStateChange(e){if(!current||!matches())return;if(e.data===1){wantsPlay=true;clearWatch();reachedPlaying=true;paint(true);setStatus('再生中')}else if(e.data===2){clearWatch();wantsPlay=false;paint(false);setStatus('一時停止中')}else if(e.data===0){const advanceNext=reachedPlaying&&wantsPlay&&$('pc-auto').checked;clearWatch();reachedPlaying=false;wantsPlay=false;paint(false);if(advanceNext)advance(1,true);else setStatus('再生が終わりました。')}else if(e.data===3){setStatus('音源を読み込んでいます。')}},
  onAutoplayBlocked(){wantsPlay=false;clearWatch();paint(false);setStatus('この端末では再生ボタンをもう一度押してください。')},
  onError(e){wantsPlay=false;reachedPlaying=false;clearWatch();paint(false);const messages={100:'この動画は現在利用できません。',101:'この動画はサイト内再生に対応していません。',150:'この動画はサイト内再生に対応していません。',153:'この環境ではYouTubeで直接お聴きください。'};setStatus((messages[e.data]||'この環境では動画を読み込めませんでした。')+' YouTubeで開くか、次の曲を選べます。')}
 }})}
 function setFull(open){if(full===open)return;full=open;panel.classList.toggle('pc-fullscreen',full);panel.dataset.mode=mode;panel.querySelector('.pc-full-tools').hidden=!full;
  for(const node of [document.querySelector('body>header'),document.querySelector('main'),document.querySelector('footer')])if(node)node.inert=full;
  if(full){previousExpanded=panel.dataset.expanded;panel.dataset.expanded='true';fullFocus=document.activeElement;panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');document.body.style.overflow='hidden';$('pc-close-full').focus()}else{panel.dataset.expanded=previousExpanded;panel.removeAttribute('role');panel.removeAttribute('aria-modal');document.body.style.overflow='';if(fullFocus?.isConnected)fullFocus.focus()}}
 $('pc-toggle').onclick=playPause;$('pc-stop').onclick=stop;$('pc-prev').onclick=()=>advance(-1);$('pc-next').onclick=()=>advance(1);$('pc-full').onclick=()=>setFull(true);$('pc-close-full').onclick=()=>setFull(false);
 $('pc-fold').onclick=()=>{const expanded=panel.dataset.expanded!=='true';panel.dataset.expanded=String(expanded);$('pc-fold').setAttribute('aria-expanded',String(expanded));$('pc-fold').setAttribute('aria-label',expanded?'プレーヤーを小さく表示':'プレーヤーを展開');$('pc-fold').textContent=expanded?'−':'＋'};
 seek.oninput=()=>{if(ready&&current)yt.seekTo(Number(seek.value),true)};
 $('pc-auto').onchange=()=>{try{localStorage.setItem('premiumcuts-auto',String($('pc-auto').checked))}catch(_){}};
 try{const auto=localStorage.getItem('premiumcuts-auto');if(auto!==null)$('pc-auto').checked=auto==='true'}catch(_){}
 panel.querySelectorAll('[data-pc-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.pcMode;panel.dataset.mode=mode;panel.querySelectorAll('[data-pc-mode]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)))});
 panel.addEventListener('keydown',e=>{if(!full)return;if(e.key==='Escape'){e.preventDefault();setFull(false)}if(e.key==='Tab'){const focusable=[...panel.querySelectorAll('a[href],button,input,iframe')].filter(n=>!n.hidden&&n.getClientRects().length);const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}});
 setInterval(()=>{if(!ready||!current||!matches())return;const d=yt.getDuration?.()||0,t=yt.getCurrentTime?.()||0;$('pc-elapsed').textContent=time(t);$('pc-duration').textContent=d?time(d):'—';seek.max=d||100;if(document.activeElement!==seek)seek.value=t},750);
 function catalogMessage(text){const n=$('pc-catalog-status');if(n)n.textContent=text}
 async function refreshCatalog(force=false){
  if(catalogRequest)return catalogRequest;
  if(!force&&Date.now()-lastCatalogCheck<15000)return false;
  lastCatalogCheck=Date.now();
  catalogRequest=(async()=>{
   const manifestResponse=await fetch(base+'version.json?check='+Date.now(),{cache:'no-store'});
   if(!manifestResponse.ok)throw Error('version');const manifest=await manifestResponse.json();
   if(!manifest.version||manifest.version===catalogVersion){catalogMessage(unique(tracks).length+'音源を掲載中');return false}
   const response=await fetch(base+'catalog-public.json?v='+encodeURIComponent(manifest.version),{cache:'no-store'});
   if(!response.ok)throw Error('catalog');const data=await response.json();
   if(data.version!==manifest.version||!Array.isArray(data.audio)||!Array.isArray(data.tracks)||!Array.isArray(data.volumes))throw Error('catalog format');
   if(!data.audio.every(t=>t&&typeof t.id==='string'&&/^[a-zA-Z0-9_-]{11}$/.test(t.videoId)&&typeof t.title==='string'&&typeof t.artist==='string'))throw Error('audio format');
   // Retain the active recording and the existing play order; append newly available cuts.
   const oldOrder=queue.slice();tracks.splice(0,tracks.length,...data.audio);byId.clear();tracks.forEach(t=>byId.set(t.id,t));
   if(typeof TRACKS!=='undefined')TRACKS.splice(0,TRACKS.length,...data.tracks);
   if(typeof VOLUMES!=='undefined')VOLUMES.splice(0,VOLUMES.length,...data.volumes);
   const available=queueFor(scope),availableSet=new Set(available),seenVideos=new Set();
   queue=oldOrder.filter(id=>availableSet.has(id));queue.forEach(id=>seenVideos.add(byId.get(id).videoId));
   for(const id of available)if(!seenVideos.has(byId.get(id).videoId)){queue.push(id);seenVideos.add(byId.get(id).videoId)}
   catalogVersion=data.version;renderQueue();window.refreshPremiumCatalog?.();catalogMessage(unique(tracks).length+'音源を掲載中');return true;
  })().catch(()=>{if(force)catalogMessage('更新を確認できませんでした。もう一度お試しください。');return false}).finally(()=>{catalogRequest=null});
  return catalogRequest;
 }
 function renderQueue(){const list=$('pc-queue-list');if(!list)return;list.replaceChildren();queue.forEach((id,i)=>{const t=byId.get(id),li=document.createElement('li'),b=document.createElement('button');b.type='button';b.dataset.queueId=id;b.className=id===current?'is-current':'';b.setAttribute('aria-pressed',String(id===current));const num=document.createElement('span');num.textContent=String(i+1).padStart(2,'0');const copy=document.createElement('span'),strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=t.title;small.textContent=t.artist;copy.append(strong,small);b.append(num,copy);b.onclick=()=>load(id,true);const a=document.createElement('a');a.href=base+'tracks/'+id+'.html';a.textContent='解説 ↗';a.setAttribute('aria-label',t.title+'の解説');li.append(b,a);list.append(li)});const count=$('pc-queue-count');if(count)count.textContent=queue.length+'曲 / 全'+unique(tracks).length+'音源';const s=$('pc-scope');if(s)s.value=scope}
 function initPage(){document.body.dataset.listeningPage=String(location.pathname.endsWith('/player.html'));if(document.body.dataset.listeningPage==='true')expanded(true);if(window.initPremiumCatalog)window.initPremiumCatalog();renderQueue();const s=$('pc-scope');if(s)s.onchange=()=>{chooseScope(s.value)};const all=$('pc-show-all');if(all)all.onclick=()=>chooseScope('all');const refresh=$('pc-refresh');if(refresh)refresh.onclick=async()=>{refresh.disabled=true;catalogMessage('曲を確認しています。');await refreshCatalog(true);refresh.disabled=false};document.querySelectorAll('[data-play-id]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.playId===current)))}
 async function navigate(url,push=true){const serial=++navigation;try{await refreshCatalog();const requestURL=new URL(url.href);requestURL.searchParams.set('_pcv',catalogVersion);const response=await fetch(requestURL.href,{cache:'no-store'});if(!response.ok)throw Error('page');const doc=new DOMParser().parseFromString(await response.text(),'text/html'),main=doc.querySelector('main');if(!main||serial!==navigation)return;document.querySelector('main').replaceWith(main);const header=doc.querySelector('body>header');if(header)document.querySelector('body>header').replaceWith(header);document.title=doc.title;
   for(const selector of ['meta[name="description"]','link[rel="canonical"]','meta[property^="og:"]','meta[name^="twitter:"]']){document.head.querySelectorAll(selector).forEach(n=>n.remove());doc.head.querySelectorAll(selector).forEach(n=>document.head.append(n.cloneNode(true)))}
   if(push)history.pushState(null,'',url.pathname+url.search+url.hash);initPage();if(url.hash)document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();else window.scrollTo(0,0);
  }catch(_){if(serial===navigation)location.assign(url.href)}}
 document.addEventListener('click',async e=>{const b=e.target.closest('[data-play-id],[data-play-volume],[data-play-all]');if(b){e.preventDefault();if(b.dataset.playId&&!byId.has(b.dataset.playId))await refreshCatalog(true);if(b.hasAttribute('data-play-all')){chooseScope('all');load(queue[0],true)}else if(b.dataset.playVolume){chooseScope('volume:'+b.dataset.playVolume);if(queue.length)load(queue[0],true);else setStatus('この作品の音源は順次追加しています。')}else playId(b.dataset.playId,b.dataset.playScope||'volume:'+byId.get(b.dataset.playId)?.volume);return}
  if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;const a=e.target.closest('a[href]');if(!a||a.target||a.hasAttribute('download'))return;const u=new URL(a.href,location.href);if(u.origin!==location.origin||!u.pathname.startsWith(base)||u.pathname===location.pathname&&u.search===location.search||!(u.pathname.endsWith('.html')||u.pathname===base))return;e.preventDefault();navigate(u)
 });
 $('pc-queue-open').onclick=()=>navigate(new URL(base+'player.html',location.origin));addEventListener('popstate',()=>navigate(new URL(location.href),false));
 window.PremiumPlayer={play:playId,stop,chooseScope,refresh:refreshCatalog,getState:()=>({queue:queue.slice(),scope,current,playing,wantsPlay,ready,full})};
 expanded(location.pathname.endsWith('/player.html'));initPage();const initial=location.pathname.match(/\/tracks\/([^/]+)\.html$/)?.[1];if(byId.has(initial)){chooseScope('volume:'+byId.get(initial).volume);load(initial,false)}else if(queue.length)load(queue[0],false);startAPI();refreshCatalog();setInterval(()=>refreshCatalog(),60000);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')refreshCatalog()});addEventListener('focus',()=>refreshCatalog());
})();
