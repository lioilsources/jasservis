/* Progressive enhancement starts after an actual content paint, not a fixed delay. */
(function () {
 'use strict';
 var source = document.currentScript.getAttribute('data-runtime-src');
 var widgetsSource = document.currentScript.getAttribute('data-widgets-src');
 var image = document.querySelector('[data-home-intro-image]') || document.querySelector('#mainImageHolder img');
 var started = false, observer;
 function enhance() {
  if (started) return;
  started = true;
  if (observer) observer.disconnect();
  var styles = [];
  var placeholders = Array.prototype.slice.call(document.querySelectorAll('template[data-home-full-css]'));
  var stylesReady = Promise.all(placeholders.map(function (placeholder) {
   return new Promise(function (resolve) {
    var link = document.createElement('link');
    styles.push(link);
    link.onload = resolve; link.onerror = resolve;
    link.media = 'print'; link.rel = 'stylesheet';
    link.href = placeholder.getAttribute('data-home-full-css');
    placeholder.parentNode.replaceChild(link, placeholder);
   });
  })).then(function () {
   return new Promise(function (resolve) {
    requestAnimationFrame(function () {
     styles.forEach(function (link) { link.media = 'all'; });
     resolve();
    });
   });
  });
  var script = document.createElement('script');
  script.src = source; script.async = true;
  function followups() {
   document.querySelectorAll('script[data-home-followup]').forEach(function (original) {
    var followup = document.createElement('script');
    followup.src = original.getAttribute('data-home-followup');
    document.head.appendChild(followup);
   });
  }
  script.onload = function () {
   stylesReady.then(function () {
    var widgets = document.createElement('script');
    widgets.src = widgetsSource;
    widgets.onload = followups;
    document.head.appendChild(widgets);
   });
  };
  document.head.appendChild(script);
 }
 function schedule() {
  var decoded = image && image.decode ? image.decode() : Promise.resolve();
  decoded.catch(function () {}).then(function () {
   requestAnimationFrame(function () { requestAnimationFrame(enhance); });
  });
 }
 function ready() {
  if (window.PerformanceObserver && PerformanceObserver.supportedEntryTypes.indexOf('paint') !== -1) {
   observer = new PerformanceObserver(function (list) {
    if (list.getEntries().some(function (entry) { return entry.name === 'first-contentful-paint'; })) schedule();
   });
   observer.observe({type:'paint',buffered:true});
  } else { requestAnimationFrame(function () { requestAnimationFrame(enhance); }); }
 }
 if (!image || image.complete) ready();
 else { image.addEventListener('load',ready,{once:true}); image.addEventListener('error',ready,{once:true}); }
}());
