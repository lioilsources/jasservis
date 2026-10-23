(function () {
    'use strict';
    var menu = document.getElementById('topnav');
    if (!menu) return;
    var nav = menu.parentElement;
    var compact = window.matchMedia('(max-width:1199px)');
    var controls = [];
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'navigation-toggle';
    toggle.innerHTML = '<span class="mobile-menu-icon" aria-hidden="true"><span></span><span></span><span></span></span><span class="mobile-menu-label">MENU</span>';
    function syncToggle() {
        toggle.setAttribute('aria-expanded', String(!menu.hidden));
        toggle.querySelector('.mobile-menu-label').textContent = menu.hidden ? 'MENU' : 'ZAVŘÍT MENU';
    }
    toggle.setAttribute('aria-controls', menu.id);
    nav.insertBefore(toggle, menu);

    function fit(panel) {
        if (!compact.matches && !panel.hidden) {
            var bottom = window.innerHeight;
            var banner = document.getElementById('cf-cookie-banner');
            if (banner && window.getComputedStyle(banner).position === 'fixed') {
                var rect = banner.getBoundingClientRect();
                if (rect.height > 0 && rect.top >= 0 && rect.top < bottom) bottom = rect.top;
            }
            panel.style.maxHeight = Math.max(0, bottom - panel.getBoundingClientRect().top - 16) + 'px';
        }
    }
    function close(control) {
        window.clearTimeout(control.leaveTimer);
        control.button.setAttribute('aria-expanded', 'false');
        control.panel.hidden = true;
    }
    function open(control) {
        controls.forEach(function (other) {
            if (other !== control) close(other);
        });
        window.clearTimeout(control.leaveTimer);
        control.panel.hidden = false;
        control.button.setAttribute('aria-expanded', 'true');
        fit(control.panel);
    }
    Array.prototype.forEach.call(menu.querySelectorAll('.current-menu-item > a'), function (link) {
        link.setAttribute('aria-current', 'page');
    });
    Array.prototype.forEach.call(menu.children, function (item) {
        var panel = item.querySelector('.sub-menu');
        if (!panel) return;
        var link = item.querySelector('.reviews-toggle') || item.querySelector('a');
        var button = item.querySelector('.reviews-toggle');
        if (!button) {
            button = document.createElement('button');
            button.type = 'button';
            button.className = 'submenu-toggle';
            button.textContent = '⌄';
            item.insertBefore(button, panel);
        }
        button.setAttribute('aria-label', 'Rozbalit nabídku: ' + link.textContent.replace(/\s*⌄\s*$/, ''));
        panel.id = item.id + '-submenu';
        button.setAttribute('aria-controls', panel.id);
        var control = {button: button, panel: panel, leaveTimer: null};
        controls.push(control);
        close(control);
        function toggle() {
            if (panel.hidden) open(control);
            else close(control);
        }
        button.addEventListener('click', toggle);
        if (link !== button) {
            // On a phone every item with a submenu only unfolds, and the page itself
            // is the first entry of the submenu; the desktop label still opens the page.
            var overview = document.createElement('li');
            overview.className = 'menu-overview';
            var overviewLink = document.createElement('a');
            overviewLink.href = link.getAttribute('href');
            overviewLink.textContent = 'Přehled – ' + link.textContent.trim() + ' →';
            overview.appendChild(overviewLink);
            panel.insertBefore(overview, panel.firstChild);
            link.addEventListener('click', function (event) {
                if (!compact.matches) return;
                event.preventDefault();
                toggle();
            });
        }
        item.addEventListener('pointerenter', function (event) {
            // Entering the arrow must leave its first click free to open the panel.
            // Entering the label still opens the desktop menu on hover.
            var pointed = document.elementFromPoint(event.clientX, event.clientY);
            if (event.pointerType === 'mouse' && !compact.matches && !item.querySelector('.reviews-toggle') &&
                !(pointed && button.contains(pointed))) open(control);
        });
        item.addEventListener('pointerleave', function (event) {
            if (event.pointerType !== 'mouse' || compact.matches) return;
            control.leaveTimer = window.setTimeout(function () {
                if (!item.contains(document.activeElement)) close(control);
            }, 200);
        });
        item.addEventListener('focusout', function (event) {
            // In the mobile list, closing on blur moves the next button before its click.
            // The next category closes this panel atomically in open().
            if (!compact.matches && !item.contains(event.relatedTarget)) close(control);
        });
        item.addEventListener('keydown', function (event) {
            if (event.key !== 'ArrowDown' || (event.target !== link && event.target !== button)) return;
            event.preventDefault();
            open(control);
            var first = panel.querySelector('a, button');
            if (first) first.focus();
        });
    });
    function reset() {
        controls.forEach(close);
        menu.hidden = compact.matches;
        syncToggle();
    }
    toggle.addEventListener('click', function () {
        menu.hidden = !menu.hidden;
        syncToggle();
        if (menu.hidden) controls.forEach(close);
    });
    document.addEventListener('click', function (event) {
        if (!nav.contains(event.target)) {
            controls.forEach(close);
            if (compact.matches) {
                menu.hidden = true;
                syncToggle();
            }
        }
    });
    nav.addEventListener('focusout', function (event) {
        if (!nav.contains(event.relatedTarget)) controls.forEach(close);
    });
    nav.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var open = controls.filter(function (control) { return !control.panel.hidden; })[0];
        if (open) { close(open); open.button.focus(); }
        else if (compact.matches && !menu.hidden) { menu.hidden = true; syncToggle(); toggle.focus(); }
    });
    window.addEventListener('resize', function () { controls.forEach(function (control) { fit(control.panel); }); });
    window.addEventListener('scroll', function () { controls.forEach(function (control) { fit(control.panel); }); }, {passive:true});
    if (compact.addEventListener) compact.addEventListener('change', reset);
    else compact.addListener(reset);
    nav.classList.add('navigation-ready');
    reset();
}());
