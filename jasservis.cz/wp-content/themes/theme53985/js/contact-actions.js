(function () {
    'use strict';
    var contacts = document.querySelector('.kontakt-prehled');
    if (!contacts) return;

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

    Array.prototype.forEach.call(contacts.querySelectorAll('[data-copy-number]'), function (button) {
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
