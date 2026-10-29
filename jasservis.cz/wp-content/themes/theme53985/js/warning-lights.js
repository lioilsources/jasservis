(function(){
 'use strict';
 var root=document.getElementById('warning-lights');if(!root)return;
 var form=root.querySelector('.wl-filters'),cards=Array.prototype.slice.call(root.querySelectorAll('.wl-card')),groups=Array.prototype.slice.call(root.querySelectorAll('.wl-group'));
 var search=root.querySelector('#wl-search'),color=root.querySelector('#wl-color'),system=root.querySelector('#wl-system'),power=root.querySelector('#wl-power');
 function normalize(text){return text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();}
 function filter(){
  var words=normalize(search.value).split(/\s+/).filter(Boolean),count=0;
  cards.forEach(function(card){var hay=normalize(card.getAttribute('data-search'));var show=words.every(function(word){return hay.indexOf(word)!==-1;})&&(!color.value||card.dataset.color===color.value)&&(!system.value||card.dataset.system===system.value)&&(!power.value||card.dataset.power===power.value);card.hidden=!show;if(show)count++;});
  groups.forEach(function(group){group.hidden=!group.querySelector('.wl-card:not([hidden])');});
  root.querySelector('#wl-count').textContent='Zobrazeno '+count+' z '+cards.length+' položek.';
  root.querySelector('#wl-empty').hidden=count!==0;
 }
 form.hidden=false;form.addEventListener('submit',function(event){event.preventDefault();});form.addEventListener('input',filter);form.addEventListener('change',filter);form.addEventListener('reset',function(){window.setTimeout(filter,0);});
 // Cross-links reveal the requested lighting group even after filtering.
 function revealHash(){var target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!target||!root.contains(target))return;form.reset();filter();if(target.tagName==='DETAILS')target.open=true;window.requestAnimationFrame(function(){target.scrollIntoView({block:'start'});});}
 window.addEventListener('hashchange',revealHash);if(location.hash)revealHash();
})();
