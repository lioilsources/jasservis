/* A small illustrative lift movement. Vehicle/logo pixels come from the original.
   The reconstructed background is visible only within the original subject mask. */
(function(){
 'use strict';
 var photos=Array.prototype.slice.call(document.querySelectorAll('img')).filter(function(img){return /\/cupra-js-servis-zvedak\.jpg(?:[?#]|$)/.test(img.currentSrc||img.src);});
 if(!photos.length)return;
 var ns='http://www.w3.org/2000/svg',serial=0,items=[],pagePaused=false;
 var motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 // Concave lower edge follows both tyres and the rocker, excluding the floor.
 var vehicle='M132 397 C166 353 296 327 416 311 L488 259 C542 224 606 203 660 201 L699 199 L699 195 L738 196 L748 201 C835 200 921 219 978 256 L1022 292 L1057 322 L1074 343 L1080 393 L1087 452 L1083 498 L1071 521 C1068 568 1048 608 1011 615 C974 622 946 600 935 566 L931 529 L592 557 C589 627 555 680 498 687 C429 697 375 655 355 589 L353 582 L241 581 C197 577 145 561 128 543 L121 515 L119 476 L125 438 Z';
 var platform='M576 550 L930 526 L934 571 L611 614 L571 607 L573 570 Z';
 // Keep the complete mechanism in one continuous layer. The affine stretch
 // raises its top with the car while the floor contact at y=840 stays fixed.
 var mechanism='M574 597 L607 602 L636 591 L657 598 L665 608 L850 578 L872 579 L874 594 L790 647 L882 683 L886 693 L881 710 L865 729 L865 754 L808 795 L786 804 L653 843 L634 843 L623 830 L611 828 L602 818 L579 821 L570 830 L543 827 L540 816 L547 805 L560 765 L497 740 L495 721 L522 704 L548 674 L566 657 L546 637 L549 623 Z';
 var links=[{d:mechanism,upper:600,lower:840,upperMove:-30,lowerMove:0}];
 function el(tag,attrs){var n=document.createElementNS(ns,tag);Object.keys(attrs||{}).forEach(function(k){n.setAttribute(k,attrs[k]);});return n;}
 function source(url,attrs){var n=el('image',Object.assign({x:'0',y:'0',width:'1280',height:'960',preserveAspectRatio:'none',href:url},attrs||{}));return n;}
 function path(d,attrs){return el('path',Object.assign({d:d},attrs||{}));}
 function fit(item){if(!item.svg)return;var a=item.img.getBoundingClientRect(),b=item.wrap.getBoundingClientRect();item.svg.style.left=(a.left-b.left-item.wrap.clientLeft)+'px';item.svg.style.top=(a.top-b.top-item.wrap.clientTop)+'px';item.svg.style.width=a.width+'px';item.svg.style.height=a.height+'px';}
 function build(item,background){
  var id='cupra-lift-'+(++serial),url=item.img.currentSrc||item.img.src;
  var svg=el('svg',{viewBox:'0 0 1280 960',preserveAspectRatio:'none','aria-hidden':'true',focusable:'false','data-lift-travel':'30'});svg.classList.add('cupra-lift-scene');svg.style.position='absolute';svg.style.pointerEvents='none';svg.style.overflow='hidden';svg.style.visibility='hidden';
  var defs=el('defs'),car=el('clipPath',{id:id+'-car',clipPathUnits:'userSpaceOnUse'}),scissors=el('clipPath',{id:id+'-scissors',clipPathUnits:'userSpaceOnUse'});
  car.appendChild(path(vehicle));car.appendChild(path(platform));links.forEach(function(part){scissors.appendChild(path(part.d));});
  var clear=el('mask',{id:id+'-clear',maskUnits:'userSpaceOnUse',maskContentUnits:'userSpaceOnUse',x:'0',y:'0',width:'1280',height:'960'});
  clear.appendChild(el('rect',{x:'0',y:'0',width:'1280',height:'960',fill:'#000'}));
  // Remove the whole original subject, independently of the moving clips.
  // A soft outer edge blends only stationary background beyond the silhouette.
  var blend=el('filter',{id:id+'-blend',filterUnits:'userSpaceOnUse',x:'0',y:'0',width:'1280',height:'960'});
  blend.appendChild(el('feGaussianBlur',{stdDeviation:'8'}));defs.appendChild(blend);
  var clearing=el('g',{filter:'url(#'+id+'-blend)'});
  [vehicle,platform,mechanism].forEach(function(d){clearing.appendChild(path(d,{fill:'#fff',stroke:'#fff','stroke-width':'64','stroke-linejoin':'round'}));});
  clear.appendChild(clearing);
  defs.appendChild(car);defs.appendChild(scissors);defs.appendChild(clear);svg.appendChild(defs);
  svg.appendChild(source(url));
  svg.appendChild(source(background,{mask:'url(#'+id+'-clear)'}));
  var movingLinks=el('g',{'class':'cupra-lift__scissors'});
  links.forEach(function(part,index){
   var clip=el('clipPath',{id:id+'-bar-'+index,clipPathUnits:'userSpaceOnUse'});clip.appendChild(path(part.d));defs.appendChild(clip);
   var scale=1+(part.lowerMove-part.upperMove)/(part.lower-part.upper),offset=part.lowerMove-(scale-1)*part.lower;
   var bar=el('g',{'class':'cupra-lift__bar','data-upper-y':part.upper,'data-lower-y':part.lower,'data-upper-move':part.upperMove,'data-lower-move':part.lowerMove});
   bar.style.setProperty('--cupra-lift-bar-scale',scale);bar.style.setProperty('--cupra-lift-bar-offset',offset+'px');
   bar.appendChild(source(url,{'clip-path':'url(#'+id+'-bar-'+index+')'}));movingLinks.appendChild(bar);
  });svg.appendChild(movingLinks);
  var movingCar=el('g',{'class':'cupra-lift__car'});movingCar.appendChild(source(url,{'clip-path':'url(#'+id+'-car)'}));svg.appendChild(movingCar);
  item.svg=svg;item.wrap.appendChild(svg);item.ready=true;fit(item);sync(item);
 }
 function prepare(item){
  if(item.loading||item.ready||item.failed||!item.img.complete||!item.img.naturalWidth)return;
  item.loading=true;
  var background=new URL('../11/cupra-lift-clean-background.png',item.img.currentSrc||item.img.src).href,bg=new Image();
  item.background=bg;
  bg.onload=function(){if(!bg.naturalWidth){fail();return;}var decoded=bg.decode?bg.decode():Promise.resolve();decoded.then(function(){item.loading=false;build(item,background);},fail);};
  function fail(){item.loading=false;item.failed=true;item.wrap.classList.remove('cupra-lift-ready');item.wrap.setAttribute('data-cupra-lift-state','static-asset-error');}
  bg.onerror=fail;bg.src=background;
 }
 function sync(item){
  fit(item);
  if(motion.matches){item.wrap.classList.remove('cupra-lift-ready');if(item.svg)item.svg.classList.remove('is-running');item.wrap.setAttribute('data-cupra-lift-state','static-reduced-motion');return;}
  if(item.visible&&!item.ready&&!item.failed){var box=item.img.getBoundingClientRect();if(box.width>0&&box.height>0)prepare(item);}
  if(item.ready){item.wrap.classList.add('cupra-lift-ready');var styled=window.getComputedStyle(item.svg).visibility==='visible',running=styled&&item.visible&&!document.hidden&&!pagePaused;item.svg.classList.toggle('is-running',running);item.wrap.setAttribute('data-cupra-lift-state',styled?(running?'running':'paused'):'static-style-unavailable');}
 }
 photos.forEach(function(img){
  var wrap=img.parentElement;if(!wrap||wrap.classList.contains('cupra-lift-photo'))return;
  wrap.classList.add('cupra-lift-photo');wrap.setAttribute('data-cupra-lift-state','static-loading');
  var item={img:img,wrap:wrap,svg:null,visible:!('IntersectionObserver' in window),ready:false,loading:false,failed:false};items.push(item);
  img.addEventListener('load',function(){sync(item);});
  if('ResizeObserver' in window){var resize=new ResizeObserver(function(){sync(item);});resize.observe(img);}else window.addEventListener('resize',function(){sync(item);});
  if('IntersectionObserver' in window){var observer=new IntersectionObserver(function(entries){item.visible=entries[0].isIntersecting&&entries[0].intersectionRatio>=.05;sync(item);},{threshold:.05});observer.observe(img);}
  sync(item);
 });
 function all(){items.forEach(sync);}
 var styleLink=document.querySelector('link[href*="/cupra-lift.css"]');if(styleLink){styleLink.addEventListener('load',all);styleLink.addEventListener('error',all);}
 if(motion.addEventListener)motion.addEventListener('change',all);else motion.addListener(all);
 document.addEventListener('visibilitychange',all);
 window.addEventListener('pagehide',function(){pagePaused=true;all();});
 window.addEventListener('pageshow',function(){pagePaused=false;all();});
}());
