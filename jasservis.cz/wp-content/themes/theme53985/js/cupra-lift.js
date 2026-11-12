/* A small illustrative lift movement. Vehicle/logo pixels come from the original.
   The reconstructed background is visible only within the original subject mask. */
(function(){
 'use strict';
 var photos=Array.prototype.slice.call(document.querySelectorAll('img')).filter(function(img){return /\/cupra-js-servis-zvedak\.jpg(?:[?#]|$)/.test(img.currentSrc||img.src);});
 if(!photos.length)return;
 var ns='http://www.w3.org/2000/svg',serial=0,items=[],pagePaused=false,travel=12;
 var motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 // The upper edge follows the bonnet and windscreen, leaving the cabinet fixed.
 // The concave lower edge follows both tyres and the rocker, excluding the floor.
 var vehicle='M132.00 397.00 L135.00 394.00 L138.00 392.00 L141.00 389.00 L145.00 386.00 L150.00 383.00 L154.00 381.00 L159.00 378.00 L164.00 376.00 L169.00 373.00 L175.00 371.00 L181.00 368.00 L188.00 366.00 L194.00 363.00 L201.00 361.00 L208.00 359.00 L215.00 356.00 L223.00 354.00 L231.00 352.00 L239.00 350.00 L247.00 348.00 L255.00 345.00 L264.00 343.00 L273.00 341.00 L282.00 339.00 L291.00 338.00 L300.00 336.00 L309.00 334.00 L319.00 332.00 L328.00 330.00 L338.00 329.00 L348.00 327.00 L358.00 325.00 L368.00 324.00 L378.00 322.00 L388.00 321.00 L399.00 320.00 L409.00 318.00 L420.00 317.00 L430.00 316.00 L434.00 313.00 L437.00 311.00 L441.00 308.00 L445.00 305.00 L449.00 303.00 L453.00 300.00 L457.00 297.00 L461.00 295.00 L465.00 292.00 L469.00 289.00 L473.00 287.00 L478.00 284.00 L482.00 281.00 L486.00 279.00 L490.00 276.00 L495.00 273.00 L499.00 271.00 L503.00 268.00 L508.00 265.00 L512.00 263.00 L516.00 260.00 L521.00 258.00 L525.00 255.00 L530.00 253.00 L534.00 251.00 L539.00 248.00 L543.00 246.00 L548.00 244.00 L552.00 241.00 L557.00 239.00 L561.00 237.00 L566.00 235.00 L570.00 233.00 L575.00 231.00 L579.00 229.00 L584.00 227.00 L588.00 225.00 L593.00 224.00 L597.00 222.00 L599.00 221.00 L601.00 220.00 L604.00 220.00 L606.00 219.00 L608.00 218.00 L610.00 217.00 L612.00 217.00 L614.00 216.00 L616.00 215.00 L618.00 214.00 L621.00 214.00 L623.00 213.00 L625.00 213.00 L627.00 212.00 L629.00 211.00 L631.00 211.00 L633.00 210.00 L635.00 210.00 L637.00 209.00 L639.00 209.00 L641.00 208.00 L643.00 208.00 L645.00 207.00 L647.00 207.00 L649.00 206.00 L651.00 206.00 L653.00 206.00 L655.00 205.00 L657.00 205.00 L659.00 205.00 L661.00 204.00 L663.00 204.00 L665.00 204.00 L667.00 203.00 L670.00 203.00 L672.00 203.00 L674.00 202.00 L676.00 202.00 L678.00 202.00 L699.00 199.00 L699.00 195.00 L738.00 196.00 L748.00 201.00 L755.00 201.00 L761.00 201.00 L768.00 201.00 L775.00 201.00 L781.00 202.00 L788.00 202.00 L795.00 202.00 L801.00 203.00 L808.00 203.00 L814.00 204.00 L821.00 205.00 L827.00 206.00 L834.00 207.00 L840.00 208.00 L846.00 209.00 L853.00 210.00 L859.00 211.00 L865.00 212.00 L871.00 214.00 L877.00 215.00 L883.00 216.00 L889.00 218.00 L895.00 220.00 L901.00 221.00 L907.00 223.00 L912.00 225.00 L918.00 227.00 L923.00 229.00 L929.00 231.00 L934.00 233.00 L940.00 236.00 L945.00 238.00 L950.00 240.00 L955.00 243.00 L960.00 245.00 L964.00 248.00 L969.00 250.00 L974.00 253.00 L978.00 256.00 L1022.00 292.00 L1057.00 322.00 L1074.00 343.00 L1080.00 393.00 L1082.00 451.00 L1079.00 484.00 L1073.00 499.00 L1072.55 500.00 L119.00 500.00 L119.00 476.00 L125.00 438.00 Z M122.00 500.00 L122.00 502.00 L124.00 503.00 L124.00 512.00 L125.00 513.00 L125.00 531.00 L123.00 534.00 L123.00 539.00 L123.00 537.00 L124.00 536.00 L125.00 537.00 L126.00 542.00 L130.00 546.00 L133.00 547.00 L142.00 558.00 L146.00 559.00 L151.00 564.00 L159.00 568.00 L163.00 569.00 L166.00 572.00 L176.00 577.00 L180.00 577.00 L184.00 579.00 L195.00 579.00 L199.00 575.00 L216.00 575.00 L218.00 577.00 L223.00 577.00 L224.00 578.00 L239.00 578.00 L240.00 579.00 L247.00 579.00 L248.00 580.00 L272.00 580.00 L273.00 581.00 L351.00 581.00 L352.00 582.00 L352.00 588.00 L357.00 593.00 L357.00 596.00 L360.00 598.00 L360.00 600.00 L361.00 601.00 L361.00 605.00 L362.00 606.00 L362.00 609.00 L363.00 610.00 L364.00 615.00 L365.00 617.00 L366.00 617.00 L368.00 619.00 L371.00 625.00 L371.00 627.00 L373.00 629.00 L375.00 634.00 L378.00 638.00 L376.00 641.00 L374.00 639.00 L379.00 645.00 L379.00 646.00 L388.00 655.00 L390.00 655.00 L393.00 658.00 L394.00 658.00 L397.00 661.00 L400.00 662.00 L402.00 664.00 L406.00 666.00 L408.00 666.00 L410.00 668.00 L414.00 669.00 L416.00 671.00 L421.00 672.00 L426.00 675.00 L429.00 675.00 L432.00 677.00 L434.00 677.00 L438.00 679.00 L442.00 679.00 L443.00 680.00 L447.00 680.00 L448.00 681.00 L452.00 681.00 L453.00 682.00 L457.00 682.00 L458.00 683.00 L466.00 683.00 L467.00 684.00 L471.00 684.00 L472.00 682.00 L475.00 682.00 L476.00 681.00 L481.00 681.00 L482.00 682.00 L490.00 681.00 L489.00 680.00 L492.00 678.00 L495.00 678.00 L497.00 676.00 L505.00 674.00 L510.00 670.00 L513.00 670.00 L516.00 667.00 L519.00 667.00 L520.00 665.00 L521.00 665.00 L524.00 662.00 L527.00 661.00 L536.00 653.00 L536.00 652.00 L552.00 635.00 L552.00 633.00 L556.00 629.00 L556.00 627.00 L560.00 622.00 L563.00 622.00 L564.00 621.00 L575.00 621.00 L576.00 620.00 L578.00 620.00 L595.00 603.00 L595.00 595.00 L599.00 590.00 L600.00 578.00 L602.00 576.00 L622.00 575.00 L623.00 574.00 L628.00 575.00 L629.00 574.00 L633.00 574.00 L634.00 573.00 L641.00 573.00 L642.00 574.00 L644.00 574.00 L645.00 573.00 L649.00 573.00 L650.00 574.00 L666.00 574.00 L669.00 571.00 L687.00 571.00 L688.00 572.00 L691.00 572.00 L693.00 570.00 L697.00 570.00 L698.00 569.00 L715.00 569.00 L717.00 567.00 L723.00 568.00 L724.00 569.00 L729.00 569.00 L730.00 568.00 L733.00 568.00 L735.00 566.00 L738.00 566.00 L739.00 567.00 L743.00 567.00 L744.00 566.00 L766.00 566.00 L768.00 564.00 L779.00 565.00 L781.00 563.00 L787.00 563.00 L788.00 562.00 L797.00 562.00 L798.00 563.00 L804.00 563.00 L805.00 562.00 L817.00 562.00 L818.00 561.00 L829.00 561.00 L830.00 560.00 L842.00 560.00 L843.00 559.00 L863.00 558.00 L864.00 557.00 L875.00 557.00 L876.00 556.00 L881.00 556.00 L882.00 555.00 L886.00 555.00 L887.00 556.00 L896.00 556.00 L900.00 553.00 L909.00 553.00 L910.00 552.00 L914.00 552.00 L915.00 553.00 L915.00 571.00 L928.00 584.00 L929.00 586.00 L929.00 590.00 L933.00 594.00 L933.00 595.00 L941.00 602.00 L942.00 602.00 L944.00 604.00 L949.00 605.00 L954.00 608.00 L957.00 608.00 L958.00 609.00 L961.00 609.00 L962.00 610.00 L965.00 610.00 L966.00 611.00 L969.00 611.00 L970.00 612.00 L983.00 613.00 L984.00 614.00 L1004.00 614.00 L1005.00 613.00 L1010.00 612.00 L1014.00 609.00 L1021.00 606.00 L1032.00 595.00 L1032.00 594.00 L1039.00 585.00 L1040.00 582.00 L1041.00 581.00 L1045.00 581.00 L1045.00 569.00 L1047.00 565.00 L1047.00 560.00 L1051.00 551.00 L1051.00 548.00 L1052.00 547.00 L1052.00 540.00 L1053.00 539.00 L1053.00 516.00 L1067.00 502.00 L1067.00 500.00 Z';
 var platform='M590 556 L916 528 L917 575 L596 610 L575 600 L577 578 Z';
 // Keep the complete mechanism in one continuous layer. The affine stretch
 // raises its top with the car while the floor contact at y=840 stays fixed.
 var mechanism='M574 597 L607 602 L636 591 L657 598 L665 608 L850 578 L872 579 L874 594 L790 647 L882 683 L886 693 L881 710 L865 729 L865 754 L808 795 L786 804 L653 843 L634 843 L623 830 L611 828 L602 818 L579 821 L570 830 L543 827 L540 816 L547 805 L560 765 L497 740 L495 721 L522 704 L548 674 L566 657 L546 637 L549 623 Z';
 var links=[{d:mechanism,upper:600,lower:840,upperMove:-travel,lowerMove:0}];
 function el(tag,attrs){var n=document.createElementNS(ns,tag);Object.keys(attrs||{}).forEach(function(k){n.setAttribute(k,attrs[k]);});return n;}
 function source(url,attrs){var n=el('image',Object.assign({x:'0',y:'0',width:'1280',height:'960',preserveAspectRatio:'none',href:url},attrs||{}));return n;}
 function path(d,attrs){return el('path',Object.assign({d:d},attrs||{}));}
 function fit(item){if(!item.svg)return;var a=item.img.getBoundingClientRect(),b=item.wrap.getBoundingClientRect();item.svg.style.left=(a.left-b.left-item.wrap.clientLeft)+'px';item.svg.style.top=(a.top-b.top-item.wrap.clientTop)+'px';item.svg.style.width=a.width+'px';item.svg.style.height=a.height+'px';}
 function build(item,background){
  var id='cupra-lift-'+(++serial),url=item.img.currentSrc||item.img.src;
  var svg=el('svg',{viewBox:'0 0 1280 960',preserveAspectRatio:'none','aria-hidden':'true',focusable:'false','data-lift-travel':String(travel)});svg.classList.add('cupra-lift-scene');svg.style.setProperty('--cupra-lift-car-offset',(-travel)+'px');svg.style.position='absolute';svg.style.pointerEvents='none';svg.style.overflow='hidden';svg.style.visibility='hidden';
  var defs=el('defs'),car=el('clipPath',{id:id+'-car',clipPathUnits:'userSpaceOnUse'}),scissors=el('clipPath',{id:id+'-scissors',clipPathUnits:'userSpaceOnUse'});
  car.appendChild(path(vehicle));car.appendChild(path(platform));links.forEach(function(part){scissors.appendChild(path(part.d));});
  var clear=el('mask',{id:id+'-clear',maskUnits:'userSpaceOnUse',maskContentUnits:'userSpaceOnUse',x:'0',y:'0',width:'1280',height:'960'});
  clear.appendChild(el('rect',{x:'0',y:'0',width:'1280',height:'960',fill:'#000'}));
  // Replace only the original subject footprint. A wide blurred clearing
  // halo exposed a second cabinet/floor outside the moving photograph.
  // The stationary room must remain exactly the original image there.
  [vehicle,platform,mechanism].forEach(function(d){clear.appendChild(path(d,{fill:'#fff',stroke:'#fff','stroke-width':'4','stroke-linejoin':'round'}));});
  defs.appendChild(car);defs.appendChild(scissors);defs.appendChild(clear);svg.appendChild(defs);
  svg.appendChild(source(url));
  svg.appendChild(source(background,{mask:'url(#'+id+'-clear)'}));
  // Continue the photographed cabinet below the bumper from the same photo.
  // This avoids the reconstructed plate's different cabinet/column boundary.
  var bumperRoom=el('clipPath',{id:id+'-bumper-room',clipPathUnits:'userSpaceOnUse'});
  bumperRoom.appendChild(el('rect',{x:'112',y:'520',width:'242',height:'80'}));defs.appendChild(bumperRoom);
  var room=el('g',{'clip-path':'url(#'+id+'-bumper-room)','mask':'url(#'+id+'-clear)'});
  room.appendChild(source(url,{y:'-40'}));svg.appendChild(room);
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
