(function(){
 'use strict';
 var top=document.getElementById('back-top');if(!top)return;
 function refresh(){top.style.display=window.scrollY>100?'block':'none';}
 window.addEventListener('scroll',refresh,{passive:true});refresh();
 var link=top.querySelector('a');if(link)link.addEventListener('click',function(e){e.preventDefault();window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});});
}());
