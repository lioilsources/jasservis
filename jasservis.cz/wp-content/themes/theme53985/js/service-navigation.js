(function () {
    'use strict';
    var menu = document.getElementById('topnav');
    if (!menu) return;
    var nav = menu.parentElement;
    var compact = window.matchMedia('(max-width:1199px)');
    var tablet = window.matchMedia('(min-width:768px) and (max-width:1199px) and (min-height:501px)');
    var canHover = window.matchMedia('(hover:hover) and (pointer:fine)');
    var controls = [];
    var arrangingHeader = false;
    function isCompactMenu() { return (compact.matches || tablet.matches) && !nav.classList.contains('short-header-full-nav'); }
    // The rendered upper menu is the shared service list. Keep the static home
    // overview as a no-JavaScript fallback, and refresh it from that list here.
    var offered = document.querySelector('.home-service-index');
    if (offered) {
        Array.prototype.forEach.call(offered.querySelectorAll('[data-service-links]'), function (target) {
            var list = target.querySelector('ul');
            Array.prototype.forEach.call(target.getAttribute('data-service-links').split(' '), function (path, index) {
                var link = menu.querySelector('a[href="' + path + '"]');
                if (!link) return; // Retain the corresponding static fallback if a source link is absent.
                var item = document.createElement('li');
                var copy = document.createElement('a');
                copy.setAttribute('href', link.getAttribute('href'));
                copy.textContent = link.textContent;
                item.appendChild(copy);
                list.replaceChild(item, list.children[index]);
            });
        });
        var phoneOverview = window.matchMedia('(max-width:767px)');
        function resetOfferedGroups() {
            Array.prototype.forEach.call(offered.querySelectorAll('details'), function (group) {
                group.open = !phoneOverview.matches;
            });
        }
        resetOfferedGroups();
        if (phoneOverview.addEventListener) phoneOverview.addEventListener('change', resetOfferedGroups);
        else phoneOverview.addListener(resetOfferedGroups);
    }
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

    function close(control) {
        window.clearTimeout(control.leaveTimer);
        control.hoverOpened = false;
        control.button.setAttribute('aria-expanded', 'false');
        control.button.setAttribute('aria-label', 'Rozbalit nabídku: ' + control.label);
        control.item.classList.remove('is-open');
        control.panel.hidden = true;
    }
    function fitDropdown(control) {
        if (isCompactMenu()) {
            control.panel.style.removeProperty('--menu-available');
            control.item.style.removeProperty('--service-menu-offset');
            return;
        }
        if (control.panel.classList.contains('service-groups')) {
            var header = nav.closest('header');
            var offset = header ? Math.max(0, header.getBoundingClientRect().bottom - control.item.getBoundingClientRect().bottom) : 0;
            control.item.style.setProperty('--service-menu-offset', Math.ceil(offset) + 'px');
        }
        var viewport = window.visualViewport;
        var bottom = viewport ? viewport.offsetTop + viewport.height : window.innerHeight;
        var banner = document.getElementById('cf-cookie-banner');
        if (banner && !banner.hidden) {
            var bannerBounds = banner.getBoundingClientRect();
            if (bannerBounds.height > 0) bottom = Math.min(bottom, bannerBounds.top);
        }
        var height = bottom - control.panel.getBoundingClientRect().top - 12;
        control.panel.style.setProperty('--menu-available', Math.max(44, Math.floor(height)) + 'px');
    }
    function open(control) {
        controls.forEach(function (other) {
            if (other !== control) close(other);
        });
        window.clearTimeout(control.leaveTimer);
        control.panel.hidden = false;
        control.button.setAttribute('aria-expanded', 'true');
        control.button.setAttribute('aria-label', 'Zavřít nabídku: ' + control.label);
        control.item.classList.add('is-open');
        fitDropdown(control);
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
        var control = {item: item, button: button, panel: panel, label: link.textContent.replace(/\s*⌄\s*$/, '').trim(), leaveTimer: null};
        controls.push(control);
        close(control);
        function toggle() {
            if (panel.hidden) open(control);
            else close(control);
        }
        button.addEventListener('click', function () {
            // Recenze is one tile that hover already opened; the click that follows keeps it open.
            if (control.hoverOpened && !panel.hidden) { control.hoverOpened = false; return; }
            toggle();
        });
        if (link !== button) {
            // A label is always a page link; the separate arrow controls its submenu.
            var overview = document.createElement('li');
            overview.className = 'menu-overview';
            var overviewLink = document.createElement('a');
            overviewLink.href = link.getAttribute('href');
            overviewLink.textContent = 'Přehled – ' + link.textContent.trim() + ' →';
            overview.appendChild(overviewLink);
            panel.insertBefore(overview, panel.firstChild);
        }
        item.addEventListener('pointerenter', function (event) {
            // Entering the arrow must leave its first click free to open the panel.
            // Entering the label (or the whole Recenze tile) opens the desktop menu on hover.
            var pointed = document.elementFromPoint(event.clientX, event.clientY);
            if (!canHover.matches || event.pointerType !== 'mouse' || isCompactMenu()) return;
            if (link === button) { if (panel.hidden) { open(control); control.hoverOpened = true; } }
            else if (!(pointed && button.contains(pointed))) open(control);
        });
        item.addEventListener('pointerleave', function (event) {
            if (!canHover.matches || event.pointerType !== 'mouse' || isCompactMenu()) return;
            control.leaveTimer = window.setTimeout(function () {
                if (!item.contains(document.activeElement)) close(control);
            }, 200);
        });
        item.addEventListener('focusout', function (event) {
            if (arrangingHeader) return;
            // In the mobile list, closing on blur moves the next button before its click.
            // The next category closes this panel atomically in open().
            if (!isCompactMenu() && !item.contains(event.relatedTarget)) close(control);
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
        menu.hidden = isCompactMenu();
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
            if (isCompactMenu()) {
                menu.hidden = true;
                syncToggle();
            }
        }
    });
    nav.addEventListener('focusout', function (event) {
        if (arrangingHeader) return;
        if (!nav.contains(event.relatedTarget)) controls.forEach(close);
    });
    nav.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var open = controls.filter(function (control) { return !control.panel.hidden; })[0];
        if (open) { close(open); open.button.focus(); }
        else if (isCompactMenu() && !menu.hidden) { menu.hidden = true; syncToggle(); toggle.focus(); }
    });
    function onNavigationBreakpoint() {
        if (!tablet.matches && !shortLandscape.matches) reset();
        arrangeShortHeader();
    }
    if (compact.addEventListener) compact.addEventListener('change', onNavigationBreakpoint);
    else compact.addListener(onNavigationBreakpoint);
    function fitOpenDropdowns() {
        controls.forEach(function (control) {
            if (!control.panel.hidden) fitDropdown(control);
        });
    }
    window.addEventListener('resize', fitOpenDropdowns);
    window.addEventListener('scroll', fitOpenDropdowns, {passive:true});
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', fitOpenDropdowns);
        window.visualViewport.addEventListener('scroll', fitOpenDropdowns, {passive:true});
    }
    // Landscape uses a contact strip above a brand/navigation strip.
    // Move the original logo and controls, never copies of links or menu state.
    var shortLandscape = window.matchMedia('(max-width:1199px) and (max-height:500px) and (orientation:landscape)');
    var logo = document.querySelector('.header .logo');
    var logoHome = document.createComment('logo original position');
    var landscapeRow;
    if (logo) logo.parentNode.insertBefore(logoHome, logo);
    function arrangeShortHeader() {
        if (!logo) return;
        arrangingHeader = true;
        var focused = document.activeElement;
        var moved = false;
        var wasFull = nav.classList.contains('short-header-full-nav');
        var wasHidden = menu.hidden;
        if (shortLandscape.matches && !landscapeRow) {
            landscapeRow = document.createElement('div');
            landscapeRow.className = 'landscape-nav-row';
            nav.insertBefore(landscapeRow, menu);
            landscapeRow.appendChild(logo);
            landscapeRow.appendChild(toggle);
            moved = true;
        } else if (!shortLandscape.matches && landscapeRow) {
            logoHome.parentNode.insertBefore(logo, logoHome.nextSibling);
            if (menu.parentElement === landscapeRow) nav.insertBefore(menu, landscapeRow.nextSibling);
            nav.insertBefore(toggle, menu);
            landscapeRow.remove();
            landscapeRow = null;
            moved = true;
        }
        nav.classList.toggle('tablet-navigation', tablet.matches);
        if (shortLandscape.matches || tablet.matches) {
            // Measure actual labels and original touch areas, rather than device names.
            nav.classList.add('measuring-short-nav');
            menu.hidden = false;
            var needed = menu.getBoundingClientRect().width;
            var available = shortLandscape.matches ? landscapeRow.clientWidth - logo.getBoundingClientRect().width - 16 : nav.clientWidth;
            nav.classList.remove('measuring-short-nav');
            var fits = needed <= available;
            nav.classList.toggle('short-header-full-nav', fits);
            if (shortLandscape.matches && fits && menu.parentElement !== landscapeRow) {
                landscapeRow.appendChild(menu);
                moved = true;
            } else if (landscapeRow && !fits && menu.parentElement === landscapeRow) {
                nav.insertBefore(menu, landscapeRow.nextSibling);
                moved = true;
            }
            menu.hidden = fits ? false : (wasFull ? controls.every(function (control) { return control.panel.hidden; }) : wasHidden);
        } else {
            nav.classList.remove('short-header-full-nav');
            if (!compact.matches) menu.hidden = false;
            else if (wasFull) menu.hidden = controls.every(function (control) { return control.panel.hidden; });
        }
        if (menu.hidden) controls.forEach(close);
        syncToggle();
        fitOpenDropdowns();
        var restoreFocus = moved || document.activeElement !== focused;
        if (restoreFocus && focused === toggle && !isCompactMenu()) menu.querySelector('a, button').focus({preventScroll: true});
        else if (restoreFocus && focused && focused.isConnected && (focused === toggle || logo.contains(focused) || (!menu.hidden && menu.contains(focused)))) focused.focus({preventScroll: true});
        arrangingHeader = false;
    }
    if (tablet.addEventListener) tablet.addEventListener('change', arrangeShortHeader);
    else tablet.addListener(arrangeShortHeader);
    if (shortLandscape.addEventListener) shortLandscape.addEventListener('change', arrangeShortHeader);
    else shortLandscape.addListener(arrangeShortHeader);
    window.addEventListener('resize', arrangeShortHeader);
    if (window.visualViewport) window.visualViewport.addEventListener('resize', arrangeShortHeader);
    window.addEventListener('orientationchange', function () { window.requestAnimationFrame(arrangeShortHeader); });
    // Safari may restore an expanded menu from the back/forward cache.
    window.addEventListener('pageshow', function (event) { if (event.persisted) { reset(); arrangeShortHeader(); } });
    nav.classList.add('navigation-ready');
    reset();
    arrangeShortHeader();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(arrangeShortHeader);
}());
