/* Run before the unchanged Google tag. Do not include query/hash in GA page fields. */
(()=>{'use strict';if(window.PremiumAnalyticsPrivacy)return;
 window.dataLayer=window.dataLayer||[];
 window.gtag=window.gtag||function(){window.dataLayer.push(arguments)};
 function clean(value){try{const u=new URL(value,location.href);return /^https?:$/.test(u.protocol)?u.origin+u.pathname:''}catch(_){return ''}}
 // Empty referrer must remain empty, not resolve to the current document.
 const initialReferrer=document.referrer?clean(document.referrer):'';
 function setLocation(url){window.gtag('set',{page_location:clean(url||location.href),page_referrer:initialReferrer})}
 setLocation();
 for(const method of ['pushState','replaceState']){const original=history[method];history[method]=function(state,title,url){setLocation(url==null?location.href:new URL(url,location.href).href);return original.apply(this,arguments)}}
 window.addEventListener('popstate',()=>setLocation());
 window.PremiumAnalyticsPrivacy={clean};
})();
