/* Mobile-only enhancement: reuse existing contacts and restore the original desktop header. */
(function () {
    'use strict';
    var header = document.querySelector('header.header');
    var widget = document.querySelector('#text-8 > .textwidget');
    var address = document.querySelector('#text-7 .textwidget b');
    if (!header || !widget || !address) return;
    var link = widget.querySelector('b > a');
    var phones = widget.querySelector('.tel');
    var hours = phones && phones.querySelector('.header-hours');
    if (!link || !phones || !hours) return;
    var holder = link.parentElement;
    var fullAddress = address.innerHTML;
    var mobile = window.matchMedia('(max-width:767px)');
    var active = false;
    var button = document.createElement('button');
    button.type = 'button';
    button.id = 'mobile-booking-toggle';
    button.className = 'mobile-booking-toggle';
    button.textContent = 'ZAVOLAT A OBJEDNAT SERVIS';
    button.setAttribute('aria-controls', 'mobile-phone-options');
    button.setAttribute('aria-expanded', 'false');

    // iOS Safari scrolled the page so the content under the button landed at the top
    // whenever the list opened or closed; put the page back where the visitor had it.
    function keepScroll(by) {
        var y = window.pageYOffset + (by || 0);
        requestAnimationFrame(function () {
            if (Math.abs(window.pageYOffset - y) > 1) window.scrollTo(0, y);
        });
    }
    function close(returnFocus) {
        if (!active) return;
        if (!phones.hidden) keepScroll();
        phones.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        if (returnFocus) button.focus();
    }
    function sync() {
        if (mobile.matches === active) return;
        if (mobile.matches) {
            active = true;
            holder.replaceChild(button, link);
            widget.appendChild(hours);
            phones.id = 'mobile-phone-options';
            phones.classList.add('mobile-phone-options');
            phones.setAttribute('role', 'group');
            phones.setAttribute('aria-labelledby', button.id);
            address.textContent = 'Statenice – Černý Vůl';
            header.classList.add('mobile-contact-ready');
            close(false);
        } else {
            active = false;
            phones.hidden = false;
            phones.classList.remove('mobile-phone-options');
            phones.removeAttribute('id');
            phones.removeAttribute('role');
            phones.removeAttribute('aria-labelledby');
            phones.appendChild(hours);
            holder.replaceChild(link, button);
            address.innerHTML = fullAddress;
            header.classList.remove('mobile-contact-ready');
            button.setAttribute('aria-expanded', 'false');
        }
    }
    button.addEventListener('click', function () {
        var y = window.pageYOffset, by = 0;
        phones.hidden = !phones.hidden;
        button.setAttribute('aria-expanded', String(!phones.hidden));
        // Keep both choices visible above an undecided cookie banner on short screens.
        var banner = document.getElementById('cf-cookie-banner');
        if (!phones.hidden && banner && !banner.hidden && window.getComputedStyle(banner).position === 'fixed') {
            var overlap = phones.getBoundingClientRect().bottom - banner.getBoundingClientRect().top;
            if (overlap > 0) by = overlap + 12;
        }
        window.scrollTo(0, y);
        keepScroll(by);
    });
    phones.addEventListener('click', function (event) {
        if (active && event.target.closest('a[href^="tel:"]')) close(true);
    });
    document.addEventListener('click', function (event) {
        if (active && !holder.contains(event.target) && !phones.contains(event.target)) close(false);
    });
    document.addEventListener('keydown', function (event) {
        if (active && !phones.hidden && event.key === 'Escape') {
            event.preventDefault();
            close(true);
        }
    });
    if (mobile.addEventListener) mobile.addEventListener('change', sync);
    else mobile.addListener(sync);
    sync();
}());
