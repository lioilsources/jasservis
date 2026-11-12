/* Pause offscreen decoration without changing the approved animation timing. */
(function () {
 'use strict';
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
