(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var text=JSON.parse(root.querySelector('#wl-messages').textContent),form=root.querySelector('.wl-filters');
 var cards=Array.from(root.querySelectorAll('.wl-card')),groups=Array.from(root.querySelectorAll('.wl-group')),brandGroups=Array.from(root.querySelectorAll('.wl-brand'));
 var fields={};['search','brand','model','color','system','power'].forEach(function(k){fields[k]=root.querySelector('#wl-'+k);});
 cards.forEach(function(card){card._scopes=JSON.parse(card.dataset.scopes);});
 var results=root.querySelector('#prehled-kontrolek'),heading=root.querySelector('#wl-results-title'),context=root.querySelector('#wl-brand-context');
 var requested=new URLSearchParams(location.search).get('znacka');if(Object.prototype.hasOwnProperty.call(text.brands,requested))fields.brand.value=requested;
 function normalize(value){return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
 function updateLanguageLinks(){Array.from(document.querySelectorAll('.language-switcher a')).forEach(function(link){var path=link.getAttribute('href').split(/[?#]/)[0];link.setAttribute('href',path+(fields.brand.value?'?znacka='+encodeURIComponent(fields.brand.value):'')+(location.hash||''));});}
 function updateURL(){var url=new URL(location.href);if(fields.brand.value)url.searchParams.set('znacka',fields.brand.value);else url.searchParams.delete('znacka');history.replaceState(null,'',url.pathname+url.search+url.hash);updateLanguageLinks();}
 function updateModels(){
  var available=new Set();cards.forEach(function(card){if(!fields.brand.value||card.dataset.brand===fields.brand.value)card._scopes.forEach(function(s){available.add(s.model);});});
  Array.from(fields.model.options).forEach(function(option){if(!option.value)return;option.hidden=!available.has(option.value);option.disabled=option.hidden;});
  if(fields.model.selectedOptions[0]&&fields.model.selectedOptions[0].disabled)fields.model.value='';
 }
 function filter(){
  var brand=fields.brand.value,words=normalize(fields.search.value).split(/\s+/).filter(Boolean),count=0,total=0;
  updateModels();
  cards.forEach(function(card){
   var inBrand=!brand||card.dataset.brand===brand;if(inBrand)total++;
   var matchScope=card._scopes.some(function(s){return (!fields.model.value||s.model===fields.model.value)&&(!fields.power.value||s.power.indexOf(fields.power.value)!==-1);});
   var show=inBrand&&matchScope&&(!fields.color.value||card.dataset.color===fields.color.value)&&(!fields.system.value||card.dataset.system===fields.system.value)&&words.every(function(word){return normalize(card.dataset.search).indexOf(word)!==-1;});
   card.hidden=!show;if(show)count++;
  });
  groups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  brandGroups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  results.dataset.selectedBrand=brand;
  heading.textContent=brand?text.brands[brand]+' — '+text.overview:text.overview;
  context.hidden=true;context.textContent=brand?text.preset+text.brands[brand]:'';
  root.querySelector('#wl-count').textContent=text.count.replace('{count}',count).replace('{total}',total);
  var empty=root.querySelector('#wl-empty');empty.hidden=count!==0;empty.textContent=brand&&total===0?text.missingBrand+' '+text.empty:text.empty;
 }
 filter();updateLanguageLinks();form.hidden=false;
 form.addEventListener('submit',function(event){event.preventDefault();});
 form.addEventListener('input',filter);
 form.addEventListener('change',function(){filter();updateURL();});
 function reset(){form.reset();fields.brand.value='';fields.model.value='';filter();updateURL();}
 form.addEventListener('reset',function(event){event.preventDefault();Array.from(form.querySelectorAll('input,select')).forEach(function(el){el.value='';});filter();updateURL();});
 var userMoved=false;
 ['wheel','touchstart','pointerdown','keydown'].forEach(function(type){window.addEventListener(type,function(){userMoved=true;},{passive:true});});
 function headerOffset(){
  var offset=12;
  Array.from(document.querySelectorAll('header.header, .isStuck, [data-sticky-header]')).forEach(function(header){
   var style=getComputedStyle(header),box=header.getBoundingClientRect();
   if((style.position==='fixed'||style.position==='sticky')&&box.height>0&&box.top<=1&&box.bottom>0)offset=Math.max(offset,box.bottom+12);
  });return offset;
 }
 function revealHash(){
  var id;try{id=decodeURIComponent(location.hash.slice(1));}catch(error){return;}
  // Existing individual-card and system anchors remain valid.
  var target=document.getElementById(id);
  if(!target&&id.indexOf('kontrolka-')===0)target=root.querySelector('[data-item="vw-'+id.slice(9).toLowerCase()+'"]');
  if(!target&&['motor','brzdy','pneumatiky','bezpecnost','osvetleni','emise','elektricka-soustava'].indexOf(id)!==-1)target=root.querySelector('.wl-group[id$="-'+id+'"]');
  if(!target||!root.contains(target))return;
  if(target!==results&&target.closest('[hidden]'))target=results;
  if(target.tagName==='DETAILS')target.open=true;
  requestAnimationFrame(function(){var offset=headerOffset();results.style.setProperty('--wl-anchor-offset',offset+'px');scrollTo(0,Math.max(0,scrollY+target.getBoundingClientRect().top-offset));(target===results?heading:target).focus({preventScroll:true});});
 }
 root.querySelector('.wl-countline a').addEventListener('click',function(event){event.preventDefault();reset();userMoved=false;if(location.hash!=='#prehled-kontrolek')location.hash='prehled-kontrolek';else revealHash();});
 window.addEventListener('popstate',function(){var brand=new URLSearchParams(location.search).get('znacka');fields.brand.value=Object.prototype.hasOwnProperty.call(text.brands,brand)?brand:'';filter();});
 window.addEventListener('hashchange',function(){userMoved=false;updateLanguageLinks();revealHash();});
 if(location.hash){
  // WebKit can finish the header/filter layout after the load event. Correct
  // this initial layout shift only until the user interacts; never change the header.
  if(window.ResizeObserver){var initialLayout=new ResizeObserver(function(){if(!userMoved)revealHash();});initialLayout.observe(root);initialLayout.observe(document.body);setTimeout(function(){initialLayout.disconnect();},2500);}
  revealHash();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){if(!userMoved)revealHash();});if(document.readyState!=='complete')window.addEventListener('load',function(){if(!userMoved)revealHash();},{once:true});}
})();
