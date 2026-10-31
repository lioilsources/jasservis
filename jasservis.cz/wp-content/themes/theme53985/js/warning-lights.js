(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var text=JSON.parse(root.querySelector('#wl-messages').textContent);
 var cards=Array.from(root.querySelectorAll('.wl-card')),groups=Array.from(root.querySelectorAll('.wl-group')),brandGroups=Array.from(root.querySelectorAll('.wl-brand'));
 var tiles=Array.from(root.querySelectorAll('.wl-brand-tile')),results=root.querySelector('#prehled-kontrolek'),heading=root.querySelector('#wl-results-title'),search=root.querySelector('#wl-search'),contact=root.querySelector('.wl-contact');
 var selectedBrand='';
 function normalize(value){return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
 function validBrand(brand){return Object.prototype.hasOwnProperty.call(text.brands,brand);}
 function updateLanguageLinks(){Array.from(document.querySelectorAll('.language-switcher a')).forEach(function(link){var path=link.getAttribute('href').split(/[?#]/)[0];link.setAttribute('href',path+(selectedBrand?'?znacka='+encodeURIComponent(selectedBrand):'')+(location.hash||''));});}
 function updateURL(){var url=new URL(location.href);if(selectedBrand)url.searchParams.set('znacka',selectedBrand);else url.searchParams.delete('znacka');history.replaceState(null,'',url.pathname+url.search+url.hash);updateLanguageLinks();}
 function showBrand(){
  var words=normalize(search.value).split(/\s+/).filter(Boolean),visible=0;
  cards.forEach(function(card){var show=selectedBrand&&card.dataset.brand===selectedBrand&&words.every(function(word){return normalize(card.dataset.search||'').indexOf(word)!==-1;});card.hidden=!show;if(show)visible++;});
  groups.forEach(function(group){var hasCards=group.querySelector('.wl-card');var owner=group.closest('.wl-brand');group.hidden=hasCards?!group.querySelector('.wl-card:not([hidden])'):!(owner&&owner.dataset.brand===selectedBrand);});
  Array.from(root.querySelectorAll('.wl-info-category')).forEach(function(section){section.hidden=!section.querySelector('.wl-card:not([hidden])');});
  Array.from(root.querySelectorAll('.wl-infotainment-section')).forEach(function(section){section.hidden=!section.querySelector('.wl-card:not([hidden])');});
  brandGroups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  tiles.forEach(function(tile){tile.setAttribute('aria-pressed',String(tile.dataset.brand===selectedBrand));});
  results.hidden=!selectedBrand;heading.textContent=selectedBrand?text.brands[selectedBrand]+' — '+text.overview:text.overview;
  if(contact)contact.hidden=!selectedBrand;
  root.querySelector('.wl-search-empty').hidden=!selectedBrand||visible!==0;
 }
 function selectBrand(brand,moveFocus){selectedBrand=brand;search.value='';groups.forEach(function(group){group.open=false;});showBrand();updateURL();if(brand&&moveFocus)requestAnimationFrame(function(){results.scrollIntoView({behavior:'smooth',block:'start'});heading.focus({preventScroll:true});});}
 tiles.forEach(function(tile){tile.addEventListener('click',function(){selectBrand(selectedBrand===tile.dataset.brand?'':tile.dataset.brand,true);});});
 search.addEventListener('input',showBrand);
 var userMoved=false;['wheel','touchstart','pointerdown','keydown'].forEach(function(type){window.addEventListener(type,function(){userMoved=true;},{passive:true});});
 function headerOffset(){var offset=12;Array.from(document.querySelectorAll('header.header, .isStuck, [data-sticky-header]')).forEach(function(header){var style=getComputedStyle(header),box=header.getBoundingClientRect();if((style.position==='fixed'||style.position==='sticky')&&box.height>0&&box.top<=1&&box.bottom>0)offset=Math.max(offset,box.bottom+12);});return offset;}
 function targetForHash(){
  var id;try{id=decodeURIComponent(location.hash.slice(1));}catch(error){return null;}
  var target=document.getElementById(id);
  if(!target&&id.indexOf('kontrolka-')===0)target=root.querySelector('[data-item="vw-'+CSS.escape(id.slice(9).toLowerCase())+'"]');
  if(!target&&['motor','brzdy','pneumatiky','bezpecnost','osvetleni','emise','elektricka-soustava'].indexOf(id)!==-1)target=root.querySelector('.wl-group[id$="-'+CSS.escape(id)+'"]');
  return target&&root.contains(target)?target:null;
 }
 function revealHash(initial){
  var target=targetForHash();if(!target)return;
  var parentTopic=target.closest('details.driver-topic');if(parentTopic)parentTopic.open=true;
  var branded=target.closest('[data-brand]');if(branded&&branded.dataset.brand!==selectedBrand){selectedBrand=branded.dataset.brand;showBrand();updateURL();}
  var parentGroup=target.closest('details.wl-group');if(parentGroup)parentGroup.open=true;
  if(target.matches&&target.matches('details.wl-group'))target.open=true;
  if(target.closest('[hidden]'))target=results;
  requestAnimationFrame(function(){if(initial===true&&userMoved)return;var offset=headerOffset();results.style.setProperty('--wl-anchor-offset',offset+'px');scrollTo(0,Math.max(0,scrollY+target.getBoundingClientRect().top-offset));(target===results?heading:target).focus({preventScroll:true});});
 }
 var requested=new URLSearchParams(location.search).get('znacka');selectedBrand=validBrand(requested)?requested:'';
 var hashTarget=targetForHash(),hashBrand=hashTarget&&hashTarget.closest('[data-brand]');if(hashBrand)selectedBrand=hashBrand.dataset.brand;
 showBrand();updateLanguageLinks();
 window.addEventListener('popstate',function(){var brand=new URLSearchParams(location.search).get('znacka');selectedBrand=validBrand(brand)?brand:'';showBrand();});
 window.addEventListener('hashchange',function(){userMoved=false;updateLanguageLinks();revealHash();});
 if(location.hash){
  if(window.ResizeObserver){var initialLayout=new ResizeObserver(function(){if(!userMoved)revealHash(true);});initialLayout.observe(root);initialLayout.observe(document.body);setTimeout(function(){initialLayout.disconnect();},2500);}
  revealHash(true);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){if(!userMoved)revealHash(true);});if(document.readyState!=='complete')window.addEventListener('load',function(){if(!userMoved)revealHash(true);},{once:true});
 }
 var onlineTiles=Array.from(root.querySelectorAll('.online-brand-tile')),onlinePanels=Array.from(root.querySelectorAll('.online-brand-panel'));
 function selectOnlineBrand(brand,moveFocus){
  onlineTiles.forEach(function(tile){tile.setAttribute('aria-pressed',String(tile.dataset.onlineBrand===brand));});
  onlinePanels.forEach(function(panel){panel.hidden=panel.dataset.onlinePanel!==brand;});
  if(brand&&moveFocus){var panel=root.querySelector('[data-online-panel="'+CSS.escape(brand)+'"]');if(panel)requestAnimationFrame(function(){panel.scrollIntoView({behavior:'smooth',block:'start'});var title=panel.querySelector('h2');if(title)title.focus({preventScroll:true});});}
 }
 onlineTiles.forEach(function(tile){tile.addEventListener('click',function(){selectOnlineBrand(tile.getAttribute('aria-pressed')==='true'?'':tile.dataset.onlineBrand,true);});});
})();
