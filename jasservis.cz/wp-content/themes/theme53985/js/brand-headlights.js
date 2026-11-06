/* Native viewport queue. No original photograph, link or text is changed. */
(function () {
 'use strict';
 var grid=document.querySelector('#portfolio-grid');
 if(!grid||!window.IntersectionObserver||!window.ResizeObserver)return;
 var motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 if(motion.matches)return;
 var shapes={
  'servis-volkswagen-s.jpg':['M348 75L378 80L380 96L353 94Z'],
  'servis-audi-s.jpg':['M157 219L183 225L181 240L162 236Z M216 231L242 232L238 244L219 243Z','M474 221L484 217L488 235L480 239Z'],
  'servis-seat-s.jpg':['M312 139L337 146L330 159L319 156Z M358 150L381 155L374 162L354 160Z'],
  'servis-cupra-s.jpg':['M272 151L291 150L296 162L279 164Z M333 142L351 139L350 154L336 158Z','M36 146L49 151L44 157L33 156Z'],
  'servis-volkswagen-uzitkove-vozy-s.jpg':['M421 182a10 8 0 1 0 20 0a10 8 0 1 0 -20 0 M457 176a10 9 0 1 0 20 0a10 9 0 1 0 -20 0']
 };
 var ns='http://www.w3.org/2000/svg',items=[],queue=[],running=false,stopped=false;
 Array.prototype.forEach.call(grid.querySelectorAll('figure img'),function(img){
  var paths=shapes[new URL(img.currentSrc||img.src,document.baseURI).pathname.split('/').pop()];
  if(!paths)return;
  var figure=img.closest('figure');if(!figure)return;
  figure.classList.add('js-headlight-photo');
  var svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 600 380');svg.setAttribute('preserveAspectRatio','none');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.classList.add('js-headlight-overlay');
  paths.forEach(function(d){var path=document.createElementNS(ns,'path');path.setAttribute('d',d);svg.appendChild(path);});figure.appendChild(svg);
  function fit(){var a=img.getBoundingClientRect(),b=figure.getBoundingClientRect();svg.style.left=(a.left-b.left-figure.clientLeft)+'px';svg.style.top=(a.top-b.top-figure.clientTop)+'px';svg.style.width=a.width+'px';svg.style.height=a.height+'px';}
  var resize=new ResizeObserver(fit);resize.observe(img);img.addEventListener('load',fit);fit();
  items.push({img:img,svg:svg,seen:false,resize:resize,visible:false});
 });
 function next(){
  if(running||stopped||!queue.length)return;
  var item=queue.shift();running=true;
  function finish(event){if(event&&event.animationName!=='js-headlight-pulse')return;item.svg.removeEventListener('animationend',finish);item.svg.removeEventListener('animationcancel',finish);item.svg.classList.remove('is-lit');running=false;next();}
  item.svg.addEventListener('animationend',finish);item.svg.addEventListener('animationcancel',finish);item.svg.classList.add('is-lit');
 }
 function ready(item){if(stopped||item.seen||!item.visible||!item.img.complete||!item.img.naturalWidth)return;item.seen=true;cards.unobserve(item.img);queue.push(item);next();}
 var cards=new IntersectionObserver(function(entries){
  items.forEach(function(item){var entry=entries.find(function(e){return e.target===item.img;});if(entry){item.visible=entry.isIntersecting&&entry.intersectionRatio>=.3;ready(item);}});next();
 },{threshold:.3});
 items.forEach(function(item){item.img.addEventListener('load',function(){ready(item);},{once:true});});
 var section=new IntersectionObserver(function(entries){if(entries.some(function(e){return e.isIntersecting;})){section.disconnect();items.forEach(function(item){cards.observe(item.img);});}},{threshold:0});section.observe(grid);
 function stop(){if(!motion.matches)return;stopped=true;queue=[];cards.disconnect();section.disconnect();items.forEach(function(item){item.svg.classList.remove('is-lit');item.resize.disconnect();});}
 if(motion.addEventListener)motion.addEventListener('change',stop);else motion.addListener(stop);
}());
