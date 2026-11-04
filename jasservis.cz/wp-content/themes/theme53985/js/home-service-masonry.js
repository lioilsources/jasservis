/* User-initiated native details enhancement; no timers or animation loop. */
(function () {
  'use strict';
  var grid = document.querySelector('#post-203 .home-service-index');
  if (!grid) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var phone = window.matchMedia('(max-width:767px)');
  var wasPhone = phone.matches;
  var states = [];
  function settle(state, expanded) {
    if (state.animation) {
      state.animation.onfinish = null;
      state.animation.cancel();
      state.animation = null;
    }
    if (!expanded && state.body.contains(document.activeElement)) state.summary.focus({preventScroll:true});
    state.group.open = expanded;
    state.body.inert = !expanded;
    state.body.style.removeProperty('height');
    state.target = expanded;
  }
  Array.prototype.forEach.call(grid.querySelectorAll(':scope > details'), function (group) {
    var summary = group.querySelector('summary');
    var list = group.querySelector('ul');
    if (!summary || !list) return;
    var body = document.createElement('div');
    body.className = 'workshop-panel-body';
    list.parentNode.insertBefore(body, list);
    body.appendChild(list);
    var state = {group:group, summary:summary, body:body, animation:null, target:group.open};
    body.inert = !group.open;
    states.push(state);
    summary.addEventListener('click', function (event) {
      event.preventDefault();
      var expanded = state.animation ? !state.target : !group.open;
      if (reduce.matches || typeof body.animate !== 'function') { settle(state, expanded); return; }
      var from = group.open ? body.getBoundingClientRect().height : 0;
      if (state.animation) {
        state.animation.onfinish = null;
        state.animation.cancel();
      }
      if (!expanded && body.contains(document.activeElement)) summary.focus({preventScroll:true});
      group.open = true;
      body.inert = !expanded;
      body.style.height = 'auto';
      var to = expanded ? body.getBoundingClientRect().height : 0;
      body.style.height = from + 'px';
      state.target = expanded;
      state.animation = body.animate([{height:from + 'px'}, {height:to + 'px'}], {
        duration:220, easing:'cubic-bezier(.2,.7,.2,1)', fill:'both'
      });
      state.animation.onfinish = function () { settle(state, expanded); };
    });
    group.addEventListener('toggle', function () {
      if (!state.animation) body.inert = !group.open;
    });
  });
  function finishMotion() {
    var changed = phone.matches !== wasPhone;
    states.forEach(function (state) {
      if (state.animation) settle(state, state.target);
      if (changed) settle(state, !phone.matches);
    });
    wasPhone = phone.matches;
  }
  window.addEventListener('resize', finishMotion, {passive:true});
  if (reduce.addEventListener) reduce.addEventListener('change', finishMotion);
  else reduce.addListener(finishMotion);
}());
