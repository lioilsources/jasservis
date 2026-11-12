(function () {
 'use strict';
 var root=document.querySelector('.advice-index');if(!root)return;
 var script=document.currentScript, routeSource=script.getAttribute('data-routes');
 var brands=['volkswagen','audi','skoda','seat','cupra','volkswagen-uzitkove-vozy'];
 var buttons=Array.from(root.querySelectorAll('[data-index-brand]'));
 var links=Array.from(root.querySelectorAll('[data-advice-link]'));
 function selected(){var value=new URLSearchParams(location.search).get('znacka');return brands.indexOf(value)>=0?value:'';}
 function render(){var brand=selected();buttons.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.indexBrand===brand));});links.forEach(function(a){var url=new URL(a.href),path=a.getAttribute('href').split(/[?#]/)[0],warning=path.match(/\/kontrolky-([^/]+)\//),context=warning?warning[1]:brand;if(warning)a.parentElement.hidden=!!(brand&&warning[1]!==brand);if(context)url.searchParams.set('znacka',context);else url.searchParams.delete('znacka');a.setAttribute('href',path+url.search+url.hash);});document.querySelectorAll('.language-switcher a').forEach(function(a){var path=a.getAttribute('href').split(/[?#]/)[0];a.href=path+(brand?'?znacka='+brand:'');});}
 buttons.forEach(function(b){b.addEventListener('click',function(){var url=new URL(location.href);if(selected()===b.dataset.indexBrand)url.searchParams.delete('znacka');else url.searchParams.set('znacka',b.dataset.indexBrand);history.pushState(null,'',url.pathname+url.search+url.hash);render();});});
 window.addEventListener('popstate',render);render();
 var params=new URLSearchParams(location.search),key=params.get('kapitola'),hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch(e){}
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
