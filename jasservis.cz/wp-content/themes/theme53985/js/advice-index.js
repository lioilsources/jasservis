(function () {
 'use strict';
 var root=document.querySelector('.advice-index');if(!root)return;
 var script=document.currentScript, routeSource=script.getAttribute('data-routes');
 var brands=['volkswagen','audi','skoda','seat','cupra','volkswagen-uzitkove-vozy'];
 function selected(){var value=new URLSearchParams(location.search).get('znacka');return brands.indexOf(value)>=0?value:'';}
 var params=new URLSearchParams(location.search),key=params.get('kapitola'),hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch(e){}
 // Brand pages contain real, scoped links and remain usable without JavaScript.
 if(root.dataset.adviceBrand)return;
 var brandLink=root.querySelector('[data-index-brand="'+selected()+'"]');
 if(brandLink&&!key&&(!hash||hash==='odborne-rady')){location.replace(brandLink.href+(hash?'#'+hash:''));return;}
 // Normal overview links do not need the legacy routing map.
 if(!key&&(!hash||(document.getElementById(hash)&&hash.indexOf('rada-')!==0)))return;
 fetch(routeSource).then(function(r){if(!r.ok)throw Error('routes');return r.json();}).then(function(routes){
  var route=routes[hash]||routes[key];
  if(key==='jak-rozpoznat-zavadu'&&!hash&&params.has('podkapitola'))route=routes['rada-'+String(Number(params.get('podkapitola'))+1).padStart(2,'0')];
  if(!route)return;
  var url=new URL(route.path,location.href),brand=selected()||route.brand;
  if(brand)url.searchParams.set('znacka',brand);
  if(key==='kontrolky'&&brand)url.pathname=url.pathname.replace(/kontrolky-volkswagen\//,'kontrolky-'+brand+'/');
  if(hash&&hash.indexOf('rada-')!==0&&hash!=='jak-rozpoznat-zavadu'&&!url.hash)url.hash=hash;
  if(url.href!==location.href)location.replace(url.href);
 }).catch(function(){/* The complete list remains usable if routing data is unavailable. */});
}());
