/* Pause offscreen decoration without changing the approved animation timing. */
(function () {
 'use strict';
 // Make the advice source explicit without changing the link or its label.
 document.querySelectorAll('.header-advice-icons').forEach(function(scene){
  var tile=scene.closest('.header-driver-advice');
  if(!tile || tile.classList.contains('has-advice-source')) return;
  if(!scene.querySelector('.header-advice-car') || !scene.querySelector('.header-advice-mechanic')) return;
  var label=tile.querySelector('.header-action-label');
  if(!label) return;
  scene.insertAdjacentHTML('beforeend',
   '<span class="header-advice-question" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 24" width="28" height="24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" focusable="false"><rect x="2" y="1" width="24" height="19" rx="7" fill="#242323"/><path d="m7 20-3 3M11 7a3 3 0 1 1 5 2c-1 1-2 1-2 3"/><circle cx="14" cy="16" r=".9" fill="currentColor" stroke="none"/></svg></span>'+
   '<span class="header-advice-idea" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 28" width="24" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M8 19c0-3-4-4-4-9a8 8 0 0 1 16 0c0 5-4 6-4 9H8ZM8 23h8M10 26h4M10 19v-6l-2-2m6 8v-6l2-2" fill="#242323"/></svg></span>');
  tile.insertAdjacentHTML('beforeend','<span class="header-advice-transfer" aria-hidden="true"><i></i><i></i><i></i></span>');
  tile.classList.add('has-advice-source');
  function geometry(){
   var t=tile.getBoundingClientRect(),l=label.getBoundingClientRect(),s=scene.getBoundingClientRect();
   // Account for an ancestor transform when converting viewport to tile coordinates.
   var scaleX=t.width/(tile.offsetWidth||1),scaleY=t.height/(tile.offsetHeight||1);
   if(!scaleX || !scaleY) return;
   var x=(l.left+l.width/2-t.left)/scaleX,y=(l.bottom-t.top)/scaleY+5;
   tile.style.setProperty('--advice-source-x',x+'px');
   tile.style.setProperty('--advice-source-y',y+'px');
   tile.style.setProperty('--advice-source-mid-dx',((l.left-t.left)/scaleX-8-x)+'px');
   tile.style.setProperty('--advice-source-dx',((s.right-t.left)/scaleX-13-x)+'px');
   tile.style.setProperty('--advice-source-dy',((s.top-t.top)/scaleY+10-y)+'px');
  }
  geometry();
  if('ResizeObserver' in window){var sizeObserver=new ResizeObserver(geometry);sizeObserver.observe(tile);sizeObserver.observe(label);}
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
