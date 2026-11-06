/* No image carousel: one photograph, two localised offers and a small silent oil layer. */
(function () {
 'use strict';
 var hero=document.querySelector('[data-oil-hero]');
 if (!hero) return;
 var slides=Array.from(hero.querySelectorAll('[data-oil-slide]'));
 var video=hero.querySelector('video'),frame=hero.querySelector('.oil-hero__frame');
 var controls=hero.querySelector('.oil-hero__controls'),pause=hero.querySelector('[data-oil-pause]');
 var icon=hero.querySelector('[data-oil-pause-icon]'),status=hero.querySelector('.oil-hero__status');
 var reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 var fine=window.matchMedia('(hover: hover) and (pointer: fine)');
 var lang=hero.getAttribute('data-oil-lang');
 var labels={
  cs:['Pozastavit animaci a střídání textů','Pokračovat v animaci a střídání textů','Automatika vypnuta: omezený pohyb'],
  en:['Pause animation and text rotation','Resume animation and text rotation','Automatic motion off: reduced motion'],
  de:['Animation und Textwechsel pausieren','Animation und Textwechsel fortsetzen','Automatik aus: reduzierte Bewegung'],
  uk:['Призупинити анімацію та зміну текстів','Продовжити анімацію та зміну текстів','Автоматичний рух вимкнено: зменшення руху'],
  vi:['Tạm dừng hiệu ứng và chuyển nội dung','Tiếp tục hiệu ứng và chuyển nội dung','Tắt hiệu ứng tự động: giảm chuyển động']
 }[lang];
 var index=0,timer=null,paused=false,focused=false,hovered=false,visible=false,loaded=false;
 var paintReady=false,photo=hero.querySelector('img');
 function fit() {
  var w=Math.max(hero.clientWidth,hero.clientHeight*1980/1312);
  frame.style.width=w+'px';frame.style.height=(w*1312/1980)+'px';
 }
 function show(next,manual) {
  index=(next+slides.length)%slides.length;
  slides.forEach(function(slide,i){
   var active=i===index;slide.classList.toggle('is-active',active);
   slide.setAttribute('aria-hidden',String(!active));slide.inert=!active;
   slide.querySelector('a').tabIndex=active?0:-1;
  });
  hero.querySelector('.oil-hero__count').textContent=(index+1)+' / '+slides.length;
  if (manual) status.textContent=slides[index].querySelector('.oil-hero__title').textContent;
 }
 function run() {
  clearTimeout(timer);
  var moving=visible&&paintReady&&!document.hidden&&!paused&&!reduced.matches;
  if (moving&&!focused&&!hovered) timer=setTimeout(function(){show(index+1,false);run();},5500);
  pause.disabled=reduced.matches;
  pause.setAttribute('aria-label',reduced.matches?labels[2]:(paused?labels[1]:labels[0]));
  pause.setAttribute('aria-pressed',String(paused||reduced.matches));
  icon.textContent='';
  if (moving) {
   if (!loaded) {
    ['webm','mp4'].forEach(function(format){
     var source=document.createElement('source');
     source.src=video.getAttribute('data-'+format);source.type='video/'+format;
     video.appendChild(source);
    });
    video.muted=true;video.defaultMuted=true;video.load();loaded=true;
   }
   var playing=video.play();if(playing) playing.catch(function(){video.classList.remove('is-playing');});
  } else video.pause();
  if (reduced.matches&&loaded) {
   video.classList.remove('is-playing');video.replaceChildren();video.removeAttribute('src');video.load();loaded=false;
  }
 }
 hero.querySelector('[data-oil-prev]').addEventListener('click',function(){show(index-1,true);run();});
 hero.querySelector('[data-oil-next]').addEventListener('click',function(){show(index+1,true);run();});
 pause.addEventListener('click',function(){paused=!paused;run();});
 hero.addEventListener('focusin',function(){focused=true;run();});
 hero.addEventListener('focusout',function(){setTimeout(function(){focused=hero.contains(document.activeElement);run();},0);});
 hero.addEventListener('pointerenter',function(){if(fine.matches){hovered=true;run();}});
 hero.addEventListener('pointerleave',function(){hovered=false;run();});
 video.addEventListener('playing',function(){video.classList.add('is-playing');});
 video.addEventListener('error',function(){video.classList.remove('is-playing');});
 document.addEventListener('visibilitychange',run);
 reduced.addEventListener('change',run);
 if ('ResizeObserver' in window) new ResizeObserver(fit).observe(hero);
 else window.addEventListener('resize',fit);
 if ('IntersectionObserver' in window) {
  new IntersectionObserver(function(entries){visible=entries[0].isIntersecting;run();},{threshold:0.05}).observe(hero);
 } else visible=true;
 function afterPhoto(){
  requestAnimationFrame(function(){requestAnimationFrame(function(){paintReady=true;run();});});
 }
 if(photo.complete) afterPhoto();else{photo.addEventListener('load',afterPhoto,{once:true});photo.addEventListener('error',afterPhoto,{once:true});}
 fit();controls.hidden=false;run();
}());
