(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var form=root.querySelector('.wl-filters'),cards=Array.prototype.slice.call(root.querySelectorAll('.wl-card')),groups=Array.prototype.slice.call(root.querySelectorAll('.wl-group'));
 var search=root.querySelector('#wl-search'),color=root.querySelector('#wl-color'),system=root.querySelector('#wl-system'),power=root.querySelector('#wl-power');
 var brands={'volkswagen':'Volkswagen','audi':'Audi','skoda':'Škoda','seat':'SEAT','cupra':'CUPRA','volkswagen-uzitkove-vozy':'Volkswagen Užitkové vozy'};
 var requestedBrand=new URLSearchParams(window.location.search).get('znacka');
 var selectedBrand=Object.prototype.hasOwnProperty.call(brands,requestedBrand)?requestedBrand:'';
 var context=root.querySelector('#wl-brand-context');
 var results=root.querySelector('#prehled-kontrolek');
 root.querySelector('#wl-results-title').textContent=selectedBrand?brands[selectedBrand]+' – obrazový přehled':'Obrazový přehled kontrolek';
 if(selectedBrand){
  context.hidden=false;
  var title=document.createElement('strong');title.textContent='Předvolená značka: '+brands[selectedBrand];context.appendChild(title);
  var note=document.createElement('p');note.textContent=selectedBrand==='volkswagen'?'Zobrazené příklady vycházejí z přehledu Volkswagen UK. Nejde o potvrzení platnosti pro každý model a rok výroby.':'Pro značku '+brands[selectedBrand]+' zatím nemáme v tomto náhledu ověřené obrazové položky. Kontrolky z přehledu Volkswagen pro tuto značku automaticky nepřebíráme. Respektujte hlášení a návod konkrétního vozidla.';context.appendChild(note);
  var clear=document.createElement('a');clear.href='./#prehled-kontrolek';clear.textContent='Zobrazit všechny dosud doložené příklady';context.appendChild(clear);
 }
 function normalize(text){return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
 function filter(){
  var words=normalize(search.value).split(/\s+/).filter(Boolean),count=0;
  cards.forEach(function(card){var hay=normalize(card.getAttribute('data-search'));var show=words.every(function(word){return hay.indexOf(word)!==-1;})&&(!color.value||card.dataset.color===color.value)&&(!system.value||card.dataset.system===system.value)&&(!power.value||card.dataset.power===power.value)&&(!selectedBrand||card.dataset.brand===selectedBrand);card.hidden=!show;if(show)count++;});
  groups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  var available=cards.filter(function(card){return !selectedBrand||card.dataset.brand===selectedBrand;}).length;
  root.querySelector('#wl-count').textContent='Zobrazeno '+count+' z '+available+' doložených položek.';
  root.querySelector('#wl-empty').textContent=selectedBrand&&selectedBrand!=='volkswagen'?'Pro značku '+brands[selectedBrand]+' zatím nejsou v tomto náhledu ověřené obrazové položky. Příklady Volkswagen pro tuto značku automaticky nepřebíráme. Rozhoduje hlášení a návod vašeho vozu.':'Pro zvolenou kombinaci nejsou v tomto náhledu doložené položky. Neznamená to, že daný vůz takovou kontrolku nemá.';
  root.querySelector('#wl-empty').hidden=count!==0;
 }
 filter();form.hidden=false;form.addEventListener('submit',function(event){event.preventDefault();});form.addEventListener('input',filter);form.addEventListener('change',filter);form.addEventListener('reset',function(){window.setTimeout(filter,0);});
 // Resolve anchors after filtering and after font/image layout settles. The
 // shared header is read for an offset, never changed by this component.
 var userMoved=false;
 ['wheel','touchstart','pointerdown','keydown'].forEach(function(type){window.addEventListener(type,function(){userMoved=true;},{passive:true});});
 function headerOffset(){
  var offset=12;
  Array.prototype.forEach.call(document.querySelectorAll('header.header, .isStuck, [data-sticky-header]'),function(header){
   var style=window.getComputedStyle(header),box=header.getBoundingClientRect();
   if((style.position==='fixed'||style.position==='sticky')&&box.height>0&&box.top<=1&&box.bottom>0)offset=Math.max(offset,box.bottom+12);
  });
  return offset;
 }
 function revealHash(){
  var id;try{id=decodeURIComponent(location.hash.slice(1));}catch(error){return;}
  var target=document.getElementById(id);if(!target||!root.contains(target))return;
  if(id!=='prehled-kontrolek'){form.reset();filter();}
  if(target.closest('[hidden]'))target=results;
  if(target.tagName==='DETAILS')target.open=true;
  window.requestAnimationFrame(function(){
   var offset=headerOffset();results.style.setProperty('--wl-anchor-offset',offset+'px');
   window.scrollTo(0,Math.max(0,window.scrollY+target.getBoundingClientRect().top-offset));
   (target===results?root.querySelector('#wl-results-title'):target).focus({preventScroll:true});
  });
 }
 window.addEventListener('hashchange',function(){userMoved=false;revealHash();});
 if(location.hash){
  revealHash();
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){if(!userMoved)revealHash();});
  if(document.readyState!=='complete')window.addEventListener('load',function(){if(!userMoved)revealHash();},{once:true});
 }
})();
