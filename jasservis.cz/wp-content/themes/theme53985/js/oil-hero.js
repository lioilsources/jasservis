/* Two persistent offers around one photograph and its silent oil layer. */
(function () {
 'use strict';
 var hero=document.querySelector('[data-oil-hero]');
 if (!hero) return;
 var video=hero.querySelector('video'),frame=hero.querySelector('.oil-hero__frame');
 var reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 // Linux WebKit ends these clips early. Use the original photo on Safari/WebKit,
 // including all iOS browsers; do not hide a decoder failure with seek/replay hacks.
 var staticOil=/AppleWebKit\//.test(navigator.userAgent)&&!/(?:Chrome|Chromium|Edg|OPR|SamsungBrowser)\//.test(navigator.userAgent);
 hero.setAttribute('data-oil-playback',staticOil?'static-webkit':'native-c');
 var visible=false,loaded=false;
 var mediaFailed=false;
 var paintReady=false,photo=hero.querySelector('img');
 function clearFlow() {
  loaded=false;mediaFailed=false;
  video.autoplay=false;video.pause();video.classList.remove('is-playing');
  video.removeAttribute('src');video.replaceChildren();video.load();
 }
 function loadFlow(){
  video.muted=true;video.defaultMuted=true;
  ['webm','mp4'].forEach(function(format){
   var source=document.createElement('source');
   source.src=video.getAttribute('data-'+format);
   source.type=format==='webm'?'video/webm; codecs="vp9"':'video/mp4';
   video.appendChild(source);
  });
  loaded=true;video.load();
 }
 function fit() {
  var w=Math.max(hero.clientWidth,hero.clientHeight*1980/1312);
  frame.style.width=w+'px';frame.style.height=(w*1312/1980)+'px';
 }
 function run() {
  var moving=visible&&paintReady&&!document.hidden&&!reduced.matches;
  if (moving&&!staticOil&&!mediaFailed) {
   video.classList.add('oil-hero__flow--contour');
   video.autoplay=true;
   if(!loaded) loadFlow();
   var playing=video.play();if(playing) playing.catch(function(){video.classList.remove('is-playing');});
  } else {video.autoplay=false;video.pause();video.classList.remove('is-playing');}
  if (reduced.matches&&loaded) clearFlow();
 }
 video.addEventListener('playing',function(){
  if(visible&&!document.hidden&&!reduced.matches) video.classList.add('is-playing');
  else {video.pause();video.classList.remove('is-playing');}
 });
 video.addEventListener('error',function(){mediaFailed=true;video.classList.remove('is-playing');video.pause();});
 document.addEventListener('visibilitychange',run);
 window.addEventListener('pagehide',clearFlow);
 window.addEventListener('pageshow',run);
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
 fit();run();
}());
