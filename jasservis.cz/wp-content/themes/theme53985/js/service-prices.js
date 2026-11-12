(function () {
 'use strict';
 var script=document.currentScript;
 if(!script)return;
 var previous;
 try{previous=JSON.parse(script.getAttribute('data-price-values')||'{}');}catch(e){return;}
 function format(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,'\u00a0');}
 function valid(n){return typeof n==='number'&&Number.isFinite(n)&&Number.isInteger(n)&&n>0;}
 var source=new URL('../price-values.json',script.src);
 fetch(source.href,{cache:'no-cache',credentials:'same-origin'}).then(function(r){if(!r.ok)throw Error('prices');return r.json();}).then(function(data){
  if(data.schemaVersion!==1||data.currency!=='CZK'||!data.values)throw Error('prices');
  var values=data.values,nodes=Array.from(document.querySelectorAll('[data-price]'));
  if(!Object.keys(previous).every(function(k){return valid(previous[k])&&valid(values[k]);})||!nodes.every(function(n){return valid(values[n.dataset.price]);}))throw Error('prices');
  var old={};Object.keys(previous).forEach(function(k){var n=previous[k];old[n]=old[n]===undefined?k:null;});
  function updateText(text){return text.replace(/\b\d+(?:[\s\u00a0.,]\d{3})*(?=[\s\u00a0]*(?:Kč|CZK)(?=\s|[.,;)"'<]|$))/g,function(m){var k=old[Number(m.replace(/[\s.,]/g,''))];return k?format(values[k]):m;});}
  function walk(value){if(typeof value==='string')return updateText(value);if(Array.isArray(value))return value.map(walk);if(value&&typeof value==='object'){var next={};Object.keys(value).forEach(function(k){next[k]=walk(value[k]);});return next;}return value;}
  var metas=Array.from(document.querySelectorAll('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]')).map(function(n){return [n,updateText(n.content)];});
  var json=Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(function(n){return [n,JSON.stringify(walk(JSON.parse(n.textContent)))];});
  nodes.forEach(function(n){n.textContent=format(values[n.dataset.price]);});
  metas.forEach(function(pair){pair[0].content=pair[1];});json.forEach(function(pair){pair[0].textContent=pair[1];});
  script.setAttribute('data-prices-loaded','true');
 }).catch(function(){/* The complete, pre-rendered price and its scope remain available. */});
}());
