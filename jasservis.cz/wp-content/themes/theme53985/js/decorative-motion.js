/* Pause offscreen decoration without changing the approved animation timing. */
(function () {
 'use strict';
 // Pull a complete copy of the advice label toward the mechanic, then think.
 document.querySelectorAll('.header-advice-icons').forEach(function(scene){
  var tile=scene.closest('.header-driver-advice');
  if(!tile || tile.classList.contains('has-advice-pull')) return;
  if(!scene.querySelector('.header-advice-car') || !scene.querySelector('.header-advice-mechanic')) return;
  var label=tile.querySelector('.header-action-label');
  if(!label) return;
  var transfer=document.createElement('span'),copy=document.createElement('span');
  transfer.className='header-advice-transfer';
  transfer.setAttribute('aria-hidden','true');
  copy.className='header-advice-copy';
  copy.textContent=label.textContent.replace(/\s+/g,' ').trim();
  transfer.appendChild(copy);
  tile.appendChild(transfer);
  tile.classList.add('has-advice-pull');
  function geometry(){
   var t=tile.getBoundingClientRect(),l=label.getBoundingClientRect(),s=scene.getBoundingClientRect();
   var scaleX=t.width/(tile.offsetWidth||1),scaleY=t.height/(tile.offsetHeight||1);
   if(!scaleX || !scaleY) return;
   var x=(l.left-t.left)/scaleX,y=(l.top-t.top)/scaleY;
   tile.style.setProperty('--advice-copy-x',x+'px');
   tile.style.setProperty('--advice-copy-y',y+'px');
   tile.style.setProperty('--advice-copy-width',(l.width/scaleX)+'px');
   tile.style.setProperty('--advice-copy-height',(l.height/scaleY)+'px');
   tile.style.setProperty('--advice-pull-dx',((s.right-t.left)/scaleX-33-x)+'px');
   tile.style.setProperty('--advice-pull-dy',((s.top-t.top)/scaleY+10-y)+'px');
   var font=window.getComputedStyle(label);
   ['fontFamily','fontSize','fontWeight','fontStyle','lineHeight','letterSpacing','textTransform'].forEach(function(property){copy.style[property]=font[property];});
   copy.style.textAlign='left';
  }
  geometry();
  if('ResizeObserver' in window){var sizeObserver=new ResizeObserver(geometry);sizeObserver.observe(tile);sizeObserver.observe(label);sizeObserver.observe(scene);}
  else window.addEventListener('resize',geometry);
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(geometry);
 });
 var regions=document.querySelectorAll('.header-advice-icons,.header-advice-transfer,.professional-home__grid');
 if (!regions.length) return;
 function visibility(){document.body.classList.toggle('is-page-inactive',document.hidden);}
 document.addEventListener('visibilitychange',visibility);
 window.addEventListener('pageshow',visibility);
 visibility();
 if (!('IntersectionObserver' in window)) return;
 var observer=new IntersectionObserver(function(entries){
  entries.forEach(function(entry){entry.target.classList.toggle('is-motion-offscreen',!entry.isIntersecting);});
 },{threshold:0});
 regions.forEach(function(region){
  region.classList.add('js-motion-region','is-motion-offscreen');
  observer.observe(region);
 });
}());
