(function () {
  'use strict';

  var grid = document.querySelector('#post-203 .home-offered-services .home-service-index');
  if (!grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(':scope > .home-service-group'));
  var mobileQuery = window.matchMedia('(max-width: 767px)');
  var frame = 0;

  function equalizeOpenPairs() {
    cards.forEach(function (card) { card.style.removeProperty('min-height'); });
    if (mobileQuery.matches) return;

    [[0, 1], [2, 3]].forEach(function (indexes) {
      var pair = indexes.map(function (index) { return cards[index]; }).filter(Boolean);
      if (pair.length < 2 || !pair[0].open || !pair[1].open) return;
      var height = Math.max(pair[0].getBoundingClientRect().height, pair[1].getBoundingClientRect().height);
      pair.forEach(function (card) { card.style.minHeight = height + 'px'; });
    });
  }

  function arrange() {
    frame = 0;
    equalizeOpenPairs();
    if (mobileQuery.matches) {
      cards.forEach(function (card) { card.style.removeProperty('grid-row'); });
      return;
    }

    var nextRow = [1, 1];
    cards.forEach(function (card, index) {
      var column = index % 2;
      var span = Math.ceil(card.getBoundingClientRect().height + 12);
      card.style.gridRow = nextRow[column] + ' / span ' + span;
      nextRow[column] += span;
    });
  }

  function schedule() {
    if (frame) cancelAnimationFrame(frame);
    frame = requestAnimationFrame(arrange);
  }

  cards.forEach(function (card) {
    card.addEventListener('toggle', schedule);
  });
  mobileQuery.addEventListener ? mobileQuery.addEventListener('change', schedule) : mobileQuery.addListener(schedule);
  window.addEventListener('resize', schedule, { passive: true });

  if ('ResizeObserver' in window) {
    var observer = new ResizeObserver(schedule);
    cards.forEach(function (card) { observer.observe(card); });
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(schedule);
    if (document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', schedule);
  }

  schedule();
}());
