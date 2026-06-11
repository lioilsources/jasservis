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
            _this.html('');
            _this.addClass(options.animateLayout);
    
            //  preview holder build
            _this.append("<div id='mainImageHolder'></div>");
            mainImageHolder = $('#mainImageHolder');
    
             //  caption holder build
            _this.append("<div id='mainCaptionHolder'><div class='container'></div></div>");
            mainCaptionHolder = $('#mainCaptionHolder');
            mainCaptionHolderContainer = $('>.container', mainCaptionHolder);
    
            //  controls build
            _this.append("<div class='controlBtn parallaxPrevBtn'><div class='innerBtn icon-angle-left'></div><div class='slidesCounter'></div></div><div class='controlBtn parallaxNextBtn'><div class='innerBtn icon-angle-right'></div><div class='slidesCounter'></div></div>");
            parallaxPrevBtn = $('.parallaxPrevBtn', _this);
            parallaxNextBtn = $('.parallaxNextBtn', _this);
    
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
            if(options.autoSwitcher){
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
            
            //--------------- keyboard events ----------------------//
            _window.on("keydown",
                function(eventObject)
                {
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
            }
            
            if(sliderData[currIndex].caption != ''){
                mainCaptionHolderContainer.append('<div class="primaryCaption"></div>');
                primaryCaption = $('> .primaryCaption', mainCaptionHolderContainer);
                primaryCaption.html(sliderData[currIndex].caption);
                objectCssTransition(primaryCaption, 0, 'ease');
                primaryCaption.addClass('animateState');   
            }
            if(sliderData[currIndex].link != '') mainCaptionHolder.append('<a href="'+sliderData[currIndex].link+'"></a>');
            
            slidesCounterList.text((currIndex+1) + '/'+itemLength);
            $(">ul >li", paralaxSliderPagination).removeClass('active').eq(currIndex).addClass('active');
    
            isPreviewLoading = true;
            isPreviewAnimate = true;
            previewSpinner.css({display:'block'}).stop().fadeTo(300, 1);
            
            if(progressBar) progressBar.remove(); 
            
            //------------------------- image slide type ----------------------------// 
            if(sliderData[currIndex].slide_type == 'image')
            {  
                var img = new Image();
                img.src = sliderData[currIndex].image;
                
                img.onload = function ()
                {
                    if(!options.liteMode){ 
                        primaryImageHolder.html('<div class="parallax-slider-img obj-inner"></div>');
                        obj_inner = $('.parallax-slider-img', primaryImageHolder);
                        obj_inner.css('background-image', 'url(' + img.src + ')'); 
                    } else { 
                        primaryImageHolder.html('<img class="parallax-slider-img obj-inner" src="'+img.src+'" alt=""/>');
                        obj_inner = $('.parallax-slider-img', primaryImageHolder);
                    }
                    
                    if(isIE()) obj_inner.css({backgroundAttachment:'fixed'});
                    
                    originalWidth = img.width;
                    originalHeight = img.height;
                    objectResize(obj_inner, primaryImageHolder.width(), _baseHeight);
                
                    onSlideLoaded();
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
                img.src = sliderData[currIndex].image;
                
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
                isPreviewLoading = false;
                previewSpinner.stop().fadeTo(300, 0, function(){ $(this).css({display:'none'}); });
                
                objectCssTransition(primaryImageHolder, options.duration, 'outCubic');
                primaryImageHolder.removeClass('animateState');
                
                if(secondarImageHolder){
                    if(sliderData[prevIndex].slide_type == 'youtube_video' || sliderData[prevIndex].slide_type == 'vimeo_video'){
                        setTimeout(function(){
                            if(sliderData[prevIndex].slide_type == 'youtube_video') sliderData[prevIndex].youtube_video.player.stopVideo();
                            if(sliderData[prevIndex].slide_type == 'vimeo_video') sliderData[prevIndex].vimeo_video.player.api('unload');
                        }, options.duration/1.25)
                    }

                    objectCssTransition(secondarImageHolder, options.duration, 'outCubic');
                    secondarImageHolder.addClass('animateState');
                }
                
                objectCssTransition(primaryCaption, options.duration, 'outCubic');
                if(primaryCaption){
                    
                    primaryCaption.removeClass('animateState');                  
                } 
                
                if(secondaryCaption){
                    objectCssTransition(secondaryCaption, options.duration, 'outCubic');
                    secondaryCaption.addClass('animateState');
                }
                
                setTimeout(function()
                {
                    if(secondarImageHolder) secondarImageHolder.remove();
                    if(secondaryCaption) secondaryCaption.remove();
                    
                    isPreviewAnimate = false;

                }, options.duration )
            }         
        }
    
        //----------------------------------------------------//
        function objectCssTransition(obj, duration, ease)
        {
            if(objectExists(obj))
            {
                var durationValue;
        
                if(duration !== 0){
                    durationValue = duration/1000;
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
             if(parallax || options.scrolling_description && !options.liteMode){
                
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