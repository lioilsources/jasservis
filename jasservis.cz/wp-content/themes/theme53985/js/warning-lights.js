(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var form=root.querySelector('.wl-filters'),cards=Array.prototype.slice.call(root.querySelectorAll('.wl-card')),groups=Array.prototype.slice.call(root.querySelectorAll('.wl-group'));
 var search=root.querySelector('#wl-search'),color=root.querySelector('#wl-color'),system=root.querySelector('#wl-system'),power=root.querySelector('#wl-power');
 var brands={'volkswagen':'Volkswagen','audi':'Audi','skoda':'Škoda','seat':'SEAT','cupra':'CUPRA','volkswagen-uzitkove-vozy':'Volkswagen Užitkové vozy'};
 var requestedBrand=new URLSearchParams(window.location.search).get('znacka');
 var selectedBrand=Object.prototype.hasOwnProperty.call(brands,requestedBrand)?requestedBrand:'';
 var context=root.querySelector('#wl-brand-context');
 if(selectedBrand){
  context.hidden=false;
  var title=document.createElement('strong');title.textContent='Předvolená značka: '+brands[selectedBrand];context.appendChild(title);
  var note=document.createElement('p');note.textContent=selectedBrand==='volkswagen'?'Zobrazené příklady vycházejí z přehledu Volkswagen UK. Nejde o potvrzení platnosti pro každý model a rok výroby.':'Pro značku '+brands[selectedBrand]+' zatím nemáme v tomto náhledu ověřené obrazové položky. Kontrolky z přehledu Volkswagen pro tuto značku automaticky nepřebíráme. Respektujte hlášení a návod konkrétního vozidla.';context.appendChild(note);
  var clear=document.createElement('a');clear.href=window.location.pathname;clear.textContent='Zobrazit všechny dosud doložené příklady';context.appendChild(clear);
 }
 function normalize(text){return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
 function filter(){
  var words=normalize(search.value).split(/\s+/).filter(Boolean),count=0;
  cards.forEach(function(card){var hay=normalize(card.getAttribute('data-search'));var show=words.every(function(word){return hay.indexOf(word)!==-1;})&&(!color.value||card.dataset.color===color.value)&&(!system.value||card.dataset.system===system.value)&&(!power.value||card.dataset.power===power.value)&&(!selectedBrand||card.dataset.brand===selectedBrand);card.hidden=!show;if(show)count++;});
  groups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  root.querySelector('#wl-count').textContent='Zobrazeno '+count+' z '+cards.length+' položek.';
  root.querySelector('#wl-empty').hidden=count!==0;
 }
 filter();form.hidden=false;form.addEventListener('submit',function(event){event.preventDefault();});form.addEventListener('input',filter);form.addEventListener('change',filter);form.addEventListener('reset',function(){window.setTimeout(filter,0);});
 // Cross-links reveal the requested lighting group even after filtering.
 function revealHash(){var target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!target||!root.contains(target))return;form.reset();filter();if(target.tagName==='DETAILS')target.open=true;window.requestAnimationFrame(function(){target.scrollIntoView({block:'start'});});}
 window.addEventListener('hashchange',revealHash);if(location.hash)revealHash();
})();
