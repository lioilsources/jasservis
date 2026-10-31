(function () {
    'use strict';
    var banner = document.getElementById('cf-cookie-banner');
    if (!banner) return;
    var settings = document.getElementById('cookie-settings');
    var details = document.getElementById('cookie-details');
    var maps = document.getElementById('cookie-maps');
    var social = document.getElementById('cookie-social');
    var frames = document.querySelectorAll('iframe[data-cookie-src]');
    var choice = null;
    var returnFocus = null;
    // The legacy value "1" only dismissed an announcement; it is not consent.
    try {
        var saved = document.cookie.match(/(?:^|;\s*)cf-cookie-banner=v2-([01])([01])(?:;|$)/);
        if (saved) choice = {maps:saved[1] === '1', social:saved[2] === '1'};
    } catch (error) { /* Keep optional services off when cookies are unavailable. */ }

    function reserveSpace() {
        var height = banner.hidden ? 0 : banner.getBoundingClientRect().height;
        if (document.body.style.getPropertyValue('--cookie-space') !== height + 'px') {
            document.body.style.setProperty('--cookie-space', height + 'px');
            window.dispatchEvent(new Event('resize'));
        }
    }
    function showSettings() {
        returnFocus = document.activeElement;
        banner.hidden = false;
        settings.hidden = true;
        details.open = true;
        reserveSpace();
        details.querySelector('summary').focus();
    }
    Array.prototype.forEach.call(frames, function (frame) {
        var placeholder = document.createElement('div');
        placeholder.className = 'cookie-embed-placeholder';
        var button = document.createElement('button');
        button.type = 'button';
        button.textContent = frame.getAttribute('data-cookie-category') === 'maps' ? 'Налаштувати згоду для Google Maps' : 'Налаштувати згоду для Facebook';
        button.setAttribute('aria-label', button.textContent);
        button.addEventListener('click', showSettings);
        placeholder.appendChild(button);
        frame.parentNode.insertBefore(placeholder, frame);
        frame.cookiePlaceholder = placeholder;
    });
    function applyChoice() {
        maps.checked = !!(choice && choice.maps);
        social.checked = !!(choice && choice.social);
        Array.prototype.forEach.call(frames, function (frame) {
            var allowed = !!(choice && choice[frame.getAttribute('data-cookie-category')]);
            frame.hidden = !allowed;
            frame.cookiePlaceholder.hidden = allowed;
            if (allowed) {
                if (!frame.hasAttribute('src')) frame.setAttribute('src', frame.getAttribute('data-cookie-src'));
            } else {
                // Unload an already open third-party document when consent is revoked.
                frame.removeAttribute('src');
            }
        });
    }
    Array.prototype.forEach.call(banner.querySelectorAll('[data-cookie-choice]'), function (button) {
        button.hidden = false;
        button.addEventListener('click', function () {
            var action = button.getAttribute('data-cookie-choice');
            choice = action === 'save' ? {maps:maps.checked, social:social.checked} : {maps:action === 'accept', social:action === 'accept'};
            try {
                document.cookie = 'cf-cookie-banner=v2-' + Number(choice.maps) + Number(choice.social) + '; Max-Age=31536000; Path=/; SameSite=Lax' + (window.location.protocol === 'https:' ? '; Secure' : '');
            } catch (error) { /* The current page still respects the choice. */ }
            applyChoice();
            banner.hidden = true;
            settings.hidden = false;
            reserveSpace();
            if (returnFocus && document.contains(returnFocus) && !returnFocus.closest('[hidden]')) returnFocus.focus();
            else settings.focus();
        });
    });
    settings.addEventListener('click', showSettings);
    banner.classList.add('cookie-ready');
    banner.hidden = !!choice;
    settings.hidden = !choice;
    applyChoice();
    details.addEventListener('toggle', reserveSpace);
    if (window.ResizeObserver) {
        var observer = new ResizeObserver(reserveSpace);
        observer.observe(banner);
        observer.observe(settings);
    }
    reserveSpace();
}());
