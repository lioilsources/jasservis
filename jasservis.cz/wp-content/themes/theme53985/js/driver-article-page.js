(function(){
 'use strict';
 var article=document.querySelector('[data-guide-article]');
 var brands=['volkswagen','audi','skoda','seat','cupra','volkswagen-uzitkove-vozy'];
 function valid(brand){return brands.indexOf(brand)!==-1?brand:'';}
 function carryBrand(link,brand){var path=link.getAttribute('href').split(/[?#]/)[0],url=new URL(link.getAttribute('href'),location.href);if(brand)url.searchParams.set('znacka',brand);else url.searchParams.delete('znacka');link.setAttribute('href',path+url.search+url.hash);}
 if(!article){
  var overview=document.getElementById('warning-lights');if(!overview)return;
  function updateOverviewLinks(){var brand=valid(new URLSearchParams(location.search).get('znacka'));Array.from(overview.querySelectorAll('.driver-article-more a')).forEach(function(link){carryBrand(link,brand);});}
  overview.addEventListener('click',function(event){var link=event.target.closest('a');if(link&&link.closest('.driver-article-more'))carryBrand(link,valid(new URLSearchParams(location.search).get('znacka')));});
  overview.addEventListener('click',function(){queueMicrotask(updateOverviewLinks);});
  window.addEventListener('popstate',updateOverviewLinks);updateOverviewLinks();return;
 }
 var variants=Array.from(article.querySelectorAll('[data-advice-brands]'));
 var buttons=Array.from(article.querySelectorAll('[data-guide-brand]'));
 var contextual=Array.from(document.querySelectorAll('.language-switcher a, .guide-article a[href]')).filter(function(link){var path=new URL(link.getAttribute('href'),location.href).pathname;return path.indexOf('/rady-pro-ridice/')!==-1||path.indexOf('/kontrolky-a-vystrazna-hlaseni/')!==-1;});
 var selected='';
 function render(){
  variants.forEach(function(item){item.hidden=selected?item.dataset.adviceBrands.split(' ').indexOf(selected)===-1:!item.hasAttribute('data-advice-fallback');});
  buttons.forEach(function(button){button.setAttribute('aria-pressed',String(button.dataset.guideBrand===selected));});
  contextual.forEach(function(link){carryBrand(link,selected);});
 }
 function select(brand,push){selected=valid(brand);var url=new URL(location.href);if(selected)url.searchParams.set('znacka',selected);else url.searchParams.delete('znacka');history[push?'pushState':'replaceState'](null,'',url.pathname+url.search+url.hash);render();}
 buttons.forEach(function(button){button.addEventListener('click',function(){select(button.dataset.guideBrand,true);});});
 window.addEventListener('popstate',function(){selected=valid(new URLSearchParams(location.search).get('znacka'));render();});
 selected=valid(new URLSearchParams(location.search).get('znacka'));render();
})();
