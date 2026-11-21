const toggle = document.querySelector('.menu-toggle');
const mobileNav = document.getElementById('mobile-nav');
function closeMenu({restoreFocus=false}={}) {
  const wasOpen=toggle.getAttribute('aria-expanded')==='true';
  toggle.setAttribute('aria-expanded','false');
  mobileNav.hidden=true;
  mobileNav.querySelectorAll('details[open]').forEach(d=>d.open=false);
  if(restoreFocus&&wasOpen) toggle.focus();
}
toggle.addEventListener('click',()=>{
  const opening=toggle.getAttribute('aria-expanded')!=='true';
  toggle.setAttribute('aria-expanded',String(opening));mobileNav.hidden=!opening;
});
mobileNav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>closeMenu()));
document.querySelectorAll('.desktop-nav details a,.language-options a').forEach(a=>a.addEventListener('click',()=>a.closest('details').open=false));
document.addEventListener('keydown',e=>{
  if(e.key!=='Escape')return;
  const active=document.activeElement;
  document.querySelectorAll('details[open]').forEach(d=>{
    if(d.contains(active))d.querySelector('summary').focus();
    d.open=false;
  });
  closeMenu({restoreFocus:true});
});
document.addEventListener('click',e=>{
  document.querySelectorAll('.desktop-nav details[open],.languages[open]').forEach(d=>{if(!d.contains(e.target))d.open=false;});
});
window.addEventListener('resize',()=>{
  if(toggle.getAttribute('aria-expanded')==='true'&&!toggle.getClientRects().length)closeMenu();
});
const copyMessages={cs:'Číslo zkopírováno.',en:'Number copied.',de:'Nummer kopiert.',uk:'Номер скопійовано.',vi:'Đã sao chép số.'};
document.querySelectorAll('[data-copy-number]').forEach(button=>{
  if(!navigator.clipboard)return;
  button.hidden=false;
  button.addEventListener('click',async()=>{
    const status=button.closest('section')?.querySelector('[role="status"]');
    try{await navigator.clipboard.writeText(button.dataset.copyNumber);if(status)status.textContent=copyMessages[document.documentElement.lang]||copyMessages.cs;}
    catch{if(status)status.textContent=button.dataset.copyNumber;}
  });
});
function syncAdviceLanguageLinks(){
  const selected=new URLSearchParams(location.search).get('znacka');
  const valid=['volkswagen','audi','skoda','seat','cupra','volkswagen-uzitkove-vozy'].includes(selected);
  document.querySelectorAll('.language-options a').forEach(a=>{const path=a.getAttribute('href').split(/[?#]/)[0];const u=new URL(a.href);if(valid)u.searchParams.set('znacka',selected);else u.searchParams.delete('znacka');a.setAttribute('href',path+u.search+u.hash);});
}
syncAdviceLanguageLinks();
window.addEventListener('popstate',syncAdviceLanguageLinks);
document.addEventListener('click',event=>{if(event.target.closest('[data-guide-brand],.advice-brand-link'))queueMicrotask(syncAdviceLanguageLinks);});
