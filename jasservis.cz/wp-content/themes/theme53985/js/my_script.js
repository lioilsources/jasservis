$(document).ready(function(){

var 
  fullWidth = $('.full_width')
, direction = $('body').css("direction")
, _window = $(window)
;


$('.full_width').css('display', 'block');

$(window).resize(
   function(){
      mainResizer();
   }
).trigger('resize');


function mainResizer(){
  if(direction == "ltr"){
    fullWidth.css({width: _window.width(), "margin-left": (_window.width()/-2),"left":"50%"});
  }else{
    fullWidth.css({width: _window.width(), "margin-right": (_window.width()/-2),"right":"50%"});
  }
}

});