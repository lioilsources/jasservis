/* Live review summaries; no rating values or access credentials are stored here. */
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
    var google = panel.querySelector('a[href*="g.page/"]');
    var googleLoaded = false;
    var googleBusy = false;
    var googleTime = 0;
    var googleHref = google && google.href;
    var lang = (document.documentElement.lang || 'cs').split('-')[0];
    var words = {
        cs:['Hodnocení Google','recenzí','Aktualizováno'],
        en:['Google rating','reviews','Updated'],
        de:['Google-Bewertung','Rezensionen','Aktualisiert'],
        uk:['Рейтинг Google','відгуків','Оновлено'],
        vi:['Đánh giá Google','lượt đánh giá','Cập nhật']
    }[lang] || ['Google rating','reviews','Updated'];
    function loadGoogle() {
        if (googleLoaded && Date.now() - googleTime > 172800000) {
            var expired = google.querySelector('.google-review-rating');
            if (expired) expired.remove();
            google.href = googleHref;
            googleLoaded = false;
        }
        if (!google || googleLoaded || googleBusy || !window.fetch) return;
        googleBusy = true;
        var controller = window.AbortController ? new AbortController() : null;
        var timeout = controller ? window.setTimeout(function () {controller.abort();}, 8000) : null;
        var options = {credentials:'omit',cache:'no-store'};
        if (controller) options.signal = controller.signal;
        fetch('https://jasservis-google-hodnoceni.sleek-bass-5878.chatgpt.site/rating.json', options)
            .then(function (response) {if (!response.ok) throw new Error('Unavailable'); return response.json();})
            .then(function (data) {
                var age = Date.now() - Date.parse(data.updatedAt);
                if (data.source !== 'Google' || typeof data.rating !== 'number' || !isFinite(data.rating) ||
                    data.rating < 1 || data.rating > 5 || !Number.isSafeInteger(data.count) || data.count < 1 ||
                    !isFinite(age) || age < -300000 || age > 172800000 ||
                    data.profileUrl !== 'https://maps.google.com/maps?cid=14113684367371719453') throw new Error('Invalid summary');
                var number = new Intl.NumberFormat(lang, {minimumFractionDigits:1,maximumFractionDigits:1}).format(data.rating);
                var count = new Intl.NumberFormat(lang).format(data.count);
                var card = document.createElement('span');
                card.className = 'google-review-rating';
                card.setAttribute('role','img');
                card.setAttribute('aria-label',words[0] + ': ' + number + ' / 5, ' + count + ' ' + words[1]);
                var line = document.createElement('span');
                line.className = 'google-review-rating-line';
                var value = document.createElement('strong');
                value.textContent = number + ' / 5';
                var stars = document.createElement('span');
                stars.className = 'google-review-stars';
                stars.setAttribute('aria-hidden','true');
                stars.textContent = '★★★★★';
                var filled = document.createElement('span');
                filled.textContent = '★★★★★';
                filled.style.width = (data.rating / 5 * 100) + '%';
                stars.appendChild(filled);
                line.appendChild(value); line.appendChild(stars); card.appendChild(line);
                var reviews = document.createElement('span');
                reviews.className = 'google-review-count';
                reviews.textContent = count + ' ' + words[1];
                card.appendChild(reviews);
                var updated = document.createElement('span');
                updated.className = 'google-review-updated';
                updated.textContent = words[2] + ' ' + new Intl.DateTimeFormat(lang,{dateStyle:'short',timeZone:'Europe/Prague'}).format(new Date(data.updatedAt));
                card.appendChild(updated);
                google.classList.add('reviews-rating-link');
                google.href = data.profileUrl;
                google.appendChild(card);
                google.setAttribute('data-rating-state','ready');
                googleTime = Date.parse(data.updatedAt);
                googleLoaded = true;
            }).catch(function () {google.setAttribute('data-rating-state','unavailable');})
            .then(function () {googleBusy = false; if (timeout) window.clearTimeout(timeout);});
    }
    function loadBadge() {
        if (panel.hidden) return;
        loadGoogle();
        if (badge.hasAttribute('src')) return;
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
