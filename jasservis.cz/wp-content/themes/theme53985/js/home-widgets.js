/* Unused home initializer omitted; original retained: wp-content/plugins/cherry-plugin/includes/js/cherry-plugin.js */
;

/* wp-content/plugins/cherry-lazy-load/js/cherry.lazy-load.js */
CherryLazyLoadPlugin = new (function($){
	var effects = ['effect-slideup', 'effect-slidedown', 'effect-slidefromleft', 'effect-slidefromright', 'effect-zoomin', 'effect-zoomout', 'effect-rotate', 'effect-skew']
	/* Can be set programatically later instead of adding a tag class to the DOM */
	this.useCSSAnimations = jQuery('.cssanimations').length;
	/* Default delay */
	this.defaultDelay = undefined;
	/* Default speed */
	this.defaultSpeed = undefined;

	var that = this;
	function getWindowHeight() {
		var myWidth = 0, myHeight = 0;
		if( typeof( window.innerWidth ) == 'number' ) {
			//Non-IE
			myHeight = window.innerHeight;
		} else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
			//IE 6+ in 'standards compliant mode'
			myHeight = document.documentElement.clientHeight;
		} else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
			//IE 4 compatible
			myHeight = document.body.clientHeight;
		}

		return myHeight
	};

	function appearBox(element, element_top, bottom_of_window) {
		/* If the object is completely visible in the window, fade it it */
		var buffer = $(element).outerHeight()/2;
		if( bottom_of_window > element_top + buffer) {
			setTimeout(function(){
				if ( that.useCSSAnimations ) {
					element.removeClass('trigger');
				} else {
					element.removeClass('trigger').animate({'opacity':'1'}, element.data('speed') !== undefined? element.data('speed') : that.defaultSpeed);
				}
			}, element.data('delay') !== undefined? element.data('delay') : that.defaultDelay);
		}
	};

	function registerAnimation(element, effect, delay, speed) {
		var effect = effect || 'random'
		if(effect == 'random'){
			effect = effects[Math.floor(Math.random()*effects.length)];
		}
		$(element).addClass('lazy-load-box').addClass('trigger').addClass(effect);

		if(delay !== undefined)
			$(element).attr('data-delay', delay)

		if(speed !== undefined)
			$(element).attr('data-speed', speed)
	};
	this.registerAnimation = registerAnimation;
	$.fn.cherryLazyLoad = function(effect, delay, speed){
		/* Add a quick jQuery hook. Register each element individually, especially for `random` effect. */
		$(this).each(function(){
			registerAnimation(this, effect, delay, speed);
		})
	};

	$(window).load(function() {
		if(!device.mobile() && !device.tablet()){
			$('.lazy-load-box.trigger').each( function(i){
				var element_offset = $(this).offset();
				var element_top = element_offset.top;
				var bottom_of_window = $(window).scrollTop() + getWindowHeight();
				appearBox($(this), element_top, bottom_of_window);
			});

			/* Every time the window is scrolled ... */
			$(window).scroll( function() {
				/* Check the location of each desired element */
				$('.lazy-load-box.trigger').each( function(i){
					var element_offset = $(this).offset(),
						element_top = element_offset.top,
						bottom_of_window = $(window).scrollTop() + getWindowHeight();

					appearBox($(this), element_top, bottom_of_window);
				});

			});
		} else {
			$('.lazy-load-box').each( function(i) {
				$(this).removeClass('trigger').css('opacity', '1');
			});
		}
	});
})(jQuery); /* Initialize with old defaults */
;

/* wp-content/plugins/cherry-lazy-load/js/device.min.js */
/*! device.js 0.2.0 */
(function(){var a,b,c,d,e,f,g,h,i,j;b=window.device,a={},window.device=a,d=window.document.documentElement,j=window.navigator.userAgent.toLowerCase(),a.ios=function(){return a.iphone()||a.ipod()||a.ipad()},a.iphone=function(){return e("iphone")},a.ipod=function(){return e("ipod")},a.ipad=function(){return e("ipad")},a.android=function(){return e("android")},a.androidPhone=function(){return a.android()&&e("mobile")},a.androidTablet=function(){return a.android()&&!e("mobile")},a.blackberry=function(){return e("blackberry")||e("bb10")||e("rim")},a.blackberryPhone=function(){return a.blackberry()&&!e("tablet")},a.blackberryTablet=function(){return a.blackberry()&&e("tablet")},a.windows=function(){return e("windows")},a.windowsPhone=function(){return a.windows()&&e("phone")},a.windowsTablet=function(){return a.windows()&&e("touch")&&!a.windowsPhone()},a.fxos=function(){return(e("(mobile;")||e("(tablet;"))&&e("; rv:")},a.fxosPhone=function(){return a.fxos()&&e("mobile")},a.fxosTablet=function(){return a.fxos()&&e("tablet")},a.meego=function(){return e("meego")},a.cordova=function(){return window.cordova&&"file:"===location.protocol},a.nodeWebkit=function(){return"object"==typeof window.process},a.mobile=function(){return a.androidPhone()||a.iphone()||a.ipod()||a.windowsPhone()||a.blackberryPhone()||a.fxosPhone()||a.meego()},a.tablet=function(){return a.ipad()||a.androidTablet()||a.blackberryTablet()||a.windowsTablet()||a.fxosTablet()},a.desktop=function(){return!a.tablet()&&!a.mobile()},a.portrait=function(){return window.innerHeight/window.innerWidth>1},a.landscape=function(){return window.innerHeight/window.innerWidth<1},a.noConflict=function(){return window.device=b,this},e=function(a){return-1!==j.indexOf(a)},g=function(a){var b;return b=new RegExp(a,"i"),d.className.match(b)},c=function(a){g(a)||(d.className+=" "+a)},i=function(a){g(a)&&(d.className=d.className.replace(" "+a,""))},a.ios()?a.ipad()?c("ios ipad tablet"):a.iphone()?c("ios iphone mobile"):a.ipod()&&c("ios ipod mobile"):c(a.android()?a.androidTablet()?"android tablet":"android mobile":a.blackberry()?a.blackberryTablet()?"blackberry tablet":"blackberry mobile":a.windows()?a.windowsTablet()?"windows tablet":a.windowsPhone()?"windows mobile":"desktop":a.fxos()?a.fxosTablet()?"fxos tablet":"fxos mobile":a.meego()?"meego mobile":a.nodeWebkit()?"node-webkit":"desktop"),a.cordova()&&c("cordova"),f=function(){a.landscape()?(i("portrait"),c("landscape")):(i("landscape"),c("portrait"))},h=window.hasOwnProperty("onorientationchange")?"orientationchange":"resize",window.addEventListener?window.addEventListener(h,f,!1):window.attachEvent?window.attachEvent(h,f):window[h]=f,f(),"function"==typeof define&&"object"==typeof define.amd&&define.amd?define(function(){return a}):"undefined"!=typeof module&&module.exports?module.exports=a:window.device=a}).call(this);
;

/* wp-content/plugins/cherry-parallax/js/jquery.mousewheel.min.js */
/*! Copyright (c) 2011 Brandon Aaron (http://brandonaaron.net)
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Thanks to: http://adomas.org/javascript-mouse-wheel/ for some pointers.
 * Thanks to: Mathias Bank(http://www.mathias-bank.de) for a scope bug fix.
 * Thanks to: Seamus Leahy for adding deltaX and deltaY
 *
 * Version: 3.0.6
 * 
 * Requires: 1.2.2+
 */
(function(a){function d(b){var c=b||window.event,d=[].slice.call(arguments,1),e=0,f=!0,g=0,h=0;return b=a.event.fix(c),b.type="mousewheel",c.wheelDelta&&(e=c.wheelDelta/120),c.detail&&(e=-c.detail/3),h=e,c.axis!==undefined&&c.axis===c.HORIZONTAL_AXIS&&(h=0,g=-1*e),c.wheelDeltaY!==undefined&&(h=c.wheelDeltaY/120),c.wheelDeltaX!==undefined&&(g=-1*c.wheelDeltaX/120),d.unshift(b,e,g,h),(a.event.dispatch||a.event.handle).apply(this,d)}var b=["DOMMouseScroll","mousewheel"];if(a.event.fixHooks)for(var c=b.length;c;)a.event.fixHooks[b[--c]]=a.event.mouseHooks;a.event.special.mousewheel={setup:function(){if(this.addEventListener)for(var a=b.length;a;)this.addEventListener(b[--a],d,!1);else this.onmousewheel=d},teardown:function(){if(this.removeEventListener)for(var a=b.length;a;)this.removeEventListener(b[--a],d,!1);else this.onmousewheel=null}},a.fn.extend({mousewheel:function(a){return a?this.bind("mousewheel",a):this.trigger("mousewheel")},unmousewheel:function(a){return this.unbind("mousewheel",a)}})})(jQuery)

;

/* wp-content/plugins/cherry-parallax/js/jquery.simplr.smoothscroll.min.js */
/* jquery.simplr.smoothscroll version 1.0 copyright (c) 2012 https://github.com/simov/simplr-smoothscroll licensed under MIT */

jQuery(document).ready(function($) {
    if(!device.mobile() && !device.tablet()){
        $.srSmoothscroll({
            step:150,
            speed:800
        });
    }
});

;(function(e){"use strict";e.srSmoothscroll=function(t){var platform = window.navigator.platform; if ((platform === 'MacIntel' || platform === 'MacPPC')){return false}; var n=e.extend({step:170,speed:1000,ease:"swing"},t||{});var r=e(window),i=e(document),s=0,o=n.step,u=n.speed,a=r.height(),f=navigator.userAgent.indexOf("AppleWebKit")!==-1?e("body"):e("html"),l=false;e("body").mousewheel(function(e,t){l=true;if(t<0)s=s+a>=i.height()?s:s+=o;else s=s<=0?0:s-=o;f.stop().animate({scrollTop:s},u,n.ease,function(){l=false});return false});r.on("resize",function(e){a=r.height()}).on("scroll",function(e){if(!l)s=r.scrollTop()})}})(jQuery);

;

/* wp-content/plugins/cherry-parallax/js/cherry.parallax.js */
jQuery(document).ready(function($){
    
    parallax_box = $('section.parallax-box');
    if(parallax_box.length > 0){
        ParallaxBox();
    }
    
    function ParallaxBox()
    {
        var windowSelector = $(window),
            documentSelector = $(document),
            documentWidth = documentSelector.width(),
            windowHeight = windowSelector.outerHeight(),
            liteMode = false,
            ieVersion = getInternetExplorerVersion();
            
        var ds = document.documentElement;
            
        if(!device.mobile() && !device.tablet()){
			liteMode = false;
            
            if (ieVersion !=-1 && ieVersion < 9){
                liteMode = true;
            }
		}else{
			liteMode = true;
		}
        
        parallax_box.each(function()
        {
           parallaxBox($(this));
        });
        
        function parallaxBox(obj){
            
            var obj_bg = obj.find('.parallax-bg'),
                type = obj_bg.data('parallax-type'),
                obj_bg_inner,
                img,
                originalWidth = 0,
                originalHeight = 0,
                img_url = obj_bg.data('img-url'),
                bufferRatio = obj_bg.data('speed'),
                parallaxInvert = obj_bg.data('invert'),
                parallaxType = 'parallax_normal',
                objHeight = obj.height(),
                objOffsetTop = obj.offset().top,
                baseHeight = 0,
                parallax = true;
                notResize = false;
            
            switch (type) {
                case 'image':
                    loadImg(); 
                    
                    break
                    
                case 'video':
                    obj_bg_inner = $('.parallax_media', obj_bg);
                    
                    if(liteMode) {
                        obj_bg_inner.remove();
                        loadImg();   
                    } else {
                        loadVideo();
                    }
                    
                    break
            }
            
            function loadImg(){
                if(img_url){
                    img = new Image();
                    img.src = img_url;
                    
                    img.onload = function ()
                    {
                        originalWidth = img.width;
                        originalHeight = img.height;
                        
                        imgBlocksStructure = !liteMode ? "<div class='parallax-img parallax-bg-inner'></div>" : "<img class='parallax-img parallax-bg-inner' src='' alt=''/>";
                        obj_bg.append(imgBlocksStructure);
                        obj_bg_inner = $('.parallax-img', obj_bg);
                        
                        if(!liteMode){
                            obj_bg_inner.css('background-image', 'url(' + (img_url) + ')');
                        } else { 
                            obj_bg_inner.attr('src', img_url);
                            bufferRatio = 'none';
                        }
                        
                        initParallax();
                    }
                }
            }
            
            function loadVideo()
            {   
                var videoElement = obj_bg_inner.get(0);
                    
                videoElement.load();
                videoElement.play();
                
                originalWidth = videoElement.videoWidth;
                originalHeight = videoElement.videoHeight;
                    
                if(img_url){
                    img = new Image();
                    img.src = img_url;
                    
                    img.onload = function ()
                    {
                        originalWidth = originalWidth==0 ? img.width : originalWidth;
                        originalHeight = originalHeight==0 ? img.height : originalHeight;
                        objectResize(obj_bg_inner, documentWidth, baseHeight, originalWidth, originalHeight);
                    }
                }
                
                videoElement.onloadeddata = function()
                {
                    originalWidth = videoElement.videoWidth;
                    originalHeight = videoElement.videoHeight;
                    objectResize(obj_bg_inner, documentWidth, baseHeight, originalWidth, originalHeight);
                }
                
                initParallax();
            }
            
            function initParallax()
            {
                notResize = false;
                
                if(!parallaxInvert){
                    parallaxType = 'parallax_normal';
                } else {
                    parallaxType = 'parallax_invert';
                }
                
                switch (bufferRatio) {
                    case 'low':
                        bufferRatio = 3;
                        
                        break
                        
                    case 'normal':
                        bufferRatio = 2.25;
                        
                        break
                        
                    case 'hight':
                        bufferRatio = 1.5;
                        
                        break
                        
                    case 'fixed':
                        if(ieVersion != -1 || getSafari()){
                            if(type != 'video'){
                                parallax = false;
                                notResize = true;
                                obj_bg_inner.css({backgroundAttachment:'fixed', width:'100%', height:'100%'});
                            } else {
                                parallaxType = 'parallax_normal';
                                bufferRatio = 2.25;
                            }
                        } else {
                            parallaxType = 'parallax_fixes';
                            bufferRatio = 1;
                        }
                        
                        break
                        
                    case 'none':
                        parallax = false;
                        parallaxType = 'parallax_none';
                        
                        break
                        
                    default:
                        bufferRatio = 2.25;
                        
                        if(bufferRatio > 5) bufferRatio = 5; 
                        if(bufferRatio <= 1) {
                            if($.browser.msie){
                                parallax = false;
                                obj_bg_inner.css({backgroundAttachment:'fixed'});
                            } else {
                                parallaxType = 'parallax_fixes';
                                bufferRatio = 1;
                            }
                        }
                    
                        break
                }          
                
                windowSelector.resize(parallaxObjResize);
                parallaxObjResize();
                
                if(!liteMode) windowSelector.scroll(parallaxMove);
            }
            
            function parallaxObjResize()
            {
                documentWidth = documentSelector.width();
                windowHeight = windowSelector.outerHeight();
            
                objHeight = obj.height();
                
                obj_bg.width(documentWidth);
                obj_bg.css({'width' : documentWidth, 'margin-left' : Math.floor(documentWidth*-0.5), 'left' : '50%'});
                               
                if(!notResize){                
                    baseHeight = getBaseHeight(parallaxType, objHeight, bufferRatio);
                    objectResize(obj_bg_inner, documentWidth, baseHeight, originalWidth, originalHeight);
                }                
                
                if(!liteMode) parallaxMove();
            }
            function parallaxMove()
            {
                if(parallax && !liteMode){
                    
                     var documentScrollTop,
                         startScrollTop,
                         endScrollTop;
         
                     objOffsetTop = obj.offset().top;
                     documentScrollTop = documentSelector.scrollTop();
         
                     startScrollTop = documentScrollTop + windowHeight;
                     endScrollTop = documentScrollTop - objHeight;
         
                     if((startScrollTop > objOffsetTop) && (endScrollTop < objOffsetTop)){  
                         
                         y = documentScrollTop - objOffsetTop;
                         
                         if(!parallaxInvert) {
                             newPositionTop =  parseInt(y / bufferRatio);
                         } else {
                             newPositionTop = -parseInt(y / bufferRatio) - parseInt(windowHeight / bufferRatio)
                         }
        
                         obj_bg_inner.css({ top: newPositionTop + 'px' });  
                     }
                 } 
            }
        }
        
        function objectResize(obj, baseWidth, baseHeight, originalWidth, originalHeight )
        {
            var imageRatio,
                originalWidth,
                originalHeight,
                newImgWidth,
                newImgHeight,
                newImgTop,
                newImgLeft;
    
            imageRatio = originalHeight/originalWidth;
            containerRatio = baseHeight/baseWidth;
    
            if(containerRatio > imageRatio){
                newImgHeight = baseHeight;
                newImgWidth = Math.round( (newImgHeight*originalWidth) / originalHeight );   
            }else{
                newImgWidth = baseWidth;
                newImgHeight = Math.round( (newImgWidth*originalHeight) / originalWidth );
            }
    
            newImgLeft=-(newImgWidth-baseWidth)*.5;
            newImgTop= -(newImgHeight-baseHeight)*.5;
            
            obj.css({width: newImgWidth, height: newImgHeight, marginTop: newImgTop, marginLeft: newImgLeft});
        }
        
        function getBaseHeight(parallaxType, objHeight, bufferRatio)
        {
            var newBaseHeight = 0;
            
            switch (parallaxType) {
                case 'parallax_normal':
                    newBaseHeight = objHeight + parseInt((windowHeight - objHeight)/bufferRatio);             
                    break
                    
                case 'parallax_invert':
                    newBaseHeight = objHeight + parseInt((windowHeight + objHeight)/bufferRatio);
                    break
                    
                case 'parallax_fixes':
                    newBaseHeight = windowHeight;
                    break
                    
                case 'parallax_none':
                    newBaseHeight = objHeight;
                    break
            }
            
            return newBaseHeight;
        }
        
        function getInternetExplorerVersion()
        {                        
            var rv = -1;
            if (navigator.appName == 'Microsoft Internet Explorer')
            {
                var ua = navigator.userAgent;
                var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
                if (re.exec(ua) != null)
                    rv = parseFloat( RegExp.$1 );
            }
            else if (navigator.appName == 'Netscape')
            {
                var ua = navigator.userAgent;
                var re  = new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})");
                                
                if (re.exec(ua) != null)
                    rv = parseFloat( RegExp.$1 );                                      
            }
            
            return rv;
        }
        function getSafari(){
            var safari = false;
            if (navigator.userAgent.search("Safari") >= 0 && navigator.userAgent.search("Chrome") < 0) safari = true;
            return  safari;       
        }
    }
    
});
;

/* wp-content/themes/CherryFramework/js/jquery.magnific-popup.min.js */
/*! Magnific Popup - v0.9.3 - 2013-07-16
* http://dimsemenov.com/plugins/magnific-popup/
* Copyright (c) 2013 Dmitry Semenov; */
(function(e){var t,i,n,o,a,r,s,l="Close",c="BeforeClose",d="AfterClose",u="BeforeAppend",p="MarkupParse",f="Open",m="Change",g="mfp",v="."+g,h="mfp-ready",C="mfp-removing",y="mfp-prevent-close",w=function(){},b=!!window.jQuery,I=e(window),x=function(e,i){t.ev.on(g+e+v,i)},k=function(t,i,n,o){var a=document.createElement("div");return a.className="mfp-"+t,n&&(a.innerHTML=n),o?i&&i.appendChild(a):(a=e(a),i&&a.appendTo(i)),a},T=function(i,n){t.ev.triggerHandler(g+i,n),t.st.callbacks&&(i=i.charAt(0).toLowerCase()+i.slice(1),t.st.callbacks[i]&&t.st.callbacks[i].apply(t,e.isArray(n)?n:[n]))},E=function(){(t.st.focus?t.content.find(t.st.focus).eq(0):t.wrap).trigger("focus")},S=function(i){return i===s&&t.currTemplate.closeBtn||(t.currTemplate.closeBtn=e(t.st.closeMarkup.replace("%title%",t.st.tClose)),s=i),t.currTemplate.closeBtn},P=function(){e.magnificPopup.instance||(t=new w,t.init(),e.magnificPopup.instance=t)},_=function(i){if(!e(i).hasClass(y)){var n=t.st.closeOnContentClick,o=t.st.closeOnBgClick;if(n&&o)return!0;if(!t.content||e(i).hasClass("mfp-close")||t.preloader&&i===t.preloader[0])return!0;if(i===t.content[0]||e.contains(t.content[0],i)){if(n)return!0}else if(o&&e.contains(document,i))return!0;return!1}},O=function(){var e=document.createElement("p").style,t=["ms","O","Moz","Webkit"];if(void 0!==e.transition)return!0;for(;t.length;)if(t.pop()+"Transition"in e)return!0;return!1};w.prototype={constructor:w,init:function(){var i=navigator.appVersion;t.isIE7=-1!==i.indexOf("MSIE 7."),t.isIE8=-1!==i.indexOf("MSIE 8."),t.isLowIE=t.isIE7||t.isIE8,t.isAndroid=/android/gi.test(i),t.isIOS=/iphone|ipad|ipod/gi.test(i),t.supportsTransition=O(),t.probablyMobile=t.isAndroid||t.isIOS||/(Opera Mini)|Kindle|webOS|BlackBerry|(Opera Mobi)|(Windows Phone)|IEMobile/i.test(navigator.userAgent),n=e(document.body),o=e(document),t.popupsCache={}},open:function(i){var n;if(i.isObj===!1){t.items=i.items.toArray(),t.index=0;var a,s=i.items;for(n=0;s.length>n;n++)if(a=s[n],a.parsed&&(a=a.el[0]),a===i.el[0]){t.index=n;break}}else t.items=e.isArray(i.items)?i.items:[i.items],t.index=i.index||0;if(t.isOpen)return t.updateItemHTML(),void 0;t.types=[],r="",t.ev=i.mainEl&&i.mainEl.length?i.mainEl.eq(0):o,i.key?(t.popupsCache[i.key]||(t.popupsCache[i.key]={}),t.currTemplate=t.popupsCache[i.key]):t.currTemplate={},t.st=e.extend(!0,{},e.magnificPopup.defaults,i),t.fixedContentPos="auto"===t.st.fixedContentPos?!t.probablyMobile:t.st.fixedContentPos,t.st.modal&&(t.st.closeOnContentClick=!1,t.st.closeOnBgClick=!1,t.st.showCloseBtn=!1,t.st.enableEscapeKey=!1),t.bgOverlay||(t.bgOverlay=k("bg").on("click"+v,function(){t.close()}),t.wrap=k("wrap").attr("tabindex",-1).on("click"+v,function(e){_(e.target)&&t.close()}),t.container=k("container",t.wrap)),t.contentContainer=k("content"),t.st.preloader&&(t.preloader=k("preloader",t.container,t.st.tLoading));var l=e.magnificPopup.modules;for(n=0;l.length>n;n++){var c=l[n];c=c.charAt(0).toUpperCase()+c.slice(1),t["init"+c].call(t)}T("BeforeOpen"),t.st.showCloseBtn&&(t.st.closeBtnInside?(x(p,function(e,t,i,n){i.close_replaceWith=S(n.type)}),r+=" mfp-close-btn-in"):t.wrap.append(S())),t.st.alignTop&&(r+=" mfp-align-top"),t.fixedContentPos?t.wrap.css({overflow:t.st.overflowY,overflowX:"hidden",overflowY:t.st.overflowY}):t.wrap.css({top:I.scrollTop(),position:"absolute"}),(t.st.fixedBgPos===!1||"auto"===t.st.fixedBgPos&&!t.fixedContentPos)&&t.bgOverlay.css({height:o.height(),position:"absolute"}),t.st.enableEscapeKey&&o.on("keyup"+v,function(e){27===e.keyCode&&t.close()}),I.on("resize"+v,function(){t.updateSize()}),t.st.closeOnContentClick||(r+=" mfp-auto-cursor"),r&&t.wrap.addClass(r);var d=t.wH=I.height(),u={};if(t.fixedContentPos&&t._hasScrollBar(d)){var m=t._getScrollbarSize();m&&(u.paddingRight=m)}t.fixedContentPos&&(t.isIE7?e("body, html").css("overflow","hidden"):u.overflow="hidden");var g=t.st.mainClass;t.isIE7&&(g+=" mfp-ie7"),g&&t._addClassToMFP(g),t.updateItemHTML(),T("BuildControls"),e("html").css(u),t.bgOverlay.add(t.wrap).prependTo(document.body),t._lastFocusedEl=document.activeElement,setTimeout(function(){t.content?(t._addClassToMFP(h),E()):t.bgOverlay.addClass(h),o.on("focusin"+v,function(i){return i.target===t.wrap[0]||e.contains(t.wrap[0],i.target)?void 0:(E(),!1)})},16),t.isOpen=!0,t.updateSize(d),T(f)},close:function(){t.isOpen&&(T(c),t.isOpen=!1,t.st.removalDelay&&!t.isLowIE&&t.supportsTransition?(t._addClassToMFP(C),setTimeout(function(){t._close()},t.st.removalDelay)):t._close())},_close:function(){T(l);var i=C+" "+h+" ";if(t.bgOverlay.detach(),t.wrap.detach(),t.container.empty(),t.st.mainClass&&(i+=t.st.mainClass+" "),t._removeClassFromMFP(i),t.fixedContentPos){var n={paddingRight:""};t.isIE7?e("body, html").css("overflow",""):n.overflow="",e("html").css(n)}o.off("keyup"+v+" focusin"+v),t.ev.off(v),t.wrap.attr("class","mfp-wrap").removeAttr("style"),t.bgOverlay.attr("class","mfp-bg"),t.container.attr("class","mfp-container"),!t.st.showCloseBtn||t.st.closeBtnInside&&t.currTemplate[t.currItem.type]!==!0||t.currTemplate.closeBtn&&t.currTemplate.closeBtn.detach(),t._lastFocusedEl&&e(t._lastFocusedEl).trigger("focus"),t.currItem=null,t.content=null,t.currTemplate=null,t.prevHeight=0,T(d)},updateSize:function(e){if(t.isIOS){var i=document.documentElement.clientWidth/window.innerWidth,n=window.innerHeight*i;t.wrap.css("height",n),t.wH=n}else t.wH=e||I.height();t.fixedContentPos||t.wrap.css("height",t.wH),T("Resize")},updateItemHTML:function(){var i=t.items[t.index];t.contentContainer.detach(),t.content&&t.content.detach(),i.parsed||(i=t.parseEl(t.index));var n=i.type;if(T("BeforeChange",[t.currItem?t.currItem.type:"",n]),t.currItem=i,!t.currTemplate[n]){var o=t.st[n]?t.st[n].markup:!1;T("FirstMarkupParse",o),t.currTemplate[n]=o?e(o):!0}a&&a!==i.type&&t.container.removeClass("mfp-"+a+"-holder");var r=t["get"+n.charAt(0).toUpperCase()+n.slice(1)](i,t.currTemplate[n]);t.appendContent(r,n),i.preloaded=!0,T(m,i),a=i.type,t.container.prepend(t.contentContainer),T("AfterChange")},appendContent:function(e,i){t.content=e,e?t.st.showCloseBtn&&t.st.closeBtnInside&&t.currTemplate[i]===!0?t.content.find(".mfp-close").length||t.content.append(S()):t.content=e:t.content="",T(u),t.container.addClass("mfp-"+i+"-holder"),t.contentContainer.append(t.content)},parseEl:function(i){var n=t.items[i],o=n.type;if(n=n.tagName?{el:e(n)}:{data:n,src:n.src},n.el){for(var a=t.types,r=0;a.length>r;r++)if(n.el.hasClass("mfp-"+a[r])){o=a[r];break}n.src=n.el.attr("data-mfp-src"),n.src||(n.src=n.el.attr("href"))}return n.type=o||t.st.type||"inline",n.index=i,n.parsed=!0,t.items[i]=n,T("ElementParse",n),t.items[i]},addGroup:function(e,i){var n=function(n){n.mfpEl=this,t._openClick(n,e,i)};i||(i={});var o="click.magnificPopup";i.mainEl=e,i.items?(i.isObj=!0,e.off(o).on(o,n)):(i.isObj=!1,i.delegate?e.off(o).on(o,i.delegate,n):(i.items=e,e.off(o).on(o,n)))},_openClick:function(i,n,o){var a=void 0!==o.midClick?o.midClick:e.magnificPopup.defaults.midClick;if(a||2!==i.which&&!i.ctrlKey&&!i.metaKey){var r=void 0!==o.disableOn?o.disableOn:e.magnificPopup.defaults.disableOn;if(r)if(e.isFunction(r)){if(!r.call(t))return!0}else if(r>I.width())return!0;i.type&&(i.preventDefault(),t.isOpen&&i.stopPropagation()),o.el=e(i.mfpEl),o.delegate&&(o.items=n.find(o.delegate)),t.open(o)}},updateStatus:function(e,n){if(t.preloader){i!==e&&t.container.removeClass("mfp-s-"+i),n||"loading"!==e||(n=t.st.tLoading);var o={status:e,text:n};T("UpdateStatus",o),e=o.status,n=o.text,t.preloader.html(n),t.preloader.find("a").on("click",function(e){e.stopImmediatePropagation()}),t.container.addClass("mfp-s-"+e),i=e}},_addClassToMFP:function(e){t.bgOverlay.addClass(e),t.wrap.addClass(e)},_removeClassFromMFP:function(e){this.bgOverlay.removeClass(e),t.wrap.removeClass(e)},_hasScrollBar:function(e){return(t.isIE7?o.height():document.body.scrollHeight)>(e||I.height())},_parseMarkup:function(t,i,n){var o;n.data&&(i=e.extend(n.data,i)),T(p,[t,i,n]),e.each(i,function(e,i){if(void 0===i||i===!1)return!0;if(o=e.split("_"),o.length>1){var n=t.find(v+"-"+o[0]);if(n.length>0){var a=o[1];"replaceWith"===a?n[0]!==i[0]&&n.replaceWith(i):"img"===a?n.is("img")?n.attr("src",i):n.replaceWith('<img src="'+i+'" class="'+n.attr("class")+'" />'):n.attr(o[1],i)}}else t.find(v+"-"+e).html(i)})},_getScrollbarSize:function(){if(void 0===t.scrollbarSize){var e=document.createElement("div");e.id="mfp-sbm",e.style.cssText="width: 99px; height: 99px; overflow: scroll; position: absolute; top: -9999px;",document.body.appendChild(e),t.scrollbarSize=e.offsetWidth-e.clientWidth,document.body.removeChild(e)}return t.scrollbarSize}},e.magnificPopup={instance:null,proto:w.prototype,modules:[],open:function(e,t){return P(),e||(e={}),e.isObj=!0,e.index=t||0,this.instance.open(e)},close:function(){return e.magnificPopup.instance.close()},registerModule:function(t,i){i.options&&(e.magnificPopup.defaults[t]=i.options),e.extend(this.proto,i.proto),this.modules.push(t)},defaults:{disableOn:0,key:null,midClick:!1,mainClass:"",preloader:!0,focus:"",closeOnContentClick:!1,closeOnBgClick:!0,closeBtnInside:!0,showCloseBtn:!0,enableEscapeKey:!0,modal:!1,alignTop:!1,removalDelay:0,fixedContentPos:"auto",fixedBgPos:"auto",overflowY:"auto",closeMarkup:'<button title="%title%" type="button" class="mfp-close">&times;</button>',tClose:"Close (Esc)",tLoading:"Loading..."}},e.fn.magnificPopup=function(i){P();var n=e(this);if("string"==typeof i)if("open"===i){var o,a=b?n.data("magnificPopup"):n[0].magnificPopup,r=parseInt(arguments[1],10)||0;a.items?o=a.items[r]:(o=n,a.delegate&&(o=o.find(a.delegate)),o=o.eq(r)),t._openClick({mfpEl:o},n,a)}else t.isOpen&&t[i].apply(t,Array.prototype.slice.call(arguments,1));else b?n.data("magnificPopup",i):n[0].magnificPopup=i,t.addGroup(n,i);return n};var z,M,B,H="inline",L=function(){B&&(M.after(B.addClass(z)).detach(),B=null)};e.magnificPopup.registerModule(H,{options:{hiddenClass:"hide",markup:"",tNotFound:"Content not found"},proto:{initInline:function(){t.types.push(H),x(l+"."+H,function(){L()})},getInline:function(i,n){if(L(),i.src){var o=t.st.inline,a=e(i.src);if(a.length){var r=a[0].parentNode;r&&r.tagName&&(M||(z=o.hiddenClass,M=k(z),z="mfp-"+z),B=a.after(M).detach().removeClass(z)),t.updateStatus("ready")}else t.updateStatus("error",o.tNotFound),a=e("<div>");return i.inlineElement=a,a}return t.updateStatus("ready"),t._parseMarkup(n,{},i),n}}});var A,F="ajax",j=function(){A&&n.removeClass(A)};e.magnificPopup.registerModule(F,{options:{settings:null,cursor:"mfp-ajax-cur",tError:'<a href="%url%">The content</a> could not be loaded.'},proto:{initAjax:function(){t.types.push(F),A=t.st.ajax.cursor,x(l+"."+F,function(){j(),t.req&&t.req.abort()})},getAjax:function(i){A&&n.addClass(A),t.updateStatus("loading");var o=e.extend({url:i.src,success:function(n,o,a){var r={data:n,xhr:a};T("ParseAjax",r),t.appendContent(e(r.data),F),i.finished=!0,j(),E(),setTimeout(function(){t.wrap.addClass(h)},16),t.updateStatus("ready"),T("AjaxContentAdded")},error:function(){j(),i.finished=i.loadError=!0,t.updateStatus("error",t.st.ajax.tError.replace("%url%",i.src))}},t.st.ajax.settings);return t.req=e.ajax(o),""}}});var N,W=function(i){if(i.data&&void 0!==i.data.title)return i.data.title;var n=t.st.image.titleSrc;if(n){if(e.isFunction(n))return n.call(t,i);if(i.el)return i.el.attr(n)||""}return""};e.magnificPopup.registerModule("image",{options:{markup:'<div class="mfp-figure"><div class="mfp-close"></div><div class="mfp-img"></div><div class="mfp-bottom-bar"><div class="mfp-title"></div><div class="mfp-counter"></div></div></div>',cursor:"mfp-zoom-out-cur",titleSrc:"title",verticalFit:!0,tError:'<a href="%url%">The image</a> could not be loaded.'},proto:{initImage:function(){var e=t.st.image,i=".image";t.types.push("image"),x(f+i,function(){"image"===t.currItem.type&&e.cursor&&n.addClass(e.cursor)}),x(l+i,function(){e.cursor&&n.removeClass(e.cursor),I.off("resize"+v)}),x("Resize"+i,t.resizeImage),t.isLowIE&&x("AfterChange",t.resizeImage)},resizeImage:function(){var e=t.currItem;if(e.img&&t.st.image.verticalFit){var i=0;t.isLowIE&&(i=parseInt(e.img.css("padding-top"),10)+parseInt(e.img.css("padding-bottom"),10)),e.img.css("max-height",t.wH-i)}},_onImageHasSize:function(e){e.img&&(e.hasSize=!0,N&&clearInterval(N),e.isCheckingImgSize=!1,T("ImageHasSize",e),e.imgHidden&&(t.content&&t.content.removeClass("mfp-loading"),e.imgHidden=!1))},findImageSize:function(e){var i=0,n=e.img[0],o=function(a){N&&clearInterval(N),N=setInterval(function(){return n.naturalWidth>0?(t._onImageHasSize(e),void 0):(i>200&&clearInterval(N),i++,3===i?o(10):40===i?o(50):100===i&&o(500),void 0)},a)};o(1)},getImage:function(i,n){var o=0,a=function(){i&&(i.img[0].complete?(i.img.off(".mfploader"),i===t.currItem&&(t._onImageHasSize(i),t.updateStatus("ready")),i.hasSize=!0,i.loaded=!0,T("ImageLoadComplete")):(o++,200>o?setTimeout(a,100):r()))},r=function(){i&&(i.img.off(".mfploader"),i===t.currItem&&(t._onImageHasSize(i),t.updateStatus("error",s.tError.replace("%url%",i.src))),i.hasSize=!0,i.loaded=!0,i.loadError=!0)},s=t.st.image,l=n.find(".mfp-img");if(l.length){var c=new Image;c.className="mfp-img",i.img=e(c).on("load.mfploader",a).on("error.mfploader",r),c.src=i.src,l.is("img")&&(i.img=i.img.clone()),i.img[0].naturalWidth>0&&(i.hasSize=!0)}return t._parseMarkup(n,{title:W(i),img_replaceWith:i.img},i),t.resizeImage(),i.hasSize?(N&&clearInterval(N),i.loadError?(n.addClass("mfp-loading"),t.updateStatus("error",s.tError.replace("%url%",i.src))):(n.removeClass("mfp-loading"),t.updateStatus("ready")),n):(t.updateStatus("loading"),i.loading=!0,i.hasSize||(i.imgHidden=!0,n.addClass("mfp-loading"),t.findImageSize(i)),n)}}});var R,Z=function(){return void 0===R&&(R=void 0!==document.createElement("p").style.MozTransform),R};e.magnificPopup.registerModule("zoom",{options:{enabled:!1,easing:"ease-in-out",duration:300,opener:function(e){return e.is("img")?e:e.find("img")}},proto:{initZoom:function(){var e=t.st.zoom,i=".zoom";if(e.enabled&&t.supportsTransition){var n,o,a=e.duration,r=function(t){var i=t.clone().removeAttr("style").removeAttr("class").addClass("mfp-animated-image"),n="all "+e.duration/1e3+"s "+e.easing,o={position:"fixed",zIndex:9999,left:0,top:0,"-webkit-backface-visibility":"hidden"},a="transition";return o["-webkit-"+a]=o["-moz-"+a]=o["-o-"+a]=o[a]=n,i.css(o),i},s=function(){t.content.css("visibility","visible")};x("BuildControls"+i,function(){if(t._allowZoom()){if(clearTimeout(n),t.content.css("visibility","hidden"),image=t._getItemToZoom(),!image)return s(),void 0;o=r(image),o.css(t._getOffset()),t.wrap.append(o),n=setTimeout(function(){o.css(t._getOffset(!0)),n=setTimeout(function(){s(),setTimeout(function(){o.remove(),image=o=null,T("ZoomAnimationEnded")},16)},a)},16)}}),x(c+i,function(){if(t._allowZoom()){if(clearTimeout(n),t.st.removalDelay=a,!image){if(image=t._getItemToZoom(),!image)return;o=r(image)}o.css(t._getOffset(!0)),t.wrap.append(o),t.content.css("visibility","hidden"),setTimeout(function(){o.css(t._getOffset())},16)}}),x(l+i,function(){t._allowZoom()&&(s(),o&&o.remove())})}},_allowZoom:function(){return"image"===t.currItem.type},_getItemToZoom:function(){return t.currItem.hasSize?t.currItem.img:!1},_getOffset:function(i){var n;n=i?t.currItem.img:t.st.zoom.opener(t.currItem.el||t.currItem);var o=n.offset(),a=parseInt(n.css("padding-top"),10),r=parseInt(n.css("padding-bottom"),10);o.top-=e(window).scrollTop()-a;var s={width:n.width(),height:(b?n.innerHeight():n[0].offsetHeight)-r-a};return Z()?s["-moz-transform"]=s.transform="translate("+o.left+"px,"+o.top+"px)":(s.left=o.left,s.top=o.top),s}}});var q="iframe",D="//about:blank",K=function(e){if(t.currTemplate[q]){var i=t.currTemplate[q].find("iframe");i.length&&(e||(i[0].src=D),t.isIE8&&i.css("display",e?"block":"none"))}};e.magnificPopup.registerModule(q,{options:{markup:'<div class="mfp-iframe-scaler"><div class="mfp-close"></div><iframe class="mfp-iframe" src="//about:blank" frameborder="0" allowfullscreen></iframe></div>',srcAction:"iframe_src",patterns:{youtube:{index:"youtube.com",id:"v=",src:"//www.youtube.com/embed/%id%?autoplay=1"},vimeo:{index:"vimeo.com/",id:"/",src:"//player.vimeo.com/video/%id%?autoplay=1"},gmaps:{index:"//maps.google.",src:"%id%&output=embed"}}},proto:{initIframe:function(){t.types.push(q),x("BeforeChange",function(e,t,i){t!==i&&(t===q?K():i===q&&K(!0))}),x(l+"."+q,function(){K()})},getIframe:function(i,n){var o=i.src,a=t.st.iframe;e.each(a.patterns,function(){return o.indexOf(this.index)>-1?(this.id&&(o="string"==typeof this.id?o.substr(o.lastIndexOf(this.id)+this.id.length,o.length):this.id.call(this,o)),o=this.src.replace("%id%",o),!1):void 0});var r={};return a.srcAction&&(r[a.srcAction]=o),t._parseMarkup(n,r,i),t.updateStatus("ready"),n}}});var Y=function(e){var i=t.items.length;return e>i-1?e-i:0>e?i+e:e},U=function(e,t,i){return e.replace("%curr%",t+1).replace("%total%",i)};e.magnificPopup.registerModule("gallery",{options:{enabled:!1,arrowMarkup:'<button title="%title%" type="button" class="mfp-arrow mfp-arrow-%dir%"></button>',preload:[0,2],navigateByImgClick:!0,arrows:!0,tPrev:"Previous (Left arrow key)",tNext:"Next (Right arrow key)",tCounter:"%curr% of %total%"},proto:{initGallery:function(){var i=t.st.gallery,n=".mfp-gallery",a=Boolean(e.fn.mfpFastClick);return t.direction=!0,i&&i.enabled?(r+=" mfp-gallery",x(f+n,function(){i.navigateByImgClick&&t.wrap.on("click"+n,".mfp-img",function(){return t.items.length>1?(t.next(),!1):void 0}),o.on("keydown"+n,function(e){37===e.keyCode?t.prev():39===e.keyCode&&t.next()})}),x("UpdateStatus"+n,function(e,i){i.text&&(i.text=U(i.text,t.currItem.index,t.items.length))}),x(p+n,function(e,n,o,a){var r=t.items.length;o.counter=r>1?U(i.tCounter,a.index,r):""}),x("BuildControls"+n,function(){if(t.items.length>1&&i.arrows&&!t.arrowLeft){var n=i.arrowMarkup,o=t.arrowLeft=e(n.replace("%title%",i.tPrev).replace("%dir%","left")).addClass(y),r=t.arrowRight=e(n.replace("%title%",i.tNext).replace("%dir%","right")).addClass(y),s=a?"mfpFastClick":"click";o[s](function(){t.prev()}),r[s](function(){t.next()}),t.isIE7&&(k("b",o[0],!1,!0),k("a",o[0],!1,!0),k("b",r[0],!1,!0),k("a",r[0],!1,!0)),t.container.append(o.add(r))}}),x(m+n,function(){t._preloadTimeout&&clearTimeout(t._preloadTimeout),t._preloadTimeout=setTimeout(function(){t.preloadNearbyImages(),t._preloadTimeout=null},16)}),x(l+n,function(){o.off(n),t.wrap.off("click"+n),t.arrowLeft&&a&&t.arrowLeft.add(t.arrowRight).destroyMfpFastClick(),t.arrowRight=t.arrowLeft=null}),void 0):!1},next:function(){t.direction=!0,t.index=Y(t.index+1),t.updateItemHTML()},prev:function(){t.direction=!1,t.index=Y(t.index-1),t.updateItemHTML()},goTo:function(e){t.direction=e>=t.index,t.index=e,t.updateItemHTML()},preloadNearbyImages:function(){var e,i=t.st.gallery.preload,n=Math.min(i[0],t.items.length),o=Math.min(i[1],t.items.length);for(e=1;(t.direction?o:n)>=e;e++)t._preloadItem(t.index+e);for(e=1;(t.direction?n:o)>=e;e++)t._preloadItem(t.index-e)},_preloadItem:function(i){if(i=Y(i),!t.items[i].preloaded){var n=t.items[i];n.parsed||(n=t.parseEl(i)),T("LazyLoad",n),"image"===n.type&&(n.img=e('<img class="mfp-img" />').on("load.mfploader",function(){n.hasSize=!0}).on("error.mfploader",function(){n.hasSize=!0,n.loadError=!0,T("LazyLoadError",n)}).attr("src",n.src)),n.preloaded=!0}}}});var G="retina";e.magnificPopup.registerModule(G,{options:{replaceSrc:function(e){return e.src.replace(/\.\w+$/,function(e){return"@2x"+e})},ratio:1},proto:{initRetina:function(){if(window.devicePixelRatio>1){var e=t.st.retina,i=e.ratio;i=isNaN(i)?i():i,i>1&&(x("ImageHasSize."+G,function(e,t){t.img.css({"max-width":t.img[0].naturalWidth/i,width:"100%"})}),x("ElementParse."+G,function(t,n){n.src=e.replaceSrc(n,i)}))}}}}),function(){var t=1e3,i="ontouchstart"in window,n=function(){I.off("touchmove"+a+" touchend"+a)},o="mfpFastClick",a="."+o;e.fn.mfpFastClick=function(o){return e(this).each(function(){var r,s=e(this);if(i){var l,c,d,u,p,f;s.on("touchstart"+a,function(e){u=!1,f=1,p=e.originalEvent?e.originalEvent.touches[0]:e.touches[0],c=p.clientX,d=p.clientY,I.on("touchmove"+a,function(e){p=e.originalEvent?e.originalEvent.touches:e.touches,f=p.length,p=p[0],(Math.abs(p.clientX-c)>10||Math.abs(p.clientY-d)>10)&&(u=!0,n())}).on("touchend"+a,function(e){n(),u||f>1||(r=!0,e.preventDefault(),clearTimeout(l),l=setTimeout(function(){r=!1},t),o())})})}s.on("click"+a,function(){r||o()})})},e.fn.destroyMfpFastClick=function(){e(this).off("touchstart"+a+" click"+a),i&&I.off("touchmove"+a+" touchend"+a)}}()})(window.jQuery||window.Zepto);
;

/* wp-content/themes/CherryFramework/js/tmstickup.js */
(function($){
	$.fn.tmStickUp=function(options){

		var getOptions = {
			correctionSelector: $('.correctionSelector')
		,	listenSelector: $('.listenSelector')
		,	active: false
		,	pseudo: true
		}
		$.extend(getOptions, options);

		var
			_this = $(this)
		,	_window = $(window)
		,	_document = $(document)
		,	thisOffsetTop = 0
		,	thisOuterHeight = 0
		,	thisMarginTop = 0
		,	thisPaddingTop = 0
		,	documentScroll = 0
		,	pseudoBlock
		,	lastScrollValue = 0
		,	scrollDir = ''
		,	tmpScrolled
		;

		if (_this.length != 0) {
			init();
		}

		function init(){
			thisOffsetTop = parseInt(_this.offset().top);
			thisMarginTop = parseInt(_this.css("margin-top"));
			thisOuterHeight = parseInt(_this.outerHeight(true));

			if(getOptions.pseudo){
				$('<div class="pseudoStickyBlock"></div>').insertAfter(_this);
				pseudoBlock = $('.pseudoStickyBlock');
				pseudoBlock.css({"position":"relative", "display":"block"});
			}

			if(getOptions.active){
				addEventsFunction();
			}
		}//end init

		function addEventsFunction(){
			_document.on('scroll', function() {
				tmpScrolled = $(this).scrollTop();
					if (tmpScrolled > lastScrollValue){
						scrollDir = 'down';
					} else {
						scrollDir = 'up';
					}
				lastScrollValue = tmpScrolled;

				if(getOptions.correctionSelector.length != 0){
					correctionValue = getOptions.correctionSelector.outerHeight(true);
				}else{
					correctionValue = 0;
				}

				documentScroll = parseInt(_window.scrollTop());
				if(thisOffsetTop - correctionValue < documentScroll){
					_this.addClass('isStuck');
					getOptions.listenSelector.addClass('isStuck');
					if(getOptions.pseudo){
						_this.css({position:"fixed", top:correctionValue});
						pseudoBlock.css({"height":thisOuterHeight});
					}else{
						_this.css({position:"fixed", top:correctionValue});
					}
				}else{
					_this.removeClass('isStuck');
					getOptions.listenSelector.removeClass('isStuck');
					if(getOptions.pseudo){
						_this.css({position:"relative", top:0});
						pseudoBlock.css({"height":0});
					}else{
						_this.css({position:"absolute", top:0});
					}
				}
			}).trigger('scroll');

			_document.on("resize", function() {
				if(_this.hasClass('isStuck')){
					if( thisOffsetTop != parseInt(pseudoBlock.offset().top) ) thisOffsetTop = parseInt(pseudoBlock.offset().top);
				} else {
					if( thisOffsetTop != parseInt(_this.offset().top) ) thisOffsetTop = parseInt(_this.offset().top);
				}
			})
		}
	}//end tmStickUp function
})(jQuery)
;

/* wp-content/themes/CherryFramework/js/device.min.js */
/*! device.js 0.1.58 */
(function(){var a,b,c,d,e,f,g,h,i,j;a=window.device,window.device={},c=window.document.documentElement,j=window.navigator.userAgent.toLowerCase(),device.ios=function(){return device.iphone()||device.ipod()||device.ipad()},device.iphone=function(){return d("iphone")},device.ipod=function(){return d("ipod")},device.ipad=function(){return d("ipad")},device.android=function(){return d("android")},device.androidPhone=function(){return device.android()&&d("mobile")},device.androidTablet=function(){return device.android()&&!d("mobile")},device.blackberry=function(){return d("blackberry")||d("bb10")||d("rim")},device.blackberryPhone=function(){return device.blackberry()&&!d("tablet")},device.blackberryTablet=function(){return device.blackberry()&&d("tablet")},device.windows=function(){return d("windows")},device.windowsPhone=function(){return device.windows()&&d("phone")},device.windowsTablet=function(){return device.windows()&&d("touch")},device.fxos=function(){return(d("(mobile;")||d("(tablet;"))&&d("; rv:")},device.fxosPhone=function(){return device.fxos()&&d("mobile")},device.fxosTablet=function(){return device.fxos()&&d("tablet")},device.meego=function(){return d("meego")},device.mobile=function(){return device.androidPhone()||device.iphone()||device.ipod()||device.windowsPhone()||device.blackberryPhone()||device.fxosPhone()||device.meego()},device.tablet=function(){return device.ipad()||device.androidTablet()||device.blackberryTablet()||device.windowsTablet()||device.fxosTablet()},device.portrait=function(){return 90!==Math.abs(window.orientation)},device.landscape=function(){return 90===Math.abs(window.orientation)},device.noConflict=function(){return window.device=a,this},d=function(a){return-1!==j.indexOf(a)},f=function(a){var b;return b=new RegExp(a,"i"),c.className.match(b)},b=function(a){return f(a)?void 0:c.className+=" "+a},h=function(a){return f(a)?c.className=c.className.replace(a,""):void 0},device.ios()?device.ipad()?b("ios ipad tablet"):device.iphone()?b("ios iphone mobile"):device.ipod()&&b("ios ipod mobile"):device.android()?device.androidTablet()?b("android tablet"):b("android mobile"):device.blackberry()?device.blackberryTablet()?b("blackberry tablet"):b("blackberry mobile"):device.windows()?device.windowsTablet()?b("windows tablet"):device.windowsPhone()?b("windows mobile"):b("desktop"):device.fxos()?device.fxosTablet()?b("fxos tablet"):b("fxos mobile"):device.meego()?b("meego mobile"):b("desktop"),e=function(){return device.landscape()?(h("portrait"),b("landscape")):(h("landscape"),b("portrait"))},i="onorientationchange"in window,g=i?"orientationchange":"resize",window.addEventListener?window.addEventListener(g,e,!1):window.attachEvent?window.attachEvent(g,e):window[g]=e,e()}).call(this);
;

/* Unused home initializer omitted; original retained: wp-content/themes/CherryFramework/js/jquery.debouncedresize.js */
;

/* Unused home initializer omitted; original retained: wp-content/themes/CherryFramework/js/jquery.ba-resize.min.js */
;

/* wp-content/themes/theme53985/parallax-slider/js/parallaxSlider.js */
(function($){
     $.fn.parallaxSlider=function(o)
     { 
            
        var options = {
            prevButton: $('.prevButton')
        ,   nextButton: $('.nextButton')
        ,   duration: 1000
        ,   autoSwitcher: true
        ,   autoSwitcherDelay: 7000
        ,   slider_navs: true
        ,   scrolling_description: false
        ,   slider_pagination: 'buttons_pagination'
        ,   animateLayout: 'zoom-fade-eff' //simple-fade-eff, zoom-fade-eff, slide-top-eff
        ,   parallaxEffect: 'parallax_effect_normal'
        ,   parallaxInvert: false
        ,   liteMode: false
        }
        $.extend(options, o);
        var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        var persistentPaused = false, pointerInside = false;
        var lang = document.documentElement.lang.split('-')[0];
        var labels = {
            cs: ['Předchozí snímek','Následující snímek','Pozastavit střídání','Pokračovat ve střídání','Automatika vypnuta: omezený pohyb','Úvodní nabídka','Snímek'],
            en: ['Previous slide','Next slide','Pause slideshow','Resume slideshow','Slideshow off: reduced motion','Featured services','Slide'],
            de: ['Vorherige Folie','Nächste Folie','Diashow pausieren','Diashow fortsetzen','Automatik aus: reduzierte Bewegung','Ausgewählte Leistungen','Folie'],
            uk: ['Попередній слайд','Наступний слайд','Призупинити показ','Продовжити показ','Автопоказ вимкнено: зменшення руху','Основні послуги','Слайд'],
            vi: ['Trang chiếu trước','Trang chiếu tiếp','Tạm dừng trình chiếu','Tiếp tục trình chiếu','Tắt tự động: giảm chuyển động','Dịch vụ nổi bật','Trang chiếu']
        };
        var sliderLabels = labels[lang] || labels.cs;
        var rotationButton;
        var initialServerSlide = false;
        // Reuse the responsive first photograph when the slideshow cycles back.
        var firstPicture = this[0].querySelector("#mainImageHolder picture");
        firstPicture = firstPicture ? firstPicture.cloneNode(true) : null;
        
        var 
            _this = $(this)
        ,   _window = $(window)
        ,   _document = $(document)
        ,   sliderData = new Array()
        ,   itemLength = 0 
        ,   currIndex
        ,   prevIndex
        ,   isPreviewLoading = false
        ,   isPreviewAnimate = false
        ,   intervalSwitcher
        
        ,   obj_inner
        ,   mainImageHolder
        ,   primaryImageHolder
        ,   secondarImageHolder
        ,   mainCaptionHolder
        ,   primaryCaption
        ,   secondaryCaption
        ,   mainCaptionHolderContainer
        ,   previewSpinner
        ,   parallaxPrevBtn
        ,   parallaxNextBtn
        ,   slidesCounterList
        ,   paralaxSliderPagination
        ,   progressBar
        ,   youtubeApiLoad = false
        ,   vimeoApiLoad = false
        
        ,   parallax = true
        ,   parallaxType = 'parallax_normal'
        ,   _baseHeight
        ,   _thisOffsetTop = _this.offset().top
        ,   _thisHeight = _this.height()
        ,   _windowWidth = _window.width()
        ,   _windowHeight = _window.height()
        ,   originalWidth = 0
        ,   originalHeight = 0
        ,   bufferRatio  
        ;
  
                
        // parse slider data      
        $('ul li', _this).each(
            function()
            {
                var this_slide = $(this),
                    slideData = new Object(),
                    slide_type = 'image',
                    image = this_slide.attr('data-preview'),
                    thumb = this_slide.attr('data-thumb-url'),
                    caption = this_slide.html(),
                    link = this_slide.attr('data-ulr-link'),
                    mp4_src = this_slide.attr('data-video-src-mp4'),
                    webm_src = this_slide.attr('data-video-src-webm'),
                    ogv_src = this_slide.attr('data-video-src-ogv'),
                    video_loader = this_slide.attr('data-video-preloader'),
                    youtube_id = this_slide.attr('data-video-youtube-id'),
                    vimeo_id = this_slide.attr('data-video-vimeo-id');

            	if (mp4_src || webm_src || ogv_src) slide_type = 'library_video';
            	if (youtube_id) {
            	   slide_type = 'youtube_video';
            	   youtubeApiLoad = true
            	}
            	if (vimeo_id) {
            	   slide_type = 'vimeo_video';
                   vimeoApiLoad = true  
            	}
                if (options.liteMode) slide_type = 'image';
                  
                slideData =
                {
                    slide_type: slide_type,
                    image: image,
                    thumb: thumb,
                    caption: caption,
                    link: link,
                    library_video: 
                    {
                        mp4_src: mp4_src,
            			webm_src: webm_src,
            			ogv_src: ogv_src,
            			video_loader: video_loader,
                        video_loaded: false,
                    },
                    youtube_video: 
                    {
                        youtube_id: youtube_id,
                    },
            		vimeo_video: 
                    {
                        vimeo_id: vimeo_id,
                    }
                };
                
                sliderData.push(slideData);
            }
        )
        
        // if necessary, load the youtube and vimeo API
        if(youtubeApiLoad)
            $.getScript( 'https://www.youtube.com/iframe_api', function( ) {
                if(sliderData[0].slide_type == 'youtube_video')
                    window.onYouTubeIframeAPIReady = function() {
                        init();   
                    }
            });
        if(vimeoApiLoad)
            $.getScript( '//f.vimeocdn.com/js/froogaloop2.min.js', function( ) {
                if(sliderData[0].slide_type == 'vimeo_video') init();
            });
        
                    
        if(sliderData[0].slide_type != 'youtube_video' && sliderData[0].slide_type != 'vimeo_video') init();
        
            
        function init()
        {               
            //  holder erase
            initialServerSlide = !!_this.find('#mainImageHolder > .primaryHolder img').length;
            _this.children('ul.baseList').remove();
            _this.addClass(options.animateLayout).attr('role', 'region').attr('aria-roledescription', 'carousel').attr('aria-label', sliderLabels[5]);
    
            //  preview holder build
            if (!initialServerSlide) _this.append("<div id='mainImageHolder'></div>");
            mainImageHolder = $('#mainImageHolder');
    
             //  caption holder build
            if (!initialServerSlide) _this.append("<div id='mainCaptionHolder'><div class='container'></div></div>");
            mainCaptionHolder = $('#mainCaptionHolder');
            mainCaptionHolderContainer = $('>.container', mainCaptionHolder);
    
            //  controls build
            _this.append("<div class='controlBtn parallaxPrevBtn'><div class='innerBtn icon-angle-left'></div><div class='slidesCounter'></div></div><div class='controlBtn parallaxNextBtn'><div class='innerBtn icon-angle-right'></div><div class='slidesCounter'></div></div>");
            parallaxPrevBtn = $('.parallaxPrevBtn', _this);
            parallaxNextBtn = $('.parallaxNextBtn', _this);
            rotationButton = $('<button type="button" class="slider-rotation"><span class="slider-rotation-icon" aria-hidden="true"></span></button>').appendTo(_this);
            rotationButton.on('click', function(){
                persistentPaused = !persistentPaused;
                if (!persistentPaused) pointerInside = false;
                autoSwitcher();
            });
    
            //  fullpreview pagination build
            _this.append("<div id='paralaxSliderPagination'><ul></ul></div>");
            paralaxSliderPagination = $('#paralaxSliderPagination');
    
            slidesCounterList = $('.slidesCounter', _this);
            
            //  preview loader build
            _this.append("<div id='previewSpinner'><span></span></div>");
            previewSpinner = $('#previewSpinner');
    
            _this.on("reBuild",
                function(e,d){
                    setBuilder(d);
                }
            )
    
            _this.on("switchNext",
                function(e){
                    nextSwither();
                }
            )
    
            _this.on("switchPrev",
                function(e){
                    prevSwither();
                }
            )
            
            if(options.liteMode) options.parallaxEffect = 'parallax_none';
            
            switch (options.parallaxEffect) {
                case 'parallax_effect_low':
                    if(!options.parallaxInvert){
                        parallaxType = 'parallax_normal';
                    } else {
                        parallaxType = 'parallax_invert';
                    }
                    
                    bufferRatio = 3;
                    
                    break
                    
                case 'parallax_effect_normal':
                    if(!options.parallaxInvert){
                        parallaxType = 'parallax_normal';
                    } else {
                        parallaxType = 'parallax_invert';
                    }
                    
                     bufferRatio = 2.25;
                     
                    break
                    
                case 'parallax_effect_high':
                    if(!options.parallaxInvert){
                        parallaxType = 'parallax_normal';
                    } else {
                        parallaxType = 'parallax_invert';
                    }
                    
                    bufferRatio = 1.5;
                    
                    break
                    
                case 'parallax_effect_fixed':
                    if(isIE()){
                        parallax = false;
                    } else {
                        parallaxType = 'parallax_fixes';
                    }
                    
                    bufferRatio = 1;
                    
                    break
                    
                default:
                    parallax = false;
                    parallaxType = 'parallax_none';
                    
                    break
            }
            
            _baseHeight = getBaseHeight();
            
            
            setBuilder();
    
            if(!options.slider_navs){
                parallaxPrevBtn.remove();
                parallaxNextBtn.remove();
            }
            if(options.slider_pagination == 'none_pagination'){
                paralaxSliderPagination.remove();
            }
            
    
            addEventsFunction();
            autoSwitcher();
        }
        
        //------------------------- set Builder -----------------------------//
        function setBuilder()
        { 
            currIndex = 0;
            itemLength = sliderData.length;
            
            $(">ul", paralaxSliderPagination).empty();
            
            switch (options.slider_pagination) {
                case 'buttons_pagination':
                    paralaxSliderPagination.addClass('buttons_pagination');
                    for (var i = 0; i < itemLength; i++) {
                        $(">ul", paralaxSliderPagination).append("<li></li>");
                    };
                    
                    break
                
                case 'images_pagination':
                    paralaxSliderPagination.addClass('images_pagination');
                    for (var i = 0; i < itemLength; i++) {
                        $(">ul", paralaxSliderPagination).append("<li><img src='"+sliderData[i].thumb+"'></li>");
                    };
                    
                    break
            }
    
            if(itemLength==1){
                paralaxSliderPagination.remove();
                parallaxPrevBtn.remove();
                parallaxNextBtn.remove();
            }
    
            imageSwitcher(0);
            addEventsPagination();
        }
    
        function autoSwitcher()
        {
            clearInterval(intervalSwitcher);
            var focused = _this[0].contains(document.activeElement) && document.activeElement !== rotationButton[0];
            var stopped = persistentPaused || motionQuery.matches;
            var rotationLabel = motionQuery.matches ? sliderLabels[4] : (persistentPaused ? sliderLabels[3] : sliderLabels[2]);
            rotationButton.attr('aria-label', rotationLabel).attr('title', rotationLabel).attr('data-paused', stopped ? 'true' : 'false');
            rotationButton.prop('disabled', motionQuery.matches);
            mainCaptionHolder.attr('aria-live', stopped || focused ? 'polite' : 'off');
            if(options.autoSwitcher && !stopped && !focused && !pointerInside && !document.hidden){
                if(itemLength>1){
                    intervalSwitcher = setInterval(function(){
                        nextSwither();
                    }, options.autoSwitcherDelay);
                }
            }
        }
        
        //---------------  addEvents  ----------------------//
        function addEventsPagination()
        {
            $(">ul >li", paralaxSliderPagination).on("click",
                function()
                {
                    if((!isPreviewLoading) && (!isPreviewAnimate) && ($(this).index() !== currIndex)){
                        clearInterval(intervalSwitcher);
                        prevIndex = currIndex;
                        currIndex = $(this).index();
                        imageSwitcher(currIndex);
                    }
                }
            )
        }
        
        function addEventsFunction()
        {
            //--------------- controls events ----------------------//
            options.prevButton.on("click",
                function()
                {
                    clearInterval(intervalSwitcher);
                    prevSwither();
                }
            )
            options.nextButton.on("click",
                function()
                {
                    clearInterval(intervalSwitcher);
                    nextSwither(); 
                }
            )
            parallaxPrevBtn.on("click",
                function()
                {
                    clearInterval(intervalSwitcher);
                    prevSwither();
                }
            )
            parallaxNextBtn.on("click",
                function()
                {
                    clearInterval(intervalSwitcher);
                    nextSwither();
                }
            )
            
            // Pause when the tab is hidden and restart with a full interval on return.
            document.addEventListener('visibilitychange', autoSwitcher);
            _this.on('focusin', autoSwitcher);
            _this.on('focusout', function(){ setTimeout(autoSwitcher, 0); });
            _this.on('mouseenter', function(){ if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return; pointerInside = true; autoSwitcher(); });
            _this.on('mouseleave', function(){ pointerInside = false; autoSwitcher(); });
            if (motionQuery.addEventListener) motionQuery.addEventListener('change', autoSwitcher);
            else motionQuery.addListener(autoSwitcher);
            parallaxPrevBtn.add(parallaxNextBtn).attr('role', 'button').attr('tabindex', '0');
            parallaxPrevBtn.attr('aria-label', sliderLabels[0]);
            parallaxNextBtn.attr('aria-label', sliderLabels[1]);
            parallaxPrevBtn.add(parallaxNextBtn).on('keydown', function(event){
                if(event.key === 'Enter' || event.key === ' '){ event.preventDefault(); $(this).trigger('click'); }
            });
            //--------------- keyboard events ----------------------//
            _window.on("keydown",
                function(eventObject)
                {
                    if (!_this[0].contains(document.activeElement)) return;
                    switch (eventObject.keyCode){
                        case 37:
                            clearInterval(intervalSwitcher);
                            prevSwither();
                        break
                        case 39:
                             clearInterval(intervalSwitcher);
                            nextSwither();
                        break
                    }
                }
            )
            
            //------------------ window scroll event -------------//
            $(window).on('scroll',
                function()
                {
                    mainScrollFunction();
                }
            ).trigger('scroll');
            
            //------------------ window resize event -------------//
            $(window).on("resize",
                function()
                {
                    mainResizeFunction();
                }
            )
        }
        
        //-----------------------------------------------------------------
        function prevSwither()
        {
            if(!isPreviewLoading && !isPreviewAnimate){
                prevIndex = currIndex;
                if(currIndex > 0){
                    currIndex--;
                }else{
                    currIndex = itemLength-1;
                }
                    imageSwitcher(currIndex);
            }
        }
        function nextSwither()
        {
            if(!isPreviewLoading && !isPreviewAnimate){
                prevIndex = currIndex;
                if(currIndex < itemLength-1){
                    currIndex++;
                }else{
                    currIndex = 0;
                }
                imageSwitcher(currIndex);
            }
        }
        
        //------------------------- main Swither ----------------------------//
        function imageSwitcher(currIndex)
        {
            // Keep the first server-rendered image/caption nodes; no JS gate for the initial paint.
            if (initialServerSlide && currIndex === 0) {
                initialServerSlide = false;
                primaryImageHolder = $('> .primaryHolder', mainImageHolder);
                primaryCaption = $('> .primaryCaption', mainCaptionHolderContainer);
                primaryCaption.attr('role', 'group').attr('aria-roledescription', sliderLabels[6]).attr('aria-label', '1 / ' + itemLength);
                obj_inner = $('.obj-inner', primaryImageHolder);
                originalWidth = 1980; originalHeight = 1312;
                objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                slidesCounterList.attr('aria-hidden', 'true').text('1/' + itemLength);
                primaryCaption.attr('aria-hidden', 'false');
                previewSpinner.hide();
                _this.addClass('slider-ready');
                return;
            }
            //  add next ImageHolder
            if(primaryImageHolder){
                secondarImageHolder = primaryImageHolder;
                secondarImageHolder.toggleClass('primaryHolder').toggleClass('secondaryHolder');
            }
            
            mainImageHolder.append('<div class="primaryHolder"></div>');
            primaryImageHolder = $('> .primaryHolder', mainImageHolder);
            objectCssTransition(primaryImageHolder, 0, 'ease');
            primaryImageHolder.addClass('animateState');
            
            
            //  add next CaptionHolder
            mainCaptionHolder.find('>a').remove();
            
            if(primaryCaption){
                secondaryCaption = primaryCaption;
                secondaryCaption.toggleClass('primaryCaption').toggleClass('secondaryCaption');
                // Retire the outgoing text immediately; image backgrounds may still crossfade.
                secondaryCaption.attr('aria-hidden', 'true').attr('inert', '').hide();
            }
            
            if(sliderData[currIndex].caption != ''){
                mainCaptionHolderContainer.append('<div class="primaryCaption"></div>');
                primaryCaption = $('> .primaryCaption', mainCaptionHolderContainer);
                primaryCaption.html(sliderData[currIndex].caption).attr('role', 'group').attr('aria-roledescription', sliderLabels[6]).attr('aria-label', (currIndex+1) + ' / ' + itemLength).attr('aria-hidden', 'true').attr('inert', '');
                objectCssTransition(primaryCaption, 0, 'ease');
                primaryCaption.addClass('animateState');   
            }
            if(sliderData[currIndex].link != '') mainCaptionHolder.append('<a href="'+sliderData[currIndex].link+'"></a>');
            
            if (!secondarImageHolder && primaryCaption) {
                primaryCaption.removeClass('animateState').attr('aria-hidden', 'false').removeAttr('inert');
            }
            slidesCounterList.attr('aria-hidden', 'true').text((currIndex+1) + '/'+itemLength);
            $(">ul >li", paralaxSliderPagination).removeClass('active').eq(currIndex).addClass('active');
    
            isPreviewLoading = true;
            isPreviewAnimate = true;
            previewSpinner.css({display:'block'}).stop().fadeTo(300, 1);
            
            if(progressBar) progressBar.remove(); 
            
            //------------------------- image slide type ----------------------------// 
            if(sliderData[currIndex].slide_type == 'image')
            {  
                var responsivePicture = currIndex === 0 && firstPicture ? firstPicture.cloneNode(true) : null;
                var img = responsivePicture ? responsivePicture.querySelector("img") : new Image();
                var slideImageLoaded = false;

                img.onload = function ()
                {
                    if (slideImageLoaded) return;
                    slideImageLoaded = true;
                    if (responsivePicture) {
                        obj_inner = $(img);
                    } else if(!options.liteMode){
                        primaryImageHolder.html('<div class="parallax-slider-img obj-inner"></div>');
                        obj_inner = $('.parallax-slider-img', primaryImageHolder);
                        obj_inner.css('background-image', 'url(' + img.src + ')'); 
                    } else { 
                        primaryImageHolder.html('<img class="parallax-slider-img obj-inner" src="'+img.src+'" alt=""/>');
                        obj_inner = $('.parallax-slider-img', primaryImageHolder);
                    }
                    
                    if(isIE()) obj_inner.css({backgroundAttachment:'fixed'});
                    
                    originalWidth = responsivePicture ? 1980 : img.width;
                    originalHeight = responsivePicture ? 1312 : img.height;
                    objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                
                    onSlideLoaded();
                }
                
                if (responsivePicture) {
                    primaryImageHolder[0].appendChild(responsivePicture);
                    if (img.complete && img.naturalWidth) img.onload();
                } else {
                    img.src = sliderData[currIndex].image;
                }
            }
            //------------------------- library video slide type ----------------------------// 
            if(sliderData[currIndex].slide_type == 'library_video')
            {    
                if(sliderData[currIndex].library_video.player){
                    
                    var videoElement = sliderData[currIndex].library_video.player;
                    
                } else {
                    
                    var videoElement = document.createElement('video');
                    
                    videoElement.className = 'parallax-slider-video obj-inner';
                    videoElement.setAttribute('loop','loop');
                    videoElement.setAttribute('poster', sliderData[currIndex].image);
                    
                    function addSourceToVideo(element, src, type)
                    {
                        if(src)
                        {                
                            var source = document.createElement('source');
                        
                            source.src = src;
                            source.type = type;
                        
                            element.appendChild(source);
                        }                
                    }   
                    
                    addSourceToVideo(videoElement, sliderData[currIndex].library_video.mp4_src, 'video/mp4');
                    addSourceToVideo(videoElement, sliderData[currIndex].library_video.webm_src, 'video/webm');
                    addSourceToVideo(videoElement, sliderData[currIndex].library_video.ogv_src, 'video/ogv');
                    
                    videoElement.load();
                    
                    sliderData[currIndex].library_video.player = videoElement;
                }
                
                primaryImageHolder.get(0).appendChild(videoElement);
                obj_inner = $('.parallax-slider-video', primaryImageHolder);
                                 
                videoElement.play();
                
                originalWidth = 0;
                originalHeight = 0;
                originalWidth = videoElement.videoWidth;
                originalHeight = videoElement.videoHeight;
                
                var img = new Image();

                
                img.onload = function ()
                {
                    originalWidth = originalWidth==0 ? img.width : originalWidth;
                    originalHeight = originalHeight==0 ? img.height : originalHeight;
                    objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                    
                    onSlideLoaded();
                }
                
                videoElement.onloadedmetadata = function()
                {
                    originalWidth = videoElement.videoWidth;
                    originalHeight = videoElement.videoHeight;
                    objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);   
                }
              
                videoLoaded = sliderData[currIndex].library_video.video_loaded;              
                
                if(sliderData[currIndex].library_video.video_loader && !videoLoaded)
                {
                    _this.append('<div class="parallax-slider-video-progress-bar"><div class="parallax-slider-video-progress"></div></div>');
                    progressBar = $('.parallax-slider-video-progress-bar', _this);
                    progressLine = $('.parallax-slider-video-progress', progressBar);
                    
                    var updateProgressBar = function()
                    {
                        if(videoElement.buffered.length > 0) {
                            if(videoElement.played.length > 0) progressBar.css({background:'#000'});
                            if(videoElement.buffered.end(0) == videoElement.duration){
                                clearTimeout(watchBuffer);
                                sliderData[currIndex].library_video.video_loaded = true;
                                progressLine.width('100%');
                                progressBar.stop().delay(1000).animate({top:'-15px'}, 1000, function(){
                                    progressBar.remove();
                                });
                            }else{
                                progressLine.width(((videoElement.buffered.end(0) / videoElement.duration) * 100) + '%');
                            }
                        }
                    };
                    var watchBuffer = setInterval(updateProgressBar, 500);
                }                                  
            }
            //------------------------- youtube video slide type ----------------------------// 
            if(sliderData[currIndex].slide_type == 'youtube_video')
            {
                var youtube_id = sliderData[currIndex].youtube_video.youtube_id;
                 
                primaryImageHolder.html('<div id="parallax-slider-youtube-video'+currIndex+'" class="parallax-slider-youtube-video obj-inner"></div>');
                 
                function onPlayerReady(event)
                {
                    event.target.playVideo();
                    
                    var intervalID;
                    intervalID = setInterval(function(){
                        if(youtubePlayer.getPlayerState() == 1){
                            clearInterval(intervalID);
                            onSlideLoaded();
                        }
                    }, 100); 
                } 
                
                originalWidth = 16;
                originalHeight = 9;

                var youtubePlayer = new YT.Player('parallax-slider-youtube-video'+currIndex+'', {
                    height: '0px',
                    width: '0px',
                    playerVars : {
                         'autoplay' : 1,
                         'showinfo' : 0,
                         'controls' : 0,
                         'loop' : 1,
                         'disablekb' : 1, 
                         'enablejsapi' : 1,
                         'html5' : isIE() ? 1 : 0,                                    
                         'playlist': youtube_id
                    },
                    videoId: youtube_id,
                    events: {
                        'onReady': onPlayerReady
                    }
                });
               
                obj_inner = $('#parallax-slider-youtube-video'+currIndex+'', primaryImageHolder);
                objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                    
                sliderData[currIndex].youtube_video.player = youtubePlayer;
                
            }
            //------------------------- vimeo video slide type ----------------------------//
            if(sliderData[currIndex].slide_type == 'vimeo_video')
            {
                var vimeo_id = sliderData[currIndex].vimeo_video.vimeo_id,
                    vimeo_iframe,
                    vimeo_player,
                    vimeo_player_playstarted = false;
                    
                primaryImageHolder.html('<div class="parallax-slider-vimeo-video obj-inner"><iframe id="vimeo-player-'+currIndex+'" class="parallax-slider-vimeo-iframe" src="http://player.vimeo.com/video/'+vimeo_id+'?api=1&player_id=vimeo-player-'+currIndex+';autoplay=1&amp;loop=1" frameborder="0"></iframe></div>');
                
                vimeo_iframe = $('#vimeo-player-'+currIndex+'')[0];
                vimeo_player = $f(vimeo_iframe);
                
                sliderData[currIndex].vimeo_video.player = vimeo_player;
                    
                vimeo_player.addEvent('ready', function() {
                    vimeo_player.addEvent('play', function(){
                        if(!vimeo_player_playstarted)
                        {
                            vimeo_player_playstarted = true;
                            
                            originalWidth = 16;
                            originalHeight = 9;
                            
                            obj_inner = $('.obj-inner', primaryImageHolder);
                            objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                            
                            setTimeout(onSlideLoaded, 500);
                        }
                    });
                })
            }
            
            function onSlideLoaded()
            {
                var slideDuration = (!secondarImageHolder || motionQuery.matches) ? 0 : options.duration;
                isPreviewLoading = false;
                previewSpinner.stop().fadeTo(300, 0, function(){ $(this).css({display:'none'}); });
                
                objectCssTransition(primaryImageHolder, slideDuration, 'outCubic');
                primaryImageHolder.removeClass('animateState');
                
                if(secondarImageHolder){
                    if(sliderData[prevIndex].slide_type == 'youtube_video' || sliderData[prevIndex].slide_type == 'vimeo_video'){
                        setTimeout(function(){
                            if(sliderData[prevIndex].slide_type == 'youtube_video') sliderData[prevIndex].youtube_video.player.stopVideo();
                            if(sliderData[prevIndex].slide_type == 'vimeo_video') sliderData[prevIndex].vimeo_video.player.api('unload');
                        }, slideDuration/1.25)
                    }

                    objectCssTransition(secondarImageHolder, slideDuration, 'outCubic');
                    secondarImageHolder.addClass('animateState');
                }
                
                objectCssTransition(primaryCaption, slideDuration, 'outCubic');
                if(primaryCaption){
                    
                    primaryCaption.removeClass('animateState').attr('aria-hidden', 'false').removeAttr('inert');
                } 
                
                if(secondaryCaption){
                    objectCssTransition(secondaryCaption, slideDuration, 'outCubic');
                    secondaryCaption.addClass('animateState');
                }
                
                setTimeout(function()
                {
                    if(secondarImageHolder) secondarImageHolder.remove();
                    if(secondaryCaption) secondaryCaption.remove();
                    
                    isPreviewAnimate = false;

                }, slideDuration )
            }         
        }
    
        //----------------------------------------------------//
        function objectCssTransition(obj, duration, ease)
        {
            if(objectExists(obj))
            {
                var durationValue;
        
                if(duration !== 0){
                    durationValue = motionQuery.matches ? 0 : duration/1000;
                }else{
                    durationValue = 0
                }
        
                switch(ease){
                    case 'ease':
                            obj.css({"-webkit-transition":"all "+durationValue+"s ease", "-moz-transition":"all "+durationValue+"s ease", "-o-transition":"all "+durationValue+"s ease", "transition":"all "+durationValue+"s ease"});
                    break;
                    case 'outSine':
                        obj.css({"-webkit-transition":"all "+durationValue+"s cubic-bezier(0.470, 0.000, 0.745, 0.715)", "-moz-transition":"all "+durationValue+"s cubic-bezier(0.470, 0.000, 0.745, 0.715)", "-o-transition":"all "+durationValue+"s cubic-bezier(0.470, 0.000, 0.745, 0.715)", "transition":"all "+durationValue+"s cubic-bezier(0.470, 0.000, 0.745, 0.715)"});
                    break;
                    case 'outCubic':
                        obj.css({"-webkit-transition":"all "+durationValue+"s cubic-bezier(0.215, 0.610, 0.355, 1.000)", "-moz-transition":"all "+durationValue+"s cubic-bezier(0.215, 0.610, 0.355, 1.000)", "-o-transition":"all "+durationValue+"s cubic-bezier(0.215, 0.610, 0.355, 1.000)", "transition":"all "+durationValue+"s cubic-bezier(0.215, 0.610, 0.355, 1.000)"});
                    break;
                    case 'outExpo':
                        obj.css({"-webkit-transition":"all "+durationValue+"s cubic-bezier(0.190, 1.000, 0.220, 1.000)", "-moz-transition":"all "+durationValue+"s cubic-bezier(0.190, 1.000, 0.220, 1.000)", "-o-transition":"all "+durationValue+"s cubic-bezier(0.190, 1.000, 0.220, 1.000)", "transition":"all "+durationValue+"s cubic-bezier(0.190, 1.000, 0.220, 1.000)"});
                    break;
                    case 'outBack':
                        obj.css({"-webkit-transition":"all "+durationValue+"s cubic-bezier(0.175, 0.885, 0.320, 1.275)", "-moz-transition":"all "+durationValue+"s cubic-bezier(0.175, 0.885, 0.320, 1.275)", "-o-transition":"all "+durationValue+"s cubic-bezier(0.175, 0.885, 0.320, 1.275)", "transition":"all "+durationValue+"s cubic-bezier(0.175, 0.885, 0.320, 1.275)"});
                    break;
                }
            }
        }
        
        //------------------------ Object resize ----------------------------//
        function objectResize(obj, baseWidth, baseHeight)
        {
            if(objectExists(obj))
            {
                var imageRatio,
                    newImgWidth,
                    newImgHeight,
                    newImgTop,
                    newImgLeft;
        
                imageRatio = originalHeight/originalWidth;
                containerRatio = baseHeight/baseWidth;
        
                if(containerRatio > imageRatio){
                    newImgHeight = baseHeight;
                    newImgWidth = Math.round( (newImgHeight*originalWidth) / originalHeight );   
                }else{
                    newImgWidth = baseWidth;
                    newImgHeight = Math.round( (newImgWidth*originalHeight) / originalWidth );
                }
        
                newImgLeft=-(newImgWidth-baseWidth)*.5;
                newImgTop= -(newImgHeight-baseHeight)*.5;
                            
                if(obj.prop('tagName').toLowerCase() == 'div'){ obj.css({width: '100%', height: newImgHeight, marginTop: newImgTop}); } else { obj.css({width: newImgWidth, height: newImgHeight, marginTop: newImgTop, marginLeft: newImgLeft}); }
                
                if(sliderData[currIndex].slide_type == 'vimeo_video'){
                    obj.find('.parallax-slider-vimeo-iframe').css({width: newImgWidth, height: newImgHeight+200, marginLeft: newImgLeft});
                }
            }
        }
        
        function objectExists(object){
            if(object){
                if(object.length > 0) return true;
            }
        }
        
        //------------------- main window scroll function -------------------//
        function mainScrollFunction(){
             if(!motionQuery.matches && (parallax || options.scrolling_description && !options.liteMode)){
                
                 var _documentScrollTop
                 ,   startScrollTop
                 ,   endScrollTop
                 ;
     
                 _documentScrollTop = _document.scrollTop();
                 _thisOffsetTop = _this.offset().top;
     
                 startScrollTop = _documentScrollTop + _windowHeight;
                 endScrollTop = _documentScrollTop - _thisHeight;
     
                 if((startScrollTop > _thisOffsetTop) && (endScrollTop < _thisOffsetTop)){  
                     
                     y = _documentScrollTop - _thisOffsetTop;
                     
                     if(parallax){
                         if(!options.parallaxInvert) {
                             newPositionTop =  parseInt(y / bufferRatio);
                         } else {
                             if(_thisOffsetTop < Math.abs(_windowHeight-_thisHeight)){
                                 newPositionTop = -parseInt(y / bufferRatio) - parseInt(_thisOffsetTop / bufferRatio);
                             } else{
                                 newPositionTop = -parseInt(y / bufferRatio) - parseInt(_windowHeight / bufferRatio)
                             }
                         }
                         
                         mainImageHolder.css({ top: newPositionTop + 'px' });   
                     }
                     
                     if(options.scrolling_description){
                         description_opacity = (1-(y / _thisHeight)).toFixed(2); 
                         if(description_opacity < 1) mainCaptionHolder.css('opacity', description_opacity);
                         
                         description_offset = parseInt(y/2.5);
                         if(description_offset > 0) {
                             mainCaptionHolder.css('top', description_offset);
                         } else {
                             mainCaptionHolder.css('top', '0px');   
                         }
                     }
                 }
             }
        }
        
        //------------------- main window resize function -------------------//
        function mainResizeFunction(){
            _windowWidth = _window.width();
            _windowHeight = _window.height();
            _thisWidth = _this.width();
            _thisHeight = _this.height();
            _thisOffsetTop = _this.offset().top;
            
            _baseHeight = getBaseHeight();
            objectResize(obj_inner, _thisWidth, _baseHeight);
            mainScrollFunction();
        }

        //------------------- get heigth function -------------------//
        function getBaseHeight(){
            
            switch (parallaxType) {
                case 'parallax_normal':
                    if(_thisOffsetTop < (_windowHeight-_thisHeight)){
                       baseHeight = _thisHeight + parseInt(_thisOffsetTop/bufferRatio); 
                    } else {
                       baseHeight = _thisHeight + parseInt((_windowHeight - _thisHeight)/bufferRatio);
                    }                 
                    break
                    
                case 'parallax_invert':
                    if(_thisOffsetTop < Math.abs(_windowHeight-_thisHeight)){
                       baseHeight = _thisHeight + parseInt((_thisOffsetTop + _thisHeight)/bufferRatio); 
                    } else {
                       baseHeight = _thisHeight + parseInt((_windowHeight + _thisHeight)/bufferRatio);
                    }
                    break
                    
                case 'parallax_fixes':
                    if((_thisOffsetTop + _thisHeight) < _windowHeight){
                        baseHeight = _thisOffsetTop + _thisHeight;
                    } else {
                        baseHeight = _windowHeight;
                    }
                    break
                    
                case 'parallax_none':
                    baseHeight = _thisHeight;
                    break
            }
            
            return baseHeight;
        }
        
        function toRadians (angle) {
            return angle * (Math.PI / 180);
        }
        
        function isIE() {
            if (navigator.userAgent.indexOf('MSIE') !== -1 || navigator.appVersion.indexOf('Trident/') > 0) {
                return true;
            }else{
                return false;
            }
        }
        
        function loadScript(url, callback){
            $.ajax({
                url: url,
                dataType: 'script',
                success: callback,
                async: true
            });
        }       
    }
})(jQuery)
;

document.dispatchEvent(new Event("jasservis:legacy-ready"));
jQuery.holdReady(false);
