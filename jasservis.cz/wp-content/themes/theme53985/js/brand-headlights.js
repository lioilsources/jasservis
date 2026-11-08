/* Repeating viewport queue. Original photographs, links and lamp shapes stay intact. */
(function () {
 'use strict';
 var grid=document.querySelector('#portfolio-grid');
 if(!grid||!window.IntersectionObserver||!window.ResizeObserver)return;
 var motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 var shapes={
  'servis-volkswagen-s.jpg':['M348 75L378 80L380 96L353 94Z'],
  'servis-audi-s.jpg':['M157 219L183 225L181 240L162 236Z M216 231L242 232L238 244L219 243Z','M474 221L484 217L488 235L480 239Z'],
  'servis-seat-s.jpg':['M312 139L337 146L330 159L319 156Z M358 150L381 155L374 162L354 160Z'],
  'servis-cupra-s.jpg':['M272 151L291 150L296 162L279 164Z M333 142L351 139L350 154L336 158Z','M36 146L49 151L44 157L33 156Z'],
  'servis-volkswagen-uzitkove-vozy-s.jpg':['M421 182a10 8 0 1 0 20 0a10 8 0 1 0 -20 0 M457 176a10 9 0 1 0 20 0a10 9 0 1 0 -20 0']
 };
 var ns='http://www.w3.org/2000/svg',items=[],active=null,cursor=0,nextFrame=0,pagePaused=false;
 var photos=Array.prototype.slice.call(grid.querySelectorAll('figure img'));
 Array.prototype.forEach.call(document.querySelectorAll('[data-headlight-extra] img'),function(img){if(photos.indexOf(img)===-1)photos.push(img);});
 photos.forEach(function(img){
  var name=new URL(img.currentSrc||img.src,document.baseURI).pathname.split('/').pop();
  var isExtra=!!img.closest('[data-headlight-extra]')&&name==='cupra-js-servis-zvedak.jpg';
  if(!grid.contains(img)&&!isExtra)return;
  var paths=isExtra?['M192 392 L258 368 L365 349 L382 352 L351 378 L315 405 L214 415 Z']:shapes[name];
  if(!paths)return;
  var figure=img.closest('figure,[data-headlight-extra]');if(!figure)return;
  figure.classList.add('js-headlight-photo');
  var svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',isExtra?'0 0 1280 960':'0 0 600 380');svg.setAttribute('preserveAspectRatio','none');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.classList.add('js-headlight-overlay');
  paths.forEach(function(d){var path=document.createElementNS(ns,'path');path.setAttribute('d',d);svg.appendChild(path);});figure.appendChild(svg);
  function fit(){var a=img.getBoundingClientRect(),b=figure.getBoundingClientRect();svg.style.left=(a.left-b.left-figure.clientLeft)+'px';svg.style.top=(a.top-b.top-figure.clientTop)+'px';svg.style.width=a.width+'px';svg.style.height=a.height+'px';}
  var resize=new ResizeObserver(fit);resize.observe(img);img.addEventListener('load',fit);fit();
  items.push({img:img,svg:svg,visible:false,finish:null});
 });
 function allowed(){return !pagePaused&&!document.hidden&&!motion.matches;}
 function cancelNext(){if(nextFrame){window.cancelAnimationFrame(nextFrame);nextFrame=0;}}
 function stopActive(){
  if(!active)return;
  var item=active;active=null;
  item.svg.removeEventListener('animationend',item.finish);item.svg.removeEventListener('animationcancel',item.finish);
  item.finish=null;item.svg.classList.remove('is-lit');
 }
 function scheduleNext(){
  if(nextFrame||active||!allowed())return;
  // Two frames leave a painted dark state, even if only one photo is visible.
  nextFrame=window.requestAnimationFrame(function(){
   nextFrame=window.requestAnimationFrame(function(){nextFrame=0;next();});
  });
 }
 function next(){
  if(active||!allowed())return;
  for(var offset=0;offset<items.length;offset++){
   var index=(cursor+offset)%items.length,item=items[index];
   if(!item.visible||!item.img.complete||!item.img.naturalWidth)continue;
   cursor=(index+1)%items.length;active=item;
   item.finish=function(event){
    if(event.target!==item.svg||event.animationName!=='js-headlight-pulse'||active!==item)return;
    stopActive();scheduleNext();
   };
   item.svg.addEventListener('animationend',item.finish);item.svg.addEventListener('animationcancel',item.finish);
   item.svg.classList.add('is-lit');return;
  }
 }
 function sync(){
  if(!allowed()){cancelNext();stopActive();return;}
  if(active&&!active.visible)stopActive();
  scheduleNext();
 }
 var cards=new IntersectionObserver(function(entries){
  items.forEach(function(item){var entry=entries.find(function(e){return e.target===item.img;});if(entry)item.visible=entry.isIntersecting&&entry.intersectionRatio>=.3;});sync();
 },{threshold:.3});
 items.forEach(function(item){cards.observe(item.img);item.img.addEventListener('load',sync);});
 if(motion.addEventListener)motion.addEventListener('change',sync);else motion.addListener(sync);
 document.addEventListener('visibilitychange',sync);
 window.addEventListener('pagehide',function(){pagePaused=true;sync();});
 window.addEventListener('pageshow',function(){pagePaused=false;sync();});
}());
