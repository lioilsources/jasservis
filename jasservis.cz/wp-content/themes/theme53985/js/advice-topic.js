(function(){
 'use strict';
 var root=document.querySelector('[data-advice-topic]');if(!root)return;
 var brands=['volkswagen','audi','skoda','seat','cupra','volkswagen-uzitkove-vozy'];
 function brand(){var b=new URLSearchParams(location.search).get('znacka');return root.dataset.warningBrand||(brands.indexOf(b)>=0?b:'');}
 function render(){var b=brand();root.querySelectorAll('.wl-brand,[data-brand-only],.online-brand-panel,.vin-brand-panel').forEach(function(e){var own=e.dataset.brand||e.dataset.brandOnly||e.dataset.onlinePanel||e.dataset.vinPanel;e.hidden=!!(b&&own!==b);});root.querySelectorAll('.advice-brand-link').forEach(function(a){a.setAttribute('aria-current',a.dataset.brand===b?'true':'false');});document.querySelectorAll('.guide-article a[href],.language-switcher a[href]').forEach(function(a){if(!a.classList.contains('advice-brand-link')&&!a.getAttribute('href').match(/^(https?:|mailto:|tel:|#)/)){var u=new URL(a.href),path=a.getAttribute('href').split(/[?#]/)[0];if(b)u.searchParams.set('znacka',b);a.setAttribute('href',path+u.search+u.hash);}});}
 root.querySelectorAll('.advice-brand-link').forEach(function(a){a.addEventListener('click',function(e){if(root.dataset.warningBrand)return;e.preventDefault();var u=new URL(location.href);u.searchParams.set('znacka',a.dataset.brand);history.pushState(null,'',u.pathname+u.search+u.hash);render();});});
 function reveal(){var id;try{id=decodeURIComponent(location.hash.slice(1));}catch(e){return;}var target=document.getElementById(id);if(!target||!root.contains(target))return;for(var e=target;e&&root.contains(e);e=e.parentElement){if(e.tagName==='DETAILS')e.open=true;}requestAnimationFrame(function(){target.scrollIntoView({block:'start'});});}
 window.addEventListener('popstate',function(){render();reveal();});window.addEventListener('hashchange',reveal);render();reveal();
}());
