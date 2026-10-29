/* Operational events only. GA's automatic page_view/click/search/video events are not re-emitted. */
(()=>{'use strict';if(window.PremiumAnalytics)return;
 const ids=()=>new Set([...(typeof TRACKS!=='undefined'?TRACKS:[]),...(typeof PREMIUM_MYSPIN!=='undefined'?PREMIUM_MYSPIN:[])].map(t=>t.id));
 const publicId=id=>ids().has(id)?id:typeof id==='string'&&id.startsWith('reference:')&&ids().has(id.slice(10))?id.slice(10):null;
 function send(name,params){if(typeof window.gtag==='function')window.gtag('event',name,params)}
 const allowedIntent=new Set(['toggle','stop','next','previous','song_select','queue_select','play_all','play_volume','reference_select']);
 function intent(action,id){if(!allowedIntent.has(action))return;const song=publicId(id);send('pc_player_intent',{action,...(song?{song_id:song}:{})})}
 let lastState=null,started=false,active=null;
 function reset(id){active=publicId(id);lastState=null;started=false}
 function state(value,id){const song=publicId(id);if(!song||song!==active||!['playing','paused','completed'].includes(value))return;if(value!=='playing'&&!started)return;if(value===lastState||value==='completed'&&lastState!=='playing')return;lastState=value;if(value==='playing')started=true;send('pc_playback_state',{state:value,song_id:song});if(value==='completed')started=false}
 const controls={'pc-toggle':'toggle','pc-stop':'stop','pc-next':'next','pc-prev':'previous'};
 function current(){return window.PremiumPlayer?.getState?.().current}
 function click(e){const t=e.target.closest?.('button,a,input');if(!t)return;
  if(controls[t.id]){intent(controls[t.id],current());return}
  if(t.dataset?.queueId){intent('queue_select',t.dataset.queueId);return}
  if(t.dataset?.playId){intent('song_select',t.dataset.playId);return}
  if(t.hasAttribute?.('data-play-all')){intent('play_all');return}
  if(t.dataset?.playVolume){intent('play_volume');return}
  if(t.dataset?.referenceTrack){intent('reference_select',t.dataset.referenceTrack);return}
  if(t.tagName==='A'&&t.href){let u;try{u=new URL(t.href,location.href)}catch(_){return}if(!['http:','https:'].includes(u.protocol))return;
   let destination=null;if(u.hostname==='www.youtube.com'||u.hostname==='youtube.com'||u.hostname==='youtu.be')destination='youtube';else if(u.hostname==='djnaoyaman.github.io'&&u.pathname.startsWith('/cratediggin/'))destination='cratediggin';else if(u.hostname==='djnaoyaman.github.io'&&u.pathname.startsWith('/suburbia-classica/'))destination='suburbia_classica';else if(u.origin!==location.origin)destination='other_external';
   if(destination)send('pc_destination_open',{destination});
  }
 }
 let searchTimer=null;
 const filters=new Set(['feature-filter','series-filter','volume-filter','side-filter','sort']);
 function resultCount(){const n=document.getElementById('catalog-list')?.children?.length;return Number.isInteger(n)?Math.min(n,10000):0}
 function input(e){const t=e.target;if(t.id==='search'){clearTimeout(searchTimer);searchTimer=setTimeout(()=>{if(t.isConnected!==false)send('pc_catalog_search',{query_present:!!t.value.trim(),result_count:resultCount()})},500)}else if(filters.has(t.id)){send('pc_catalog_filter',{filter_type:t.id,result_count:resultCount()})}}
 window.PremiumAnalytics={intent,reset,state};document.addEventListener('click',click,true);document.addEventListener('input',input);
})();
