(function () {
    'use strict';
    var shared=window.JASSERVIS_BUSINESS_DATA;
    var dialog = document.createElement('dialog');
    dialog.className = 'contact-booking-panel';
    dialog.setAttribute('aria-labelledby', 'contact-booking-title');
    dialog.innerHTML = '<div class="contact-booking-panel__header"><button type="button" class="contact-booking-panel__close" aria-label="Zavřít kontaktní panel">×</button>' +
        '<h2 id="contact-booking-title">Objednání servisu</h2></div><div class="contact-booking-panel__cards">' +
        card('Kancelář a objednání', shared.office.display, shared.office.tel, shared.office.email) +
        card('Servis', shared.workshop.display, shared.workshop.tel, shared.workshop.email) +
        '</div><p class="contact-booking-panel__hours">Po–Pá 9:00–18:00</p>';
    var preparation=document.createElement('p');preparation.className='site-contact-preparation';preparation.textContent=shared.preparation[document.documentElement.lang]||shared.preparation.cs;dialog.appendChild(preparation);
    document.body.appendChild(dialog);
    var opener;
    var scrollState;
    function lockScroll() {
        var body = document.body;
        scrollState = {x: window.scrollX, y: window.scrollY, position: body.style.position, top: body.style.top, left: body.style.left, width: body.style.width, overflow: document.documentElement.style.overflow};
        body.style.position = 'fixed';
        body.style.top = -scrollState.y + 'px';
        body.style.left = -scrollState.x + 'px';
        body.style.width = '100%';
        document.documentElement.style.overflow = 'hidden';
    }
    function unlockScroll() {
        if (!scrollState) return;
        var state = scrollState;
        scrollState = null;
        var body = document.body;
        body.style.position = state.position;
        body.style.top = state.top;
        body.style.left = state.left;
        body.style.width = state.width;
        document.documentElement.style.overflow = state.overflow;
        window.scrollTo(state.x, state.y);
    }
    function fitPanel() {
        var height = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        dialog.style.setProperty('--contact-viewport-height', height + 'px');
    }
    window.addEventListener('resize', fitPanel);
    if (window.visualViewport) window.visualViewport.addEventListener('resize', fitPanel);
    window.addEventListener('pageshow', function (event) {
        if (event.persisted) { if (dialog.open) dialog.close(); unlockScroll(); }
    });
    function card(title, number, phone, email) {
        return '<section class="contact-booking-panel__card kontakt-prehled__karta"><h3>' + title + '</h3>' +
            '<span class="contact-booking-panel__phone" tabindex="0">' + number + '</span>' +
            '<a href="mailto:' + email + '">' + email + '</a>' +
            '<a class="contact-booking-panel__call" href="tel:' + phone + '">Zavolat</a>' +
            '<button class="contact-booking-panel__copy" type="button" data-copy-number="' + number + '">Kopírovat číslo</button>' +
            '<div role="status" aria-live="polite"></div></section>';
    }
    document.addEventListener('click', function (event) {
        var trigger = event.target.closest('[data-booking-panel]');
        if (!trigger || typeof dialog.showModal !== 'function' || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = trigger;
        fitPanel();
        lockScroll();
        dialog.showModal();
    });
    dialog.querySelector('.contact-booking-panel__close').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
        var box = dialog.getBoundingClientRect();
        if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
    });
    // Cycle focus within the modal; Escape still uses the native dialog behavior.
    dialog.addEventListener('keydown', function (event) {
        if (event.key !== 'Tab') return;
        var controls = Array.prototype.filter.call(dialog.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])'), function (node) { return node.getBoundingClientRect().height > 0; });
        if (!controls.length) return;
        var first = controls[0], last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    dialog.addEventListener('close', function () {
        unlockScroll();
        if (opener) opener.focus({preventScroll: true});
    });

    function fallbackCopy(text) {
        var previous = document.activeElement;
        var field = document.createElement('textarea');
        field.value = text;
        field.readOnly = true;
        field.tabIndex = -1;
        field.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;';
        (dialog.open ? dialog : document.body).appendChild(field);
        field.select();
        var copied = false;
        try { copied = document.execCommand('copy'); } catch (error) { /* Report failure below. */ }
        field.remove();
        if (previous) previous.focus();
        return copied;
    }

    Array.prototype.forEach.call(document.querySelectorAll('[data-copy-number]'), function (button) {
        button.hidden = false;
        button.addEventListener('click', async function () {
            var text = button.getAttribute('data-copy-number');
            var status = button.closest('.kontakt-prehled__karta').querySelector('[role="status"]');
            var copied = false;
            status.textContent = '';
            if (navigator.clipboard && window.isSecureContext) {
                try {
                    await navigator.clipboard.writeText(text);
                    copied = true;
                } catch (error) { /* Try the older browser clipboard path. */ }
            }
            if (!copied) copied = fallbackCopy(text);
            status.textContent = copied ? 'Zkopírováno: ' + text : 'Číslo se nepodařilo zkopírovat. Označte je a zkopírujte ručně.';
            if (!copied) {
                var number = button.closest('.kontakt-prehled__karta').querySelector('.contact-booking-panel__phone, .kontakt-prehled__tel');
                if (number) {
                    var selection = window.getSelection();
                    var range = document.createRange();
                    range.selectNodeContents(number);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            }
        });
    });
}());
