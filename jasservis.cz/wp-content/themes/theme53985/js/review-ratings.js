/* Live, provider-generated rating badge; no rating values are stored here. */
(function () {
    'use strict';
    var item = document.getElementById('menu-item-recenze');
    var panel = item && item.querySelector('.sub-menu');
    var button = item && item.querySelector('.reviews-toggle');
    var link = panel && panel.querySelector('a[href*="firmy.cz/detail/12996882-"]');
    if (!link || !button || panel.querySelector('.reviews-rating-badge')) return;
    panel.classList.add('js-review-ratings');
    link.classList.add('reviews-rating-link');
    link.href = 'https://www.firmy.cz/detail/12996882-j-s-servis-jaroslav-mateju-statenice.html#hodnoceni';
    var label = document.createElement('span');
    label.className = 'reviews-rating-label';
    label.textContent = link.textContent.trim();
    link.textContent = '';
    link.appendChild(label);
    var badge = document.createElement('img');
    badge.className = 'reviews-rating-badge';
    badge.alt = 'J&S servis – Jaroslav Matějů na Firmy.cz';
    badge.width = 249;
    badge.height = 56;
    badge.decoding = 'async';
    badge.addEventListener('load', function () {
        link.setAttribute('data-rating-state', 'ready');
    });
    badge.addEventListener('error', function () {
        badge.hidden = true;
        link.setAttribute('data-rating-state', 'unavailable');
    });
    link.appendChild(badge);
    function loadBadge() {
        if (panel.hidden || badge.hasAttribute('src')) return;
        link.setAttribute('data-rating-state', 'loading');
        badge.src = 'https://www.firmy.cz/img-stars/light-12996882.svg';
    }
    // The existing navigation owns opening, closing, focus and keyboard handling.
    // Observe its state so click, keyboard and desktop hover share one request.
    if (window.MutationObserver) {
        new MutationObserver(loadBadge).observe(panel, {attributes:true, attributeFilter:['hidden']});
    }
    button.addEventListener('click', loadBadge);
    loadBadge();
}());
