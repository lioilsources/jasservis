/* Repeating outline queue over the unchanged 600 x 380 diagnostics photograph. */
(function () {
 'use strict';
 if(!window.IntersectionObserver||!window.ResizeObserver||!window.matchMedia)return;
 var grid=document.querySelector('#portfolio-grid');
 if(!grid)return;
 var ns='http://www.w3.org/2000/svg',motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 var outlines=[
  'M40 25 Q37 25 37 29 L37 114 Q37 117 40 117 L203 130 Q206 130 206 127 L206 49 Q206 46 203 46 Z',
  'M244 34 Q241 34 241 37 L241 101 Q241 104 244 104 L339 113 Q342 113 342 110 L342 47 Q342 44 339 44 Z',
  'M434 29 Q431 29 431 32 L431 91 Q431 94 434 94 L552 86 Q555 86 555 83 L555 16 Q555 13 552 13 Z',
  'M522 103 Q519 103 519 106 L519 200 Q519 203 522 203 L599 205 L599 96 Z',
  'M522 227 Q519 227 519 230 L519 300 Q519 303 522 303 L599 315 L599 232 Z'
 ];
 var items=[],active=null,timer=0,cursor=0,pagePaused=false;
 Array.prototype.forEach.call(grid.querySelectorAll('img'),function(img){
  var name;
  try{name=new URL(img.currentSrc||img.getAttribute('src')||'',document.baseURI).pathname.split('/').pop();}catch(error){return;}
  if(name!=='diagnostika-odis-s.jpg')return;
  var host=img.closest('a.image-wrap')||img.parentElement;
  if(!host||host.querySelector('.js-diagnostic-panel-overlay'))return;
  host.classList.add('js-diagnostic-panel-photo');
  var svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 600 380');svg.setAttribute('preserveAspectRatio','none');
  svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  svg.setAttribute('data-diagnostic-active-panel','none');
  svg.classList.add('js-diagnostic-panel-overlay');
  // Preserve the original layout even if the decorative stylesheet cannot load.
  svg.style.position='absolute';svg.style.pointerEvents='none';svg.style.overflow='hidden';
  var paths=outlines.map(function(d,index){
   var path=document.createElementNS(ns,'path');path.setAttribute('d',d);
   path.setAttribute('fill','none');path.setAttribute('data-diagnostic-panel',String(index+1));
   path.classList.add('js-diagnostic-panel-outline');svg.appendChild(path);return path;
  });
  host.appendChild(svg);
  function fit(){
   var a=img.getBoundingClientRect(),b=host.getBoundingClientRect();
   svg.style.left=(a.left-b.left-host.clientLeft)+'px';svg.style.top=(a.top-b.top-host.clientTop)+'px';
   svg.style.width=a.width+'px';svg.style.height=a.height+'px';
  }
  var resize=new ResizeObserver(fit);resize.observe(img);resize.observe(host);
  img.addEventListener('load',fit);fit();
  items.push({img:img,svg:svg,paths:paths,visible:false,nextPanel:0,finish:null});
 });
 function allowed(){return !pagePaused&&!document.hidden&&!motion.matches;}
 function cancelNext(){if(timer){window.clearTimeout(timer);timer=0;}}
 function stopActive(){
  if(!active)return;
  var item=active.item,path=active.path;active=null;
  path.removeEventListener('animationend',item.finish);path.removeEventListener('animationcancel',item.finish);
  item.finish=null;path.classList.remove('is-lit');item.svg.setAttribute('data-diagnostic-active-panel','none');
 }
 function scheduleNext(immediate){
  if(timer||active||!allowed())return;
  timer=window.setTimeout(function(){timer=0;next();},immediate?0:350);
 }
 function next(){
  if(active||!allowed())return;
  for(var offset=0;offset<items.length;offset++){
   var index=(cursor+offset)%items.length,item=items[index];
   if(!item.visible||!item.img.complete||!item.img.naturalWidth)continue;
   var path=item.paths[item.nextPanel];item.nextPanel=(item.nextPanel+1)%item.paths.length;
   cursor=(index+1)%items.length;active={item:item,path:path};
   item.finish=function(event){
    if(event.target!==path||event.animationName!=='js-diagnostic-outline-pulse'||!active||active.path!==path)return;
    stopActive();scheduleNext(false);
   };
   path.addEventListener('animationend',item.finish);path.addEventListener('animationcancel',item.finish);
   item.svg.setAttribute('data-diagnostic-active-panel',path.getAttribute('data-diagnostic-panel'));
   path.classList.add('is-lit');return;
  }
 }
 function sync(){
  if(!allowed()){cancelNext();stopActive();return;}
  if(active&&!active.item.visible)stopActive();
  scheduleNext(true);
 }
 var observer=new IntersectionObserver(function(entries){
  items.forEach(function(item){
   for(var i=0;i<entries.length;i++)if(entries[i].target===item.img){item.visible=entries[i].isIntersecting&&entries[i].intersectionRatio>=.2;break;}
  });sync();
 },{threshold:.2});
 items.forEach(function(item){observer.observe(item.img);item.img.addEventListener('load',sync);});
 if(motion.addEventListener)motion.addEventListener('change',sync);else motion.addListener(sync);
 document.addEventListener('visibilitychange',sync);
 window.addEventListener('pagehide',function(){pagePaused=true;sync();});
 window.addEventListener('pageshow',function(){pagePaused=false;sync();});
}());
