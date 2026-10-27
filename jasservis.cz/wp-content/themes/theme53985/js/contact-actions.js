(function () {
    'use strict';
    var dialog = document.createElement('dialog');
    dialog.className = 'contact-booking-panel';
    dialog.setAttribute('aria-labelledby', 'contact-booking-title');
    dialog.innerHTML = '<button type="button" class="contact-booking-panel__close" aria-label="Zavřít kontaktní panel">×</button>' +
        '<h2 id="contact-booking-title">Objednání servisu</h2><div class="contact-booking-panel__cards">' +
        card('Kancelář a objednání', '+420 605 399 448', '+420605399448', 'admin@jasservis.cz') +
        card('Servis', '+420 608 313 437', '+420608313437', 'j.mateju@jasservis.cz') +
        '</div><p class="contact-booking-panel__hours">Po–Pá 9:00–18:00</p>';
    document.body.appendChild(dialog);
    var opener;
    function card(title, number, phone, email) {
        return '<section class="contact-booking-panel__card kontakt-prehled__karta"><h3>' + title + '</h3>' +
            '<a class="contact-booking-panel__phone" href="tel:' + phone + '">' + number + '</a>' +
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
        dialog.showModal();
    });
    dialog.querySelector('.contact-booking-panel__close').addEventListener('click', function () { dialog.close(); });
    dialog.addEventListener('click', function (event) {
        var box = dialog.getBoundingClientRect();
        if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
    });
    dialog.addEventListener('close', function () { if (opener) opener.focus(); });

    function fallbackCopy(text) {
        var previous = document.activeElement;
        var field = document.createElement('textarea');
        field.value = text;
        field.readOnly = true;
        field.tabIndex = -1;
        field.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;';
        document.body.appendChild(field);
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
            if (navigator.clipboard && window.isSecureContext) {
                try {
                    await navigator.clipboard.writeText(text);
                    copied = true;
                } catch (error) { /* Try the older browser clipboard path. */ }
            }
            if (!copied) copied = fallbackCopy(text);
            status.textContent = copied ? 'Číslo bylo zkopírováno: ' + text : 'Číslo se nepodařilo zkopírovat. Označte je a zkopírujte ručně.';
        });
    });
}());
