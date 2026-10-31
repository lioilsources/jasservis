(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var text=JSON.parse(root.querySelector('#wl-messages').textContent);
 var tiles=Array.from(root.querySelectorAll('.wl-brand-tile')),brandAdvice=root.querySelector('#brand-advice'),adviceTitle=root.querySelector('#brand-advice-title');
 var cards=Array.from(root.querySelectorAll('.wl-card')),groups=Array.from(root.querySelectorAll('.wl-group')),brandGroups=Array.from(root.querySelectorAll('.wl-brand'));
 var mainTopics=Array.from(root.querySelectorAll('details.driver-topic')),infoDetails=Array.from(root.querySelectorAll('.wl-infotainment-section,.wl-info-category')),onlinePanels=Array.from(root.querySelectorAll('.online-brand-panel')),vinPanels=Array.from(root.querySelectorAll('.vin-brand-panel'));
 var selectedBrand='',changingTopic=false;
 function validBrand(brand){return Object.prototype.hasOwnProperty.call(text.brands,brand);}
 function updateLanguageLinks(){Array.from(document.querySelectorAll('.language-switcher a')).forEach(function(link){var path=link.getAttribute('href').split(/[?#]/)[0];link.setAttribute('href',path+(selectedBrand?'?znacka='+encodeURIComponent(selectedBrand):'')+(location.hash||''));});}
 function updateURL(mode,clearHash){var url=new URL(location.href);if(selectedBrand)url.searchParams.set('znacka',selectedBrand);else url.searchParams.delete('znacka');if(clearHash)url.hash='';history[mode==='push'?'pushState':'replaceState'](null,'',url.pathname+url.search+url.hash);updateLanguageLinks();}
 function closeContent(){mainTopics.concat(groups,infoDetails).forEach(function(detail){detail.open=false;});}
 function showBrand(){
  cards.forEach(function(card){card.hidden=!(selectedBrand&&card.dataset.brand===selectedBrand);});
  groups.forEach(function(group){var owner=group.closest('.wl-brand');group.hidden=!(owner&&owner.dataset.brand===selectedBrand);});
  Array.from(root.querySelectorAll('.wl-info-category,.wl-infotainment-section')).forEach(function(section){var owner=section.closest('.wl-brand');section.hidden=!(owner&&owner.dataset.brand===selectedBrand);});
  brandGroups.forEach(function(group){group.hidden=group.dataset.brand!==selectedBrand;});
  onlinePanels.forEach(function(panel){panel.hidden=panel.dataset.onlinePanel!==selectedBrand;});
  vinPanels.forEach(function(panel){panel.hidden=panel.dataset.vinPanel!==selectedBrand;});
  tiles.forEach(function(tile){tile.setAttribute('aria-pressed',String(tile.dataset.brand===selectedBrand));});
  brandAdvice.hidden=!selectedBrand;
  adviceTitle.textContent=selectedBrand?text.advicePrefix+' – '+text.brands[selectedBrand]:'';
 }
 function selectBrand(brand,options){options=options||{};if(brand===selectedBrand&&options.toggle)brand='';selectedBrand=validBrand(brand)?brand:'';closeContent();showBrand();updateURL(options.push?'push':'replace',options.clearHash);if(selectedBrand&&options.focus)requestAnimationFrame(function(){brandAdvice.scrollIntoView({behavior:'smooth',block:'start'});adviceTitle.focus({preventScroll:true});});}
 tiles.forEach(function(tile){tile.addEventListener('click',function(){selectBrand(tile.dataset.brand,{toggle:true,push:true,clearHash:true,focus:true});});});
 mainTopics.forEach(function(topic){topic.addEventListener('toggle',function(){if(!topic.open||changingTopic)return;changingTopic=true;mainTopics.forEach(function(other){if(other!==topic)other.open=false;});changingTopic=false;});});
 var userMoved=false;['wheel','touchstart','pointerdown','keydown'].forEach(function(type){window.addEventListener(type,function(){userMoved=true;},{passive:true});});
 function headerOffset(){var offset=12;Array.from(document.querySelectorAll('header.header, .isStuck, [data-sticky-header]')).forEach(function(header){var style=getComputedStyle(header),box=header.getBoundingClientRect();if((style.position==='fixed'||style.position==='sticky')&&box.height>0&&box.top<=1&&box.bottom>0)offset=Math.max(offset,box.bottom+12);});return offset;}
 function targetForHash(){var id;try{id=decodeURIComponent(location.hash.slice(1));}catch(error){return null;}var target=document.getElementById(id);if(!target&&id.indexOf('kontrolka-')===0)target=root.querySelector('[data-item="vw-'+CSS.escape(id.slice(9).toLowerCase())+'"]');if(!target&&['motor','brzdy','pneumatiky','bezpecnost','osvetleni','emise','elektricka-soustava'].indexOf(id)!==-1)target=root.querySelector('.wl-group[id$="-'+CSS.escape(id)+'"]');return target&&root.contains(target)?target:null;}
 function revealHash(initial){var target=targetForHash();if(!target)return;var branded=target.closest('[data-brand]'),brand=branded&&branded.dataset.brand;if(brand&&brand!==selectedBrand){selectedBrand=brand;closeContent();showBrand();updateURL('replace',false);}if(!selectedBrand)return;var detail=target.matches&&target.matches('details')?target:target.closest('details');while(detail){detail.open=true;detail=detail.parentElement&&detail.parentElement.closest('details');}var parentTopic=target.closest('details.driver-topic');if(parentTopic)parentTopic.open=true;requestAnimationFrame(function(){if(initial===true&&userMoved)return;var offset=headerOffset();scrollTo(0,Math.max(0,scrollY+target.getBoundingClientRect().top-offset));if(target.focus)target.focus({preventScroll:true});});}
 var requested=new URLSearchParams(location.search).get('znacka'),hashTarget=targetForHash(),hashBrand=hashTarget&&hashTarget.closest('[data-brand]');selectedBrand=validBrand(hashBrand&&hashBrand.dataset.brand)?hashBrand.dataset.brand:(validBrand(requested)?requested:'');
 showBrand();updateLanguageLinks();if(location.hash)revealHash(true);
 window.addEventListener('popstate',function(){var brand=new URLSearchParams(location.search).get('znacka');selectedBrand=validBrand(brand)?brand:'';closeContent();showBrand();if(location.hash)revealHash();updateLanguageLinks();});
 window.addEventListener('hashchange',function(){userMoved=false;revealHash();updateLanguageLinks();});
})();
