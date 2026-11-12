/* Pause offscreen decoration without changing the approved animation timing. */
(function () {
 'use strict';
 // A decorative copy of the advice text travels through the hand into the head.
 document.querySelectorAll('.header-advice-icons').forEach(function(scene){
  var tile=scene.closest('.header-driver-advice');
  if(!tile || tile.classList.contains('has-advice-pour')) return;
  if(!scene.querySelector('.header-advice-car') || !scene.querySelector('.header-advice-mechanic')) return;
  var label=tile.querySelector('.header-action-label');
  if(!label) return;
  var stream=document.createElement('span');
  stream.className='header-advice-transfer';
  stream.setAttribute('aria-hidden','true');
  Array.from(label.textContent.replace(/\s+/g,'').normalize('NFC')).slice(0,9).forEach(function(character,index){
   var letter=document.createElement('i');
   letter.textContent=character;
   letter.style.setProperty('--advice-letter-delay',(index*.11)+'s');
   stream.appendChild(letter);
  });
  tile.appendChild(stream);
  tile.classList.add('has-advice-pour');
  function geometry(){
   var t=tile.getBoundingClientRect(),l=label.getBoundingClientRect(),s=scene.getBoundingClientRect();
   var scaleX=t.width/(tile.offsetWidth||1),scaleY=t.height/(tile.offsetHeight||1);
   if(!scaleX || !scaleY) return;
   var x=(l.left-t.left)/scaleX+6,y=(l.top+l.height*.45-t.top)/scaleY;
   var right=(s.right-t.left)/scaleX,top=(s.top-t.top)/scaleY;
   tile.style.setProperty('--advice-source-x',x+'px');
   tile.style.setProperty('--advice-source-y',y+'px');
   tile.style.setProperty('--advice-hand-dx',(right-13-x)+'px');
   tile.style.setProperty('--advice-hand-dy',(top+25-y)+'px');
   tile.style.setProperty('--advice-pour-dx',(right-40-x)+'px');
   tile.style.setProperty('--advice-pour-dy',(top-2-y)+'px');
   tile.style.setProperty('--advice-head-dx',(right-44-x)+'px');
   tile.style.setProperty('--advice-head-dy',(top+11-y)+'px');
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
