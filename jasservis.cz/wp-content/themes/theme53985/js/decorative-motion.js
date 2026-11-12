/* Pause offscreen decoration without changing the approved animation timing. */
(function () {
 'use strict';
 // Keep the advice story identical on every page without duplicating SVG markup.
 document.querySelectorAll('.header-advice-icons').forEach(function(scene){
  if(scene.classList.contains('has-advice-reading')) return;
  if(!scene.querySelector('.header-advice-car') || !scene.querySelector('.header-advice-mechanic')) return;
  scene.insertAdjacentHTML('beforeend',
   '<span class="header-advice-book" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 26" width="32" height="26" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M16 6C11 2 6 2 2 4v17c5-2 10-1 14 2 4-3 9-4 14-2V4c-4-2-9-2-14 2Z" fill="#242323"/><path d="M16 6v17M6 8l6 2M6 13l6 2M20 10l6-2M20 15l6-2"/></svg></span>'+
   '<span class="header-advice-idea" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 28" width="24" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" focusable="false"><path d="M8 19c0-3-4-4-4-9a8 8 0 0 1 16 0c0 5-4 6-4 9H8ZM8 23h8M10 26h4M10 19v-6l-2-2m6 8v-6l2-2" fill="#242323"/></svg></span>');
  scene.classList.add('has-advice-reading');
 });
 var regions=document.querySelectorAll('.header-advice-icons,.professional-home__grid');
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
